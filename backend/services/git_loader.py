import os
import json
import shutil
import tempfile
from core.logging_config import logger
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ──────────────────────────────────────────────────────────────────────
# Supported file type configuration
# ──────────────────────────────────────────────────────────────────────

# Source code files → processed by LanguageParser (understands classes, functions)
CODE_SUFFIXES = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".rb", ".go", ".php", ".mjs"]

# Text/documentation files → read as plain text
TEXT_SUFFIXES = [".md", ".txt", ".rst", ".html", ".css", ".sh", ".bat", ".ps1"]

# Configuration/data files → read as plain text
CONFIG_SUFFIXES = [".json", ".yml", ".yaml", ".toml", ".ini", ".cfg",
                   ".env.example", ".sql"]

# Special files without extension that we want to include
SPECIAL_FILES = {"Dockerfile", "Makefile", "Procfile", "Gemfile",
                 ".gitignore", ".dockerignore"}

# Files/directories to always ignore
IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
               ".tox", ".mypy_cache", ".pytest_cache", "dist", "build"}

# Generated/lock files to always ignore (large and not useful for analysis)
IGNORE_FILES = {"package-lock.json", "yarn.lock", "poetry.lock",
                "Pipfile.lock", "composer.lock", "pnpm-lock.yaml",
                ".DS_Store"}

# Maximum file size to read (bytes) — prevents loading huge generated files
MAX_FILE_SIZE = 50_000  # ~50KB


