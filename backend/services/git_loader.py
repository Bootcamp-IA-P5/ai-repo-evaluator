import os
import re
import json
import shutil
import tempfile
from core.logging_config import logger
from core.settings import settings
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


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
        # Validate GitHub URL — HTTPS only for public repos
        github_pattern = re.compile(
            r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(\.git)?$"
        )
        if not github_pattern.match(repo_url):
            raise ValueError(
                "Invalid repository URL. Only public GitHub HTTPS URLs are supported "
                "(e.g. https://github.com/owner/repo)"
            )

        target_dir = tempfile.mkdtemp(prefix="repo_clone_")

        try:
            # 1. Shallow clone — only latest snapshot, no history needed for RAG
            try:
                Repo.clone_from(
                    repo_url,
                    target_dir,
                )
            except Exception as e:
                raise RuntimeError(f"Error cloning repository: {str(e)}") from e

            # 2. Load files by type
            all_documents = []

            # 2a. Source code → LanguageParser (understands code structure)
            code_docs = self._load_code_files(target_dir)
            all_documents.extend(code_docs)
            logger.debug(f"Source code: {len(code_docs)} documents loaded")

            # 2b. Notebooks .ipynb → extract cells
            notebook_docs = self._load_notebooks(target_dir)
            all_documents.extend(notebook_docs)
            logger.debug(f"Notebooks: {len(notebook_docs)} documents loaded")

            # 2c. Text, configuration and special files → plain text
            text_docs = self._load_text_files(target_dir)
            all_documents.extend(text_docs)
            logger.debug(f"Text/config: {len(text_docs)} documents loaded")
            
            #2d. Git history -> Commits and branches
            git_docs = self._load_git_history(target_dir)
            all_documents.extend(git_docs)
            logger.debug(f"Git history: {len(git_docs)} commits loaded")
            
            # 2e. Directory Structure
            structure_doc = self._generate_repo_tree(target_dir)
            all_documents.append(structure_doc)
            logger.debug("Directory structure map generated and added to documents")

            if not all_documents:
                logger.warning("No processable files found in the repository")
                return []

            logger.debug(f"Total: {len(all_documents)} documents before splitting")

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

            logger.debug(f"Repository processed: {len(chunks)} chunks generated")
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
        code_suffixes_set = set(settings.CODE_SUFFIXES)
        documents = []

        for root, dirs, files in os.walk(repo_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in settings.IGNORE_DIRS]

            for filename in files:
                _, ext = os.path.splitext(filename)
                ext = ext.lower()
                if ext not in code_suffixes_set:
                    continue
                if filename in settings.IGNORE_FILES:
                    continue

                filepath = os.path.join(root, filename)
                try:
                    loader = GenericLoader.from_filesystem(
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
            dirs[:] = [d for d in dirs if d not in settings.IGNORE_DIRS]

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

                except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
                    logger.warning(f"Error reading notebook {filepath}: {e}")

        return documents

    def _load_text_files(self, repo_dir: str) -> list[Document]:
        """
        Loads text, configuration and special files.
        Reads them as plain text — no specialized parser needed.
        """
        valid_suffixes = set(settings.TEXT_SUFFIXES + settings.CONFIG_SUFFIXES)
        documents = []

        for root, dirs, files in os.walk(repo_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in settings.IGNORE_DIRS]

            for filename in files:
                # Skip lock/generated files
                if filename in settings.IGNORE_FILES:
                    continue

                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, repo_dir)

                # Determine if we should process this file
                _, ext = os.path.splitext(filename)
                is_valid_ext = ext.lower() in valid_suffixes
                is_special = filename in settings.SPECIAL_FILES

                if not (is_valid_ext or is_special):
                    continue

                # Skip code files (already processed by LanguageParser)
                if ext.lower() in set(settings.CODE_SUFFIXES):
                    continue

                # Skip files larger than MAX_FILE_SIZE
                file_size = os.path.getsize(filepath)
                if file_size > settings.MAX_FILE_SIZE:
                    logger.debug(f"Skipping large file ({file_size} bytes): {rel_path}")
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    if not content.strip():
                        continue

                    # Determine type based on extension
                    if ext.lower() in {".md", ".txt", ".rst"}:
                        file_type = "documentation"
                    elif ext.lower() == ".sql":
                        file_type = "database_schema"
                    elif filename in settings.SPECIAL_FILES or ext.lower() in {".yml", ".yaml", ".toml", ".json"}:
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
    
    def _load_git_history(self, target_dir) -> list[Document]:
        git_docs = []
        try:
            repo = Repo(target_dir)
            # Only las 100 commits
            for commit in repo.iter_commits(max_count=100):
                # Create content that can be used by the LLM
                content = (
                    f"GIT_COMMIT_ENTRY:\n"
                    f"Hash: {commit.hexsha}\n"
                    f"Author: {commit.author.name}\n"
                    f"Date: {commit.committed_datetime}\n"
                    f"Message: {commit.message.strip()}"
                )
                
                # Include metadata
                metadata = {
                    "source": "git_log",
                    "file_path": "GIT_HISTORY", # Ruta virtual
                    "commit_hash": commit.hexsha,
                    "author": commit.author.name,
                    "timestamp": commit.authored_date
                }
                git_docs.append(Document(page_content=content, metadata=metadata))
                
        except Exception as e:
            logger.error(f"Could not load git history: {e}")
        return git_docs
    
    def _generate_repo_tree(self, target_dir):
        tree_str = "REPOSITORY SRTUCTURE:\n"
        for root, dirs, files in os.walk(target_dir):
            # Ignorar carpetas ocultas como .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            level = root.replace(target_dir, '').count(os.sep)
            indent = ' ' * 4 * (level)
            tree_str += f"{indent}{os.path.basename(root)}/\n"
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                tree_str += f"{sub_indent}{f}\n"
        
        return Document(
            page_content=tree_str,
            metadata={"source": "repo_structure", "file_path": "DIRECTORY_TREE.md"}
        )
        