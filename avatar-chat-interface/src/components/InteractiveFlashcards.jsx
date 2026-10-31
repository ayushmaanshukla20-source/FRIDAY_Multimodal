import React, { useState } from 'react';
import { Layers, ChevronLeft, ChevronRight, RotateCw, Download, Check } from 'lucide-react';

export default function InteractiveFlashcards({ cards = [], topic = 'Study Deck' }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  if (!cards || cards.length === 0) return null;

  const currentCard = cards[currentIndex] || {};

  const handleNext = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % cards.length);
  };

  const handlePrev = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev - 1 + cards.length) % cards.length);
  };

  const handleExportCSV = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      'Front,Back\n' +
      cards
        .map((c) => `"${(c.front || '').replace(/"/g, '""')}","${(c.back || '').replace(/"/g, '""')}"`)
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${topic.replace(/\s+/g, '_')}_flashcards.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 2500);
  };

  return (
    <div className="my-3 rounded-xl border border-cyan-500/30 bg-[#080c16]/95 p-3.5 shadow-[0_0_20px_rgba(6,182,212,0.15)] select-none">
      {/* Deck Header */}
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-1.5 text-cyan-400 font-mono">
          <Layers size={14} />
          <span className="font-semibold">{topic}</span>
          <span className="text-slate-500">• {cards.length} Cards</span>
        </div>
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-1 text-[11px] text-slate-300 hover:text-cyan-300 px-2 py-0.5 rounded bg-slate-800/80 hover:bg-slate-700 transition-colors"
          title="Export as CSV / Anki Compatible Deck"
        >
          {downloaded ? <Check size={12} className="text-emerald-400" /> : <Download size={12} />}
          <span>{downloaded ? 'Exported' : 'Export Deck'}</span>
        </button>
      </div>

      {/* Flip Card Area */}
      <div
        onClick={() => setIsFlipped(!isFlipped)}
        className="relative h-44 rounded-xl cursor-pointer p-4 flex flex-col justify-between transition-all duration-300 border border-slate-700/60 bg-gradient-to-br from-slate-900/90 to-[#0c1222] hover:border-cyan-500/50"
      >
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
          <span className="uppercase tracking-wider">
            {isFlipped ? '💡 Solution / Concept' : '❓ Question / Prompt'}
          </span>
          <div className="flex items-center gap-1 text-cyan-400/80">
            <RotateCw size={12} />
            <span>Click to flip</span>
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center text-center px-3 my-2 overflow-y-auto">
          <p className="text-[14px] leading-relaxed font-medium text-slate-100">
            {isFlipped ? currentCard.back : currentCard.front}
          </p>
        </div>

        <div className="flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>Card {currentIndex + 1} of {cards.length}</span>
          <span className="text-cyan-400/70">{isFlipped ? 'Answer View' : 'Question View'}</span>
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="flex items-center justify-between pt-2.5 px-1">
        <button
          onClick={handlePrev}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-cyan-300 px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-700/60 transition-colors"
        >
          <ChevronLeft size={14} />
          <span>Previous</span>
        </button>

        {/* Progress Dots */}
        <div className="flex items-center gap-1">
          {cards.slice(0, 10).map((_, idx) => (
            <div
              key={idx}
              className={`w-1.5 h-1.5 rounded-full transition-all ${
                idx === currentIndex ? 'bg-cyan-400 w-4 shadow-[0_0_6px_#06b6d4]' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>

        <button
          onClick={handleNext}
          className="flex items-center gap-1 text-xs text-cyan-300 hover:text-cyan-100 px-2.5 py-1 rounded-lg bg-cyan-950/60 border border-cyan-500/30 hover:bg-cyan-900/60 transition-colors"
        >
          <span>Next</span>
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
}
