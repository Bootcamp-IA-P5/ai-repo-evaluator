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
    <div className={`prose prose-sm max-w-none ${className}`}>
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
          <p className="text-sm text-gray-700 leading-relaxed mb-3">{children}</p>
        ),
        code: ({ children, className }) => {
          const isInline = !className;
          return isInline ? (
            <code className="bg-gray-100 text-sm px-1.5 py-0.5 rounded border border-gray-200">
              {children}
            </code>
          ) : (
            <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-x-auto">
              <code className="text-sm">{children}</code>
            </pre>
          );
        },
        pre: ({ children }) => (
          <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-x-auto">
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
          <li className="text-sm text-gray-700">{children}</li>
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
            className="text-indigo-600 hover:text-indigo-800 underline"
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
          <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-200">
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
          <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-3 py-2 text-sm text-gray-700">{children}</td>
        ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
