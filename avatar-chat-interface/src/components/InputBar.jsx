import React, { useRef, useEffect, useState } from 'react';
import {
  Send,
  Mic,
  MicOff,
  Paperclip,
  AlertCircle,
  X,
  FileText,
  FileCheck,
  Brain,
  Camera,
  Layers,
  Sparkles,
} from 'lucide-react';

const STUDY_QUICK_ACTIONS = [
  {
    id: 'ocr',
    label: '📝 OCR Notes',
    prompt: 'Transcribe these handwritten notes into structured Markdown notes with key takeaways.',
    taskType: 'ocr_notes',
  },
  {
    id: 'diagram',
    label: '🔬 Diagram Analyzer',
    prompt: 'Analyze this diagram, identify all components, explain mechanisms, and output a Mermaid concept map.',
    taskType: 'analyze_diagram',
  },
  {
    id: 'problem',
    label: '📐 Solve Problem',
    prompt: 'Solve this problem step-by-step with LaTeX equations and explain the concept.',
    taskType: 'solve_problem',
  },
  {
    id: 'flashcards',
    label: '🗂️ Flashcards',
    prompt: 'Generate 5 high-yield revision flashcards for this topic.',
    taskType: 'generate_quiz',
  },
  {
    id: 'image',
    label: '🎨 Draw Picture',
    prompt: 'Generate a picture of ',
    taskType: 'general',
  },
  {
    id: 'pdf',
    label: '📄 Export PDF',
    prompt: 'Generate a structured academic PDF study guide for this subject.',
    taskType: 'general',
  },
];

