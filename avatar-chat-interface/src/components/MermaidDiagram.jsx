import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Network, Copy, Check, AlertCircle } from 'lucide-react';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: '#070913',
    primaryColor: '#06b6d4',
    primaryTextColor: '#f8fafc',
    primaryBorderColor: '#0891b2',
    lineColor: '#38bdf8',
    secondaryColor: '#8b5cf6',
    tertiaryColor: '#1e293b',
  },
  securityLevel: 'loose',
  flowchart: {
    curve: 'basis',
    useMaxWidth: true,
  },
});

export default function MermaidDiagram({ code }) {
  const containerRef = useRef(null);
  const [svg, setSvg] = useState('');
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const renderDiagram = async () => {
      if (!code) return;
      const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;

      try {
        setError(null);
        // Sanitize code
        const cleanCode = code.trim();
        const { svg: renderedSvg } = await mermaid.render(id, cleanCode);
        if (isMounted) {
          setSvg(renderedSvg);
        }
      } catch (err) {
        console.warn('Mermaid rendering error:', err);
        if (isMounted) {
          setError(err.message || 'Diagram syntax parsing error.');
        }
      }
    };

    renderDiagram();
    return () => {
      isMounted = false;
    };
  }, [code]);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (error) {
    return (
      <div className="my-3 rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 text-xs text-amber-300 font-mono">
        <div className="flex items-center gap-1.5 font-semibold mb-1 text-amber-400">
          <AlertCircle size={14} />
          <span>Diagram Render Fallback</span>
        </div>
        <pre className="p-2 bg-black/40 rounded overflow-x-auto text-[11px] text-slate-300">
          {code}
        </pre>
      </div>
    );
  }

  return (
    <div className="my-3 rounded-xl border border-cyan-500/30 bg-[#070913]/90 shadow-[0_0_20px_rgba(6,182,212,0.15)] overflow-hidden">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border-b border-cyan-500/20 text-xs">
        <div className="flex items-center gap-1.5 text-cyan-400 font-mono font-medium">
          <Network size={14} />
          <span className="tracking-wide uppercase text-[11px]">Visual Concept Map</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-cyan-300 px-2 py-0.5 rounded bg-slate-800/60 hover:bg-slate-700/60 transition-colors"
          title="Copy Diagram Code"
        >
          {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      {/* SVG Diagram Canvas */}
      <div
        ref={containerRef}
        className="p-4 overflow-x-auto flex items-center justify-center min-h-[140px] [&_svg]:max-w-full [&_svg]:h-auto"
        dangerouslySetInnerHTML={{ __html: svg }}
      />
    </div>
  );
}
