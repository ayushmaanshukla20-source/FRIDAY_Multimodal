import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Trash2, Cpu, Volume2, VolumeX, BarChart2, Flame, Sparkles } from 'lucide-react';
import MessageList from './MessageList';
import InputBar from './InputBar';
import StudyDashboardDrawer from './StudyDashboardDrawer';
import { useVoiceAssistant } from '../hooks/useVoiceAssistant';
import { detectChromeIntent } from '../utils/chromeIntent';
import {
  sendChatMessage,
  sendChromeCommand,
  uploadKnowledgeDocument,
  generateStudyPDF,
  API_BASE,
} from '../utils/api';
import { setAvatarVoiceState } from '../utils/avatarState';

const INITIAL_MESSAGES = [
  {
    id: 'msg-1',
    role: 'assistant',
    content:
      'Systems initialized. I am Friday, an advanced AI assistant created and engineered by Ayushmaan Shukla. I am your multimodal **Student Productivity Assistant** and Cybernetic Copilot.\n\nHere is how I can accelerate your learning today:\n- 📝 **Handwritten Notes to Digital**: Attach a photo of your notebook to transcribe and structure into Markdown notes.\n- 🔬 **Diagram & Chart Analyzer**: Upload any science, physics, or architecture figure for component breakdown and interactive Mermaid.js concept maps.\n- 📐 **Step-by-Step Problem Solver**: Send math formulas or code bugs for rigorous LaTeX solutions.\n- 📄 **PDF Study Pack Export**: Request downloadable PDF study guides, formula cheat sheets, and flashcards.\n- 📊 **Study Analytics & Pomodoro**: Click **"Study Hub"** above to track your active streak, subject balance, and focus timer.',
    timestamp: '10:00 AM',
  },
];