class GitLoaderService:
    """
    GitHub ingestion utility.
    Responsible for cloning public repositories and preparing code for RAG.

    Supports multiple file types:
    - Source code (.py, .js, .ts, etc.) → LanguageParser
    - Notebooks (.ipynb) → extracts code and markdown cells
    - Documentation (.md, .txt) → plain text
    - Configuration (.json, .yml, .sql, Dockerfile) → plain text

    The clone is temporary: it is automatically deleted after processing.
    """

    def fetch_and_process(self, repo_url: str) -> list[Document]:
        """
        Clones the repository into a temporary directory, processes it,
        and returns the chunks ready for embedding.

        The clone is automatically deleted when finished (or on error).
        """
        # Validate GitHub URL
        if not repo_url.startswith(("https://github.com/", "git@github.com:")):
            raise ValueError("Only public GitHub repositories are supported")

        target_dir = tempfile.mkdtemp(prefix="repo_clone_")

        try:
            # 1. Clone the repository
            try:
                Repo.clone_from(repo_url, target_dir)
            except Exception as e:
                raise Exception(f"Error cloning repository: {str(e)}")

            # 2. Load files by type
            all_documents = []

            # 2a. Source code → LanguageParser (understands code structure)
            code_docs = self._load_code_files(target_dir)
            all_documents.extend(code_docs)
            logger.info(f"Source code: {len(code_docs)} documents loaded")

            # 2b. Notebooks .ipynb → extract cells
            notebook_docs = self._load_notebooks(target_dir)
            all_documents.extend(notebook_docs)
            logger.info(f"Notebooks: {len(notebook_docs)} documents loaded")

            # 2c. Text, configuration and special files → plain text
            text_docs = self._load_text_files(target_dir)
            all_documents.extend(text_docs)
            logger.info(f"Text/config: {len(text_docs)} documents loaded")

            if not all_documents:
                logger.warning("No processable files found in the repository")
                return []

            logger.info(f"Total: {len(all_documents)} documents before splitting")

            # 3. Splitting (chunking)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1200,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            chunks = splitter.split_documents(all_documents)

            # 4. Enrich metadata
            for chunk in chunks:
                if "file_path" not in chunk.metadata:
                    source = chunk.metadata.get("source", "")
                    chunk.metadata["file_path"] = os.path.relpath(source, target_dir) if source else "unknown"

            logger.info(f"Repository processed: {len(chunks)} chunks generated")
            return chunks

        finally:
            # Always clean up the clone, even on error
            shutil.rmtree(target_dir, ignore_errors=True)

    # ──────────────────────────────────────────────────────────────────
    # Loaders by file type
    # ──────────────────────────────────────────────────────────────────

    def _load_code_files(self, repo_dir: str) -> list[Document]:
        """
        Loads source code files with LanguageParser.
        This parser understands code structure (functions, classes)
        and produces smarter chunks.

        Uses os.walk to respect IGNORE_DIRS (e.g. node_modules)
        before passing files to LanguageParser.
        """
        code_suffixes_set = set(CODE_SUFFIXES)
        documents = []

        for root, dirs, files in os.walk(repo_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for filename in files:
                _, ext = os.path.splitext(filename)
                if ext.lower() not in code_suffixes_set:
                    continue
                if filename in IGNORE_FILES:
                    continue

                filepath = os.path.join(root, filename)
                try:
                    loader = GenericLoader.from_path(
                        root,
                        glob=filename,
                        suffixes=[ext],
                        parser=LanguageParser()
                    )
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata["type"] = "source_code"
                        doc.metadata["file_path"] = os.path.relpath(
                            doc.metadata["source"], repo_dir
                        )
                    documents.extend(docs)
                except Exception as e:
                    logger.warning(f"Error loading {filepath}: {e}")

        return documents

    def _load_notebooks(self, repo_dir: str) -> list[Document]:
        """
        Loads .ipynb notebooks by extracting code and markdown cells.

        A notebook is a JSON with a list of cells. Each cell has:
        - cell_type: "code" or "markdown"
        - source: list of content lines

        We concatenate all cells into a single document per notebook,
        marking each cell with its type so the AI understands the context.
        """
        documents = []

        for root, dirs, files in os.walk(repo_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for filename in files:
                if not filename.endswith(".ipynb"):
                    continue

                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        notebook = json.load(f)

                    cells = notebook.get("cells", [])
                    if not cells:
                        continue

                    # Extract content from each cell with its type
                    parts = []
                    for cell in cells:
                        cell_type = cell.get("cell_type", "unknown")
                        source = "".join(cell.get("source", []))
                        if source.strip():
                            parts.append(f"[{cell_type.upper()}]\n{source}")

                    if parts:
                        content = "\n\n".join(parts)
                        rel_path = os.path.relpath(filepath, repo_dir)
                        documents.append(Document(
                            page_content=content,
                            metadata={
                                "source": filepath,
                                "type": "notebook",
                                "file_path": rel_path,
                            }
                        ))

                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.warning(f"Error reading notebook {filepath}: {e}")

        return documents

    def _load_text_files(self, repo_dir: str) -> list[Document]:
        """
        Loads text, configuration and special files.
        Reads them as plain text — no specialized parser needed.
        """
        valid_suffixes = set(TEXT_SUFFIXES + CONFIG_SUFFIXES)
        documents = []

        for root, dirs, files in os.walk(repo_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for filename in files:
                # Skip lock/generated files
                if filename in IGNORE_FILES:
                    continue

                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, repo_dir)

                # Determine if we should process this file
                _, ext = os.path.splitext(filename)
                is_valid_ext = ext.lower() in valid_suffixes
                is_special = filename in SPECIAL_FILES

                if not (is_valid_ext or is_special):
                    continue

                # Skip code files (already processed by LanguageParser)
                if ext.lower() in set(CODE_SUFFIXES):
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read(MAX_FILE_SIZE)

                    if not content.strip():
                        continue

                    # Determine type based on extension
                    if ext.lower() in {".md", ".txt", ".rst"}:
                        file_type = "documentation"
                    elif ext.lower() == ".sql":
                        file_type = "database_schema"
                    elif filename in SPECIAL_FILES or ext.lower() in {".yml", ".yaml", ".toml", ".json"}:
                        file_type = "configuration"
                    else:
                        file_type = "text"

                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": filepath,
                            "type": file_type,
                            "file_path": rel_path,
                        }
                    ))

                except (UnicodeDecodeError, PermissionError) as e:
                    logger.warning(f"Error reading {filepath}: {e}")

        return documents