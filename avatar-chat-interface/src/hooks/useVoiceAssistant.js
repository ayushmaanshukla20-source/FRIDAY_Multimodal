import { useState, useEffect, useRef, useCallback } from 'react';

// Synthesizes a crisp, futuristic 2-tone HUD activation chime using Web Audio API
export function playActivationPing() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.type = 'sine';
    const now = ctx.currentTime;
    osc.frequency.setValueAtTime(680, now);
    osc.frequency.exponentialRampToValueAtTime(1180, now + 0.1);

    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

    osc.start(now);
    osc.stop(now + 0.3);
  } catch (e) {
    // ignore
  }
}

/**
 * Robust, Zero-Conflict Voice Assistant Hook:
 * - 100% Native Web Speech API without getUserMedia hardware locks
 * - Handles Chrome user-gesture permission model cleanly
 * - Live transcript streaming with 1.2s silence auto-dispatch
 * - Wake word support ("Hello Friday" / "Hey Friday")
 * - Speech synthesis with Chrome GC pin and safety timer
 */
export function useVoiceAssistant({ onAutoSend }) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [permissionError, setPermissionError] = useState(null);
  const [speechSupported, setSpeechSupported] = useState(true);

  const recognitionRef = useRef(null);
  const userWantsListeningRef = useRef(false);
  const isSpeakingRef = useRef(false);
  const isRunningRef = useRef(false);
  const silenceTimeoutRef = useRef(null);
  const currentTranscriptRef = useRef('');
  const isSendingRef = useRef(false);
  const safetyTtsTimeoutRef = useRef(null);
  const levelAnimRef = useRef(null);
  const startListeningRef = useRef(null);

  // Clean formatting for natural spoken dialogue
  const cleanSpeechText = useCallback((text) => {
    if (!text) return '';
    return text
      .replace(/```[\s\S]*?```/g, 'Code block omitted.')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/\[ACTION:[^\]]+\]/g, '')
      .replace(/[*#_>~]/g, '')
      .replace(/https?:\/\/\S+/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }, []);

  // Animate audioLevel when speaking / sound detected
  const pulseAudioLevel = (active) => {
    if (active) {
      setAudioLevel(Math.floor(15 + Math.random() * 25));
    } else {
      setAudioLevel(0);
    }
  };

  // Dispatch final speech transcript to chat
  const dispatchSpeech = useCallback(
    (text) => {
      const trimmed = text.trim();
      if (!trimmed || isSendingRef.current) return;

      isSendingRef.current = true;
      currentTranscriptRef.current = '';

      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
        silenceTimeoutRef.current = null;
      }

      pulseAudioLevel(false);

      if (onAutoSend) {
        onAutoSend(trimmed);
      }

      setTimeout(() => {
        isSendingRef.current = false;
      }, 500);
    },
    [onAutoSend]
  );

  // Core Speech Recognition Engine
  const startListening = useCallback(() => {
    if (isSpeakingRef.current) return;

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    userWantsListeningRef.current = true;
    setPermissionError(null);

    if (isRunningRef.current && recognitionRef.current) {
      return; // already listening
    }

    try {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        isRunningRef.current = true;
        setIsListening(true);
        setPermissionError(null);
      };

      recognition.onaudiostart = () => {
        pulseAudioLevel(true);
      };

      recognition.onsoundstart = () => {
        pulseAudioLevel(true);
      };

      recognition.onspeechstart = () => {
        pulseAudioLevel(true);
      };

      recognition.onspeechend = () => {
        pulseAudioLevel(false);
      };

      recognition.onresult = (event) => {
        if (isSpeakingRef.current) return;

        let interimText = '';
        let hasFinal = false;
        let finalChunk = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const item = event.results[i];
          if (item.isFinal) {
            hasFinal = true;
            finalChunk += item[0].transcript + ' ';
          } else {
            interimText += item[0].transcript;
          }
        }

        const rawSpoken = (finalChunk || interimText).trim();
        if (!rawSpoken) return;

        pulseAudioLevel(true);

        // Check if wake word ("hello friday", "friday") was said
        const wakeWordRegex = /^(?:hey|hello|hi|ok|okay)?\s*(?:friday|jarvis)\b[,:\s]*/i;
        let cleanText = rawSpoken;
        if (wakeWordRegex.test(rawSpoken)) {
          playActivationPing();
          cleanText = rawSpoken.replace(wakeWordRegex, '').trim();
        }

        // Live stream text into input bar
        currentTranscriptRef.current = cleanText || rawSpoken;
        window.dispatchEvent(
          new CustomEvent('speech-interim-transcript', { detail: currentTranscriptRef.current })
        );

        if (silenceTimeoutRef.current) clearTimeout(silenceTimeoutRef.current);

        // 1.2s silence detection or final token -> auto send!
        if (hasFinal) {
          silenceTimeoutRef.current = setTimeout(() => {
            dispatchSpeech(currentTranscriptRef.current);
          }, 600);
        } else {
          silenceTimeoutRef.current = setTimeout(() => {
            dispatchSpeech(currentTranscriptRef.current);
          }, 1200);
        }
      };

      recognition.onerror = (e) => {
        console.warn('Speech recognition event:', e.error);
        if (e.error === 'not-allowed') {
          setPermissionError('Microphone blocked. Please click Allow in Chrome.');
          userWantsListeningRef.current = false;
          setIsListening(false);
          isRunningRef.current = false;
        } else if (e.error !== 'no-speech' && e.error !== 'aborted') {
          // ignore transient errors
        }
      };

      recognition.onend = () => {
        isRunningRef.current = false;
        setIsListening(false);
        pulseAudioLevel(false);

        // Restart listener by re-instantiating fresh SpeechRecognition instance
        if (userWantsListeningRef.current && !isSpeakingRef.current && !isSendingRef.current) {
          setTimeout(() => {
            if (userWantsListeningRef.current && !isSpeakingRef.current) {
              startListeningRef.current?.();
            }
          }, 250);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.warn('Recognition start exception:', err);
      isRunningRef.current = false;
      setIsListening(false);
    }
  }, [dispatchSpeech]);

  // Keep ref updated
  useEffect(() => {
    startListeningRef.current = startListening;
  }, [startListening]);

  const stopListening = useCallback(() => {
    userWantsListeningRef.current = false;
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {}
    }
    isRunningRef.current = false;
    setIsListening(false);
    pulseAudioLevel(false);
  }, []);

  // Text-To-Speech (TTS)
  const speak = useCallback(
    (text, onComplete) => {
      if (!window.speechSynthesis) {
        if (onComplete) onComplete();
        return;
      }

      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      if (safetyTtsTimeoutRef.current) clearTimeout(safetyTtsTimeoutRef.current);

      // Temporarily pause speech recognition while speaking
      isSpeakingRef.current = true;
      setIsSpeaking(true);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }

      const cleaned = cleanSpeechText(text);
      if (!cleaned) {
        isSpeakingRef.current = false;
        setIsSpeaking(false);
        if (onComplete) onComplete();
        if (userWantsListeningRef.current) setTimeout(startListening, 300);
        return;
      }

      // Natural concise sentences
      const sentences = cleaned.split(/(?<=[.!?])\s+/);
      const speechText = sentences.slice(0, 3).join(' ');

      const utterance = new SpeechSynthesisUtterance(speechText);
      utterance.rate = 1.05;
      utterance.pitch = 1.02;

      // Select natural English voice
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice =
        voices.find(
          (v) =>
            (v.name.includes('Zira') ||
              v.name.includes('Google UK English Female') ||
              v.name.includes('Samantha') ||
              v.name.includes('Natural') ||
              v.name.includes('Female')) &&
            v.lang.startsWith('en')
        ) ||
        voices.find((v) => v.lang.startsWith('en')) ||
        voices[0];

      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }

      const finishSpeech = () => {
        if (safetyTtsTimeoutRef.current) {
          clearTimeout(safetyTtsTimeoutRef.current);
          safetyTtsTimeoutRef.current = null;
        }
        isSpeakingRef.current = false;
        setIsSpeaking(false);
        if (onComplete) onComplete();

        // Re-arm listener after speaking if user wants continuous listening
        if (userWantsListeningRef.current) {
          setTimeout(() => {
            startListening();
          }, 350);
        }
      };

      utterance.onend = finishSpeech;
      utterance.onerror = finishSpeech;

      // Chrome garbage-collection bug fix: pin utterance to window
      window._activeSpeechUtterance = utterance;

      // Resume speech synthesis engine in case Chrome paused it
      try {
        window.speechSynthesis.resume();
      } catch (e) {}

      window.speechSynthesis.speak(utterance);

      // Safety timeout
      const safetyMs = Math.max(4000, speechText.length * 85);
      safetyTtsTimeoutRef.current = setTimeout(finishSpeech, safetyMs);
    },
    [cleanSpeechText, startListening]
  );

  const stopSpeaking = useCallback(() => {
    if (safetyTtsTimeoutRef.current) {
      clearTimeout(safetyTtsTimeoutRef.current);
      safetyTtsTimeoutRef.current = null;
    }
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    isSpeakingRef.current = false;
    setIsSpeaking(false);
    if (userWantsListeningRef.current) {
      setTimeout(startListening, 200);
    }
  }, [startListening]);

  // Manual Microphone Toggle (Explicit User Gesture)
  const toggleManualMic = useCallback(() => {
    if (isSpeakingRef.current) {
      stopSpeaking();
    }

    if (isListening) {
      stopListening();
    } else {
      playActivationPing();
      currentTranscriptRef.current = '';
      window.dispatchEvent(new CustomEvent('speech-interim-transcript', { detail: '' }));
      startListening();
    }
  }, [isListening, startListening, stopListening, stopSpeaking]);

  // Clean up
  useEffect(() => {
    return () => {
      stopListening();
      if (safetyTtsTimeoutRef.current) clearTimeout(safetyTtsTimeoutRef.current);
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    };
  }, [stopListening]);

  return {
    isListening,
    isSpeaking,
    audioLevel,
    permissionError,
    speechSupported,
    toggleManualMic,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  };
}