export default function ChatPanel({ onVoiceStateChange }) {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [isStudyHubOpen, setIsStudyHubOpen] = useState(false);

  const ttsEnabledRef = useRef(ttsEnabled);
  useEffect(() => {
    ttsEnabledRef.current = ttsEnabled;
  }, [ttsEnabled]);

  const voiceRef = useRef(null);

  // Helper to vocalize response safely using SpeechSynthesis
  const safelySpeak = useCallback((text) => {
    if (!ttsEnabledRef.current || !text) return;
    try {
      if (voiceRef.current?.speak) {
        voiceRef.current.speak(text);
      }
    } catch (e) {
      console.warn('Speech synthesis call failed:', e);
    }
  }, []);

  // Primary send message handler (supports text, voice, and multimodal attachments)
  const handleSendMessage = useCallback(
    async (text, meta = {}) => {
      const query = (text || '').trim();
      const attachment = meta.attachment;
      const taskType = meta.taskType;

      if (!query && !attachment) return;

      const userMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: query || (attachment ? `Uploaded ${attachment.name}` : ''),
        attachment: attachment
          ? {
              name: attachment.name,
              previewUrl: attachment.previewUrl,
              type: attachment.type,
            }
          : null,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        // ---------------------------------------------------------------------
        // 1. DOCUMENT INGESTION (RAG)
        // ---------------------------------------------------------------------
        if (attachment && attachment.type === 'document') {
          try {
            const uploadRes = await uploadKnowledgeDocument(attachment.file);
            const docName = uploadRes.document?.name || attachment.name;
            const chunks = uploadRes.chunks_indexed || 0;

            const chatRes = await sendChatMessage(
              query || `Summarize the uploaded document: ${docName} and extract key study concepts.`,
              { useRag: true }
            );

            const assistantMessage = {
              id: `asst-${Date.now()}`,
              role: 'assistant',
              content: `📑 **Document Ingested & Indexed**\n\n- **File**: \`${docName}\`\n- **Knowledge Chunks**: \`${chunks}\`\n\n${chatRes.reply}`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };

            setMessages((prev) => [...prev, assistantMessage]);
            setIsLoading(false);
            safelySpeak(chatRes.reply);
            return;
          } catch (docErr) {
            console.error('Document ingestion error:', docErr);
            const assistantMessage = {
              id: `asst-${Date.now()}`,
              role: 'assistant',
              content: `⚠️ **Document Processing Error**: ${docErr.message}`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setIsLoading(false);
            return;
          }
        }

        // ---------------------------------------------------------------------
        // 2. CHROME AUTOMATION INTENT ROUTING (Backend Bridge on :8080)
        // ---------------------------------------------------------------------
        const chromeIntent = detectChromeIntent(query);
        if (chromeIntent && !attachment) {
          try {
            const result = await sendChromeCommand({
              command: query,
              action: chromeIntent.action,
              query: chromeIntent.query,
            });

            const spokenReply = result.message || `Executed ${result.action} in Chrome.`;

            const assistantMessage = {
              id: `asst-${Date.now()}`,
              role: 'assistant',
              content: `🌐 **Chrome Automation Executed**\n\n- **Directive**: \`${query}\`\n- **Action**: \`${result.action}\`\n- **Status**: \`${result.success ? 'Success' : 'Failed'}\`\n\n${spokenReply}`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };

            setMessages((prev) => [...prev, assistantMessage]);
            setIsLoading(false);
            safelySpeak(spokenReply);
            return;
          } catch (err) {
            console.warn('Chrome backend bridge error:', err);
            const errMsg = `Boss, unable to connect to local Chrome bridge at ${API_BASE}/api/chrome: ${err.message}.`;
            const assistantMessage = {
              id: `asst-${Date.now()}`,
              role: 'assistant',
              content: `⚠️ **Bridge Connection Error**\n\n${errMsg}`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setIsLoading(false);
            safelySpeak('Unable to reach the Chrome backend bridge, Boss.');
            return;
          }
        }

        // ---------------------------------------------------------------------
        // 3. EXPLICIT PDF GENERATION INTENT
        // ---------------------------------------------------------------------
        if (
          !attachment &&
          (/\b(?:export|generate|create|make|compile)\s+(?:a\s+)?(?:study\s+guide|cheat\s+sheet|pdf)\b/i.test(query) ||
            /\b(?:download\s+pdf|pdf\s+study\s+guide)\b/i.test(query))
        ) {
          try {
            const subjectMatch = query.match(/(?:for|in|on)\s+([a-zA-Z0-9\s#+]+?)(?:\s+(?:pdf|guide|sheet))?$/i);
            const detectedSubject = subjectMatch ? subjectMatch[1].trim() : 'Active Revision Block';

            const pdfRes = await generateStudyPDF({
              title: `${detectedSubject}: AI Study Pack`,
              subject: detectedSubject,
              documentType: query.toLowerCase().includes('cheat') ? 'cheat_sheet' : 'study_guide',
              keyTakeaways: [
                'Prioritize conceptual clarity over rote memorization.',
                'Utilize active recall and spaced repetition flashcards.',
                'Cross-reference formula derivations with practice problems.',
              ],
              sections: [
                {
                  title: '1. Foundational Core Principles',
                  content:
                    'Mastering foundational principles ensures adaptive analytical capability across complex examinations.',
                },
                {
                  title: '2. High-Yield Summary & Methodology',
                  content:
                    '- Break problems down into known and unknown variables.\n- Apply canonical mathematical and structural formulations.\n- Validate edge conditions and units.',
                },
              ],
              practiceQuestions: [
                {
                  question: `Explain the fundamental theorem governing ${detectedSubject}.`,
                  answer: 'Derived through axiomatic principles and empirical validation.',
                },
              ],
            });

            if (pdfRes.success && pdfRes.download_url) {
              const msg = `Boss, I have compiled your **${pdfRes.title}** into a downloadable PDF study guide.`;
              const assistantMessage = {
                id: `asst-${Date.now()}`,
                role: 'assistant',
                content: `📄 **Academic PDF Artifact Generated**\n\n- **Title**: \`${pdfRes.title}\`\n- **Filename**: \`${pdfRes.filename}\`\n\nDownload link: ${pdfRes.download_url}`,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              };
              setMessages((prev) => [...prev, assistantMessage]);
              setIsLoading(false);
              safelySpeak(msg);
              return;
            }
          } catch (pdfErr) {
            console.warn('PDF direct generation fallback:', pdfErr);
          }
        }

        // ---------------------------------------------------------------------
        // 4. CONVERSATIONAL AI & MULTIMODAL VISION QUERY
        // ---------------------------------------------------------------------
        try {
          const { reply } = await sendChatMessage(query, {
            imageBase64: attachment?.type === 'image' ? attachment.base64 : undefined,
            taskType: taskType,
            useRag: true,
          });

          const assistantMessage = {
            id: `asst-${Date.now()}`,
            role: 'assistant',
            content: reply,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          };

          setMessages((prev) => [...prev, assistantMessage]);
          setIsLoading(false);
          safelySpeak(reply);
        } catch (chatErr) {
          console.error('Chat API Error:', chatErr);
          const errMsg = `Boss, communication with the neural core failed: ${chatErr.message}.`;
          const assistantMessage = {
            id: `asst-${Date.now()}`,
            role: 'assistant',
            content: `⚠️ **AI Neural Core Error**\n\n${errMsg}\n\nPlease verify that the backend is active on \`${API_BASE}\`.`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setIsLoading(false);
          safelySpeak('Communication with the neural core failed, Boss.');
        }
      } catch (unexpectedErr) {
        console.error('Unexpected error in handleSendMessage:', unexpectedErr);
        const fallbackMsg = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: `⚠️ **Operational Exception**: ${unexpectedErr.message || 'Operation failed.'}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, fallbackMsg]);
        setIsLoading(false);
        safelySpeak('An unexpected operational error occurred, Boss.');
      }
    },
    [safelySpeak]
  );

  // Voice Assistant Hook
  const voice = useVoiceAssistant({
    onAutoSend: (transcript) => {
      handleSendMessage(transcript);
    },
  });

  // Store voice in ref for safelySpeak
  useEffect(() => {
    voiceRef.current = voice;
  }, [voice]);

  // Synchronize high-frequency voice telemetry directly with Three.js store
  useEffect(() => {
    setAvatarVoiceState({
      isListening: voice.isListening,
      isSpeaking: voice.isSpeaking,
      audioLevel: voice.audioLevel,
    });
    if (onVoiceStateChange) {
      onVoiceStateChange({
        isListening: voice.isListening,
        isSpeaking: voice.isSpeaking,
        audioLevel: voice.audioLevel,
      });
    }
  }, [voice.isListening, voice.isSpeaking, voice.audioLevel, onVoiceStateChange]);

  const handleClearChat = () => {
    if (voiceRef.current?.stopSpeaking) {
      voiceRef.current.stopSpeaking();
    }
    setMessages([
      {
        id: `asst-${Date.now()}`,
        role: 'assistant',
        content:
          'Conversation buffer refreshed. Ready for study analysis, note transcription, or problem solving, Boss.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#080b13]/80 backdrop-blur-xl border-l border-cyan-500/15 relative z-10 select-text">
      {/* ---------------- SIDEBAR HEADER ---------------- */}
      <div className="px-4 py-3 border-b border-slate-800/80 bg-[#070911]/90 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-950/80 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.25)]">
            <Cpu size={18} />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              Friday AI Study Copilot
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 font-mono">
                Multimodal
              </span>
            </h1>
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <span
                className={`w-2 h-2 rounded-full transition-colors duration-300 ${
                  voice.isSpeaking
                    ? 'bg-amber-400 shadow-[0_0_8px_#f59e0b]'
                    : voice.isListening
                    ? 'bg-emerald-400 shadow-[0_0_8px_#10b981] animate-pulse'
                    : 'bg-cyan-400 shadow-[0_0_8px_#00f2fe]'
                }`}
              />
              <span className="font-mono text-[11px]">
                {voice.isSpeaking
                  ? 'Friday Speaking'
                  : voice.isListening
                  ? 'Listening (Auto-send)'
                  : 'Vision & Study Core Online'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Study Hub Drawer Toggle Button */}
          <button
            onClick={() => setIsStudyHubOpen(!isStudyHubOpen)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-gradient-to-r from-amber-500/15 to-cyan-500/15 border border-amber-500/30 hover:border-cyan-400 text-xs font-mono text-amber-300 hover:text-white transition-all shadow-[0_0_12px_rgba(245,158,11,0.15)] cursor-pointer"
            title="Open Student Productivity Dashboard & Pomodoro"
          >
            <Flame size={14} className="text-amber-400" />
            <span className="hidden sm:inline font-semibold">Study Hub</span>
          </button>

          {/* TTS Mute / Unmute Toggle */}
          <button
            onClick={() => setTtsEnabled(!ttsEnabled)}
            title={ttsEnabled ? 'Mute Assistant Voice' : 'Unmute Assistant Voice'}
            className={`p-2 rounded-lg border transition-all ${
              ttsEnabled
                ? 'bg-cyan-950/60 border-cyan-500/40 text-cyan-300 hover:bg-cyan-900/60 shadow-[0_0_10px_rgba(6,182,212,0.15)]'
                : 'bg-slate-900/60 border-slate-700/50 text-slate-500 hover:text-slate-300'
            }`}
          >
            {ttsEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          </button>

          {/* Clear History Button */}
          <button
            onClick={handleClearChat}
            title="Clear Chat History"
            className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 hover:bg-rose-950/20 transition-all"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* ---------------- CHAT STREAM / MESSAGE LIST ---------------- */}
      <div className="flex-1 overflow-hidden relative">
        <MessageList messages={messages} isLoading={isLoading} />

        {/* Slide-over Study Dashboard Drawer */}
        <StudyDashboardDrawer
          isOpen={isStudyHubOpen}
          onClose={() => setIsStudyHubOpen(false)}
          onNotify={(note) => {
            safelySpeak(note);
          }}
        />
      </div>

      {/* ---------------- DOCKED MULTIMODAL INPUT AREA ---------------- */}
      <InputBar
        input={input}
        setInput={setInput}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        isListening={voice.isListening}
        onToggleManualMic={voice.toggleManualMic}
        audioLevel={voice.audioLevel}
        permissionError={voice.permissionError}
      />
    </div>
  );
}
