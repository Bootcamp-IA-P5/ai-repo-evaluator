'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-sm max-w-none min-w-0 wrap-anywhere ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Custom styling for different markdown elements
        h1: ({ children }) => (
          <h1 className="text-lg font-semibold text-gray-900 mb-2">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-base font-semibold text-gray-800 mb-2">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-sm font-semibold text-gray-700 mb-2">{children}</h3>
        ),
        p: ({ children }) => (
          <p className="text-sm text-gray-700 leading-relaxed mb-3 wrap-anywhere">{children}</p>
        ),
        code: ({ children, className }) => {
          const isInline = !className;
          return isInline ? (
            <code className="bg-gray-100 text-gray-900 text-sm font-mono px-1.5 py-0.5 rounded border border-gray-300 break-all">
              {children}
            </code>
          ) : (
            <code className="block text-sm text-gray-900 font-mono whitespace-pre-wrap wrap-break-word sm:whitespace-pre">
              {children}
            </code>
          );
        },
        pre: ({ children }) => (
          <pre className="bg-gray-100 border border-gray-300 rounded-lg p-3 overflow-x-auto max-w-full w-full text-gray-900">
            {children}
          </pre>
        ),
        ul: ({ children }) => (
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1 mb-3">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside text-sm text-gray-700 space-y-1 mb-3">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="text-sm text-gray-700 wrap-anywhere">{children}</li>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-gray-300 pl-3 text-sm text-gray-600 italic mb-3">
            {children}
          </blockquote>
        ),
        a: ({ children, href }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 hover:text-indigo-800 underline break-all"
          >
            {children}
          </a>
        ),
        strong: ({ children }) => (
          <strong className="font-semibold text-gray-900">{children}</strong>
        ),
        em: ({ children }) => (
          <em className="italic text-gray-700">{children}</em>
        ),
        table: ({ children }) => (
          <div className="max-w-full overflow-x-auto">
            <table className="w-full table-auto border border-gray-200 text-xs sm:text-sm">
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-gray-50">{children}</thead>
        ),
        tbody: ({ children }) => (
          <tbody className="bg-white">{children}</tbody>
        ),
        tr: ({ children }) => (
          <tr className="border-t border-gray-200">{children}</tr>
        ),
        th: ({ children }) => (
          <th className="px-2 sm:px-3 py-1.5 sm:py-2 text-left text-[10px] sm:text-xs font-semibold text-gray-600 uppercase tracking-wider align-top whitespace-normal wrap-anywhere">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-2 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-gray-700 align-top whitespace-normal wrap-anywhere">
            {children}
          </td>
        ),
        ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
