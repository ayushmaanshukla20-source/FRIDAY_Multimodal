import React, { useEffect, useRef, useState } from 'react';
import {
  Bot,
  User,
  Copy,
  Check,
  Terminal,
  FileText,
  Download,
  Image as ImageIcon,
  Sparkles,
} from 'lucide-react';
import MermaidDiagram from './MermaidDiagram';
import InteractiveFlashcards from './InteractiveFlashcards';

// ---------------------------------------------------------------------------
// Markdown, Mermaid & Multimodal Message Formatter
// ---------------------------------------------------------------------------
function FormattedMessageText({ content, attachment }) {
  const [copiedIdx, setCopiedIdx] = useState(null);

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  // Detect code blocks (```lang ... ```)
  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-2 text-[14px] leading-relaxed break-words">
      {/* Attached image preview if message has one */}
      {attachment?.previewUrl && (
        <div className="mb-2.5 rounded-xl overflow-hidden border border-cyan-500/30 max-w-sm">
          <img
            src={attachment.previewUrl}
            alt="Attached Study Material"
            className="w-full h-auto max-h-56 object-cover bg-black/60"
          />
          <div className="px-2.5 py-1 bg-slate-900/90 border-t border-cyan-500/20 text-[11px] font-mono text-cyan-300 flex items-center gap-1.5">
            <ImageIcon size={12} />
            <span>{attachment.name || 'Visual Study Payload'}</span>
          </div>
        </div>
      )}

      {parts.map((part, index) => {
        if (part.startsWith('```') && part.endsWith('```')) {
          const lines = part.slice(3, -3).trim().split('\n');
          const firstLine = lines[0].trim();
          const hasLang = /^[a-zA-Z0-9_-]+$/.test(firstLine);
          const lang = hasLang ? firstLine.toLowerCase() : 'code';
          const code = (hasLang ? lines.slice(1) : lines).join('\n');

          // 1. Render Renderable Visual Mermaid.js Concept Maps
          if (lang === 'mermaid') {
            return <MermaidDiagram key={index} code={code} />;
          }

          // 2. Check if JSON block contains flashcard deck
          if (lang === 'json' && code.includes('"front"') && code.includes('"back"')) {
            try {
              const cards = JSON.parse(code);
              if (Array.isArray(cards)) {
                return <InteractiveFlashcards key={index} cards={cards} topic="AI Generated Flashcards" />;
              }
            } catch (e) {
              // fallback to regular code block
            }
          }

          // 3. Regular Code Snippet with Syntax Styling
          return (
            <div
              key={index}
              className="my-3 rounded-xl overflow-hidden border border-slate-700/60 bg-[#060810]/95 font-mono text-[12.5px]"
            >
              <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/80 border-b border-slate-800 text-xs text-slate-400">
                <div className="flex items-center gap-1.5 text-cyan-400">
                  <Terminal size={13} />
                  <span className="uppercase text-[11px] tracking-wider">{lang}</span>
                </div>
                <button
                  onClick={() => handleCopy(code, index)}
                  className="flex items-center gap-1 hover:text-white transition-colors py-0.5 px-1.5 rounded bg-slate-800/60 hover:bg-slate-700/60"
                  title="Copy code"
                >
                  {copiedIdx === index ? (
                    <>
                      <Check size={12} className="text-emerald-400" />
                      <span className="text-[10px] text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy size={12} />
                      <span className="text-[10px]">Copy</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="p-3 overflow-x-auto text-slate-200">
                <code>{code}</code>
              </pre>
            </div>
          );
        }

        // ---------------------------------------------------------------------
        // Detect Markdown Images: ![alt](url)
        // ---------------------------------------------------------------------
        const imgMatches = [];
        const imgRegex = /!\[(.*?)\]\((https?:\/\/[^\s)]+)\)/g;
        let match;
        while ((match = imgRegex.exec(part)) !== null) {
          imgMatches.push({ alt: match[1], url: match[2] });
        }

        // Detect PDF download links in text
        const pdfMatch = part.match(/(https?:\/\/[^\s]+\/api\/study\/download\/[^\s)]+)/i);

        // Clean text of raw markdown image and duplicate download links for clean display
        const textWithoutImages = part
          .replace(/!\[(.*?)\]\((https?:\/\/[^\s)]+)\)/g, '')
          .replace(/\[Download (?:Full-Res Picture|Image)\]\([^)]+\)/gi, '')
          .trim();

        return (
          <div key={index}>
            {textWithoutImages && (
              <p className="whitespace-pre-wrap">
                {textWithoutImages.split('\n\n').map((paragraph, pIdx) => (
                  <span key={pIdx} className="block my-1">
                    {paragraph.split(/(\*\*.*?\*\*)/g).map((seg, sIdx) => {
                      if (seg.startsWith('**') && seg.endsWith('**')) {
                        return (
                          <strong key={sIdx} className="font-semibold text-cyan-300">
                            {seg.slice(2, -2)}
                          </strong>
                        );
                      }
                      return seg;
                    })}
                  </span>
                ))}
              </p>
            )}

            {/* Render High-Res Generated Image Card */}
            {imgMatches.map((img, iIdx) => (
              <div
                key={iIdx}
                className="my-3 rounded-2xl overflow-hidden border border-cyan-500/40 bg-slate-950/90 shadow-[0_0_25px_rgba(6,182,212,0.25)] transition-all"
              >
                <div className="relative group overflow-hidden bg-black/70 flex items-center justify-center min-h-[220px]">
                  <img
                    src={img.url}
                    alt={img.alt}
                    className="w-full max-h-96 object-contain rounded-t-2xl transition-transform duration-300 group-hover:scale-[1.02]"
                    loading="lazy"
                  />
                </div>
                <div className="p-3 bg-slate-900/95 border-t border-cyan-500/25 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs text-cyan-300 font-mono">
                    <Sparkles size={14} className="text-cyan-400 shrink-0 animate-pulse" />
                    <span className="font-medium truncate max-w-[200px] sm:max-w-xs">
                      {img.alt || 'Generated Picture'}
                    </span>
                  </div>
                  <a
                    href={img.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    download
                    className="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 text-xs font-mono flex items-center gap-1.5 transition-all shadow-[0_0_10px_rgba(6,182,212,0.15)]"
                  >
                    <Download size={13} />
                    <span>Download</span>
                  </a>
                </div>
              </div>
            ))}

            {/* Quick PDF Action Card if detected */}
            {pdfMatch && (
              <div className="my-2 p-2.5 rounded-xl border border-cyan-500/40 bg-cyan-950/30 flex items-center justify-between">
                <div className="flex items-center gap-2 text-cyan-300 text-xs font-mono">
                  <FileText size={16} />
                  <span>Downloadable Academic PDF Artifact</span>
                </div>
                <a
                  href={pdfMatch[1]}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 text-xs font-mono flex items-center gap-1 transition-all"
                >
                  <Download size={13} />
                  <span>Open PDF</span>
                </a>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Message Feed Container
// ---------------------------------------------------------------------------
export default function MessageList({ messages, isLoading }) {
  const scrollEndRef = useRef(null);

  // Auto-scroll on new message
  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      {messages.map((message) => {
        const isAssistant = message.role === 'assistant';

        return (
          <div
            key={message.id}
            className={`flex gap-3 ${isAssistant ? 'justify-start' : 'justify-end'} group`}
          >
            {/* Assistant Avatar Icon */}
            {isAssistant && (
              <div className="w-8 h-8 rounded-full bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center shrink-0 shadow-[0_0_12px_rgba(6,182,212,0.3)]">
                <Bot size={17} className="text-cyan-400" />
              </div>
            )}

            {/* Message Bubble */}
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-lg relative ${
                isAssistant
                  ? 'bg-[#0a0e1c]/90 text-slate-200 border border-slate-800/80'
                  : 'bg-gradient-to-r from-cyan-950/80 to-blue-950/80 text-cyan-50 border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
              }`}
            >
              <FormattedMessageText content={message.content} attachment={message.attachment} />

              <div
                className={`mt-1.5 flex items-center gap-1.5 text-[10px] font-mono ${
                  isAssistant ? 'text-slate-500' : 'text-cyan-400/60 justify-end'
                }`}
              >
                <span>{message.timestamp}</span>
              </div>
            </div>

            {/* User Icon */}
            {!isAssistant && (
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-cyan-500/30 flex items-center justify-center shrink-0 text-cyan-300">
                <User size={16} />
              </div>
            )}
          </div>
        );
      })}

      {/* Typing / Reasoning Indicator */}
      {isLoading && (
        <div className="flex gap-3 justify-start items-center">
          <div className="w-8 h-8 rounded-full bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center shrink-0 animate-pulse">
            <Bot size={17} className="text-cyan-400" />
          </div>
          <div className="rounded-2xl px-4 py-2.5 bg-[#0a0e1c]/80 border border-slate-800/80 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '300ms' }} />
            <span className="ml-2 text-xs font-mono text-cyan-300">Processing visual synthesis...</span>
          </div>
        </div>
      )}

      <div ref={scrollEndRef} />
    </div>
  );
}