export default function InputBar({
  input,
  setInput,
  onSendMessage,
  isLoading,
  isListening,
  onToggleManualMic,
  audioLevel = 0,
  permissionError = null,
}) {
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const [attachment, setAttachment] = useState(null);
  const [selectedTaskType, setSelectedTaskType] = useState(null);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  // Listen for live speech interim updates
  useEffect(() => {
    const handleInterim = (e) => {
      if (typeof e.detail === 'string') {
        setInput(e.detail);
      }
    };
    window.addEventListener('speech-interim-transcript', handleInterim);
    return () => window.removeEventListener('speech-interim-transcript', handleInterim);
  }, [setInput]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes >= 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }
    if (bytes >= 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
    return `${Math.round(bytes / 1024)} KB`;
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const MAX_FILE_SIZE_BYTES = 1024 * 1024 * 1024; // 1 GB limit
    if (file.size > MAX_FILE_SIZE_BYTES) {
      alert(`File size (${formatFileSize(file.size)}) exceeds the maximum 1 GB limit.`);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    const isImage = file.type.startsWith('image/');
    const formattedSize = formatFileSize(file.size);

    if (isImage && file.size <= 25 * 1024 * 1024) {
      const reader = new FileReader();
      reader.onload = (uploadEvent) => {
        setAttachment({
          file,
          name: file.name,
          size: formattedSize,
          type: 'image',
          base64: uploadEvent.target.result,
          previewUrl: uploadEvent.target.result,
        });
      };
      reader.readAsDataURL(file);
    } else {
      setAttachment({
        file,
        name: file.name,
        size: formattedSize,
        type: isImage ? 'image' : 'document',
        previewUrl: null,
      });
    }
  };

  const handleRemoveAttachment = () => {
    setAttachment(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleQuickAction = (action) => {
    setInput(action.prompt);
    setSelectedTaskType(action.taskType);
    textareaRef.current?.focus();
  };

  const handleSend = () => {
    const promptText = (input || '').trim() || (attachment ? 'Analyze this study payload, Boss.' : '');
    if (!promptText || isLoading) return;

    onSendMessage(promptText, {
      attachment: attachment,
      taskType: selectedTaskType,
    });

    setInput('');
    setAttachment(null);
    setSelectedTaskType(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="p-3 border-t border-slate-800/80 bg-[#070911]/95 backdrop-blur-md">
      {/* 1. Quick Study Action Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-1 scrollbar-none text-[11px] font-mono">
        {STUDY_QUICK_ACTIONS.map((action) => (
          <button
            key={action.id}
            type="button"
            onClick={() => handleQuickAction(action)}
            className="px-2.5 py-1 rounded-full whitespace-nowrap bg-slate-900/80 border border-slate-700/60 hover:border-cyan-400 text-slate-300 hover:text-cyan-300 hover:bg-slate-800 transition-all flex items-center gap-1 shrink-0"
          >
            <span>{action.label}</span>
          </button>
        ))}
      </div>

      {/* 2. Permission Error Alert */}
      {permissionError && (
        <div className="mb-2 px-3 py-2 rounded-lg bg-red-950/70 border border-red-500/60 flex items-center gap-2 text-xs text-red-200 font-mono shadow-[0_0_15px_rgba(239,68,68,0.2)]">
          <AlertCircle size={15} className="text-red-400 shrink-0" />
          <span>{permissionError}</span>
        </div>
      )}

      {/* 3. Active Voice Listening HUD */}
      {isListening ? (
        <div className="mb-2 px-3 py-1.5 rounded-lg bg-cyan-950/50 border border-cyan-500/50 flex items-center justify-between text-xs font-mono shadow-[0_0_18px_rgba(6,182,212,0.2)]">
          <div className="flex items-center gap-2 text-cyan-300">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping shadow-[0_0_10px_#00f2fe]" />
            <span className="font-semibold uppercase tracking-wider">Listening to Voice...</span>
            <div className="flex items-center gap-1 ml-1.5 h-4">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="w-1 bg-cyan-400 rounded-full transition-all duration-75"
                  style={{
                    height: `${Math.max(4, Math.min(18, (audioLevel / 16) * (i + 1) * 2.8))}px`,
                  }}
                />
              ))}
            </div>
          </div>
          <div className="text-cyan-400/90 text-[11px] font-mono">
            Auto-sends on 1.2s pause • <span className="text-slate-300">Speak naturally</span>
          </div>
        </div>
      ) : null}

      {/* 4. Attachment Preview Chip */}
      {attachment && (
        <div className="mb-2 p-2 rounded-xl bg-cyan-950/40 border border-cyan-500/40 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2.5 overflow-hidden">
            {attachment.previewUrl ? (
              <img
                src={attachment.previewUrl}
                alt="Preview"
                className="w-9 h-9 rounded-lg object-cover border border-cyan-400/30 shrink-0"
              />
            ) : (
              <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400 shrink-0">
                <FileCheck size={18} />
              </div>
            )}
            <div className="overflow-hidden">
              <span className="font-medium text-slate-100 truncate block text-xs">
                {attachment.name}
              </span>
              <span className="text-[10px] text-cyan-400/80 font-mono">
                {attachment.size} • Ready for Multimodal Analysis
              </span>
            </div>
          </div>
          <button
            onClick={handleRemoveAttachment}
            className="p-1 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
          >
            <X size={15} />
          </button>
        </div>
      )}

      {/* 5. Main Input Bar */}
      <div className="glass-input rounded-xl p-2 flex flex-col gap-2 transition-all">
        {/* Hidden File Input */}
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept="image/*,.pdf,.docx,.doc,.txt,.md"
          onChange={handleFileSelect}
        />

        {/* Text Area */}
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isListening
              ? 'Transcribing your voice live... Speak naturally...'
              : 'Ask questions, upload handwritten notes, diagrams, or ask to export PDF study guide...'
          }
          disabled={isLoading}
          className="w-full bg-transparent resize-none outline-none text-slate-100 placeholder-slate-500 text-[14px] leading-relaxed px-2 py-1 max-h-[120px]"
        />

        {/* Action Controls */}
        <div className="flex items-center justify-between pt-1 px-1">
          <div className="flex items-center gap-2">
            {/* Attachment Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800/60 transition-colors flex items-center gap-1 text-xs font-mono"
              title="Upload Notes, Diagram, Math Problem, or PDF"
            >
              <Paperclip size={17} />
              <span className="hidden sm:inline">Attach Material</span>
            </button>

            {/* Mic Button */}
            <button
              type="button"
              onClick={onToggleManualMic}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 font-mono text-[12px] font-semibold cursor-pointer ${
                isListening
                  ? 'bg-red-500/25 text-red-300 border border-red-500/60 shadow-[0_0_20px_rgba(239,68,68,0.4)] animate-pulse'
                  : 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/25 hover:border-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.2)]'
              }`}
              title={isListening ? 'Click to stop microphone' : 'Click to start voice listening'}
            >
              {isListening ? <MicOff size={15} /> : <Mic size={15} />}
              <span>{isListening ? 'STOP' : 'MIC'}</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            {/* Send Button */}
            <button
              type="button"
              onClick={handleSend}
              disabled={(!input.trim() && !attachment) || isLoading}
              className={`p-2 rounded-lg transition-all flex items-center justify-center cursor-pointer ${
                (input.trim() || attachment) && !isLoading
                  ? 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-[0_0_15px_rgba(6,182,212,0.4)] scale-100 hover:scale-105 active:scale-95'
                  : 'bg-slate-800 text-slate-600 cursor-not-allowed scale-95'
              }`}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
