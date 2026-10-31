import streamlit as st
import streamlit.components.v1 as components

def render_vad_microphone(backend_url: str = "http://127.0.0.1:8000", silence_timeout_ms: int = 2000, volume_threshold: int = 15, height: int = 90):
    """
    Renders an interactive Voice Activity Detection (VAD) microphone component.
    Uses Chrome's native SpeechRecognition (with Gemini WebM backend fallback)
    and Web Audio API AnalyserNode for volume monitoring and automatic silence auto-stop.
    Dispatches directly into Streamlit's chat input.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Rajdhani:wght@600;700&display=swap');
        
        * {{
          box-sizing: border-box;
          margin: 0;
          padding: 0;
          font-family: 'Rajdhani', sans-serif;
          user-select: none;
        }}

        body {{
          background: transparent;
          color: #e2f1ff;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          overflow: hidden;
        }}

        .vad-card {{
          width: 100%;
          background: linear-gradient(135deg, rgba(5, 12, 28, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%);
          border: 1px solid rgba(0, 240, 255, 0.35);
          border-left: 4px solid #00f0ff;
          border-radius: 8px;
          padding: 10px 18px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7), inset 0 0 15px rgba(0, 240, 255, 0.05);
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
        }}

        .vad-left {{
          display: flex;
          align-items: center;
          gap: 14px;
        }}

        .vad-btn {{
          background: linear-gradient(180deg, #091a38 0%, #050d1e 100%);
          color: #00f0ff;
          border: 1px solid #00f0ff;
          border-radius: 50%;
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.25s ease;
          box-shadow: 0 0 12px rgba(0, 240, 255, 0.25);
          outline: none;
          flex-shrink: 0;
        }}

        .vad-btn:hover {{
          background: rgba(0, 240, 255, 0.2);
          box-shadow: 0 0 20px #00f0ff;
          transform: scale(1.05);
        }}

        .vad-btn.active {{
          background: #ff3366;
          color: #fff;
          border-color: #ff3366;
          box-shadow: 0 0 25px rgba(255, 51, 102, 0.6);
          animation: pulseRed 1.4s infinite;
        }}

        @keyframes pulseRed {{
          0% {{ transform: scale(1); }}
          50% {{ transform: scale(1.06); }}
          100% {{ transform: scale(1); }}
        }}

        .vad-details {{
          display: flex;
          flex-direction: column;
        }}

        .vad-title {{
          font-family: 'Orbitron', monospace;
          font-size: 13px;
          font-weight: 800;
          letter-spacing: 1.5px;
          color: #00f0ff;
          text-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
        }}

        .vad-status {{
          font-size: 13px;
          font-weight: 600;
          color: #8ab4f8;
          margin-top: 2px;
        }}

        .vad-status.speaking {{
          color: #00ffaa;
          font-weight: 700;
          text-shadow: 0 0 6px #00ffaa;
        }}

        .vad-status.silence {{
          color: #ffb400;
          font-weight: 700;
        }}

        /* Real-time Visualizer VU-Meter */
        .meter-container {{
          display: flex;
          align-items: center;
          gap: 3px;
          height: 32px;
          background: rgba(0, 0, 0, 0.5);
          padding: 4px 10px;
          border-radius: 4px;
          border: 1px solid rgba(0, 240, 255, 0.2);
          min-width: 140px;
          justify-content: center;
        }}

        .meter-bar {{
          width: 4px;
          height: 6px;
          background: rgba(0, 240, 255, 0.25);
          border-radius: 2px;
          transition: height 0.08s ease, background 0.08s ease;
        }}

        .meter-bar.active {{
          background: #00f0ff;
          box-shadow: 0 0 6px #00f0ff;
        }}

        .meter-bar.hot {{
          background: #00ffaa;
          box-shadow: 0 0 8px #00ffaa;
        }}
      </style>
    </head>
    <body>
      <div class="vad-card">
        <div class="vad-left">
          <button class="vad-btn" id="vad-toggle-btn" onclick="toggleVAD()" title="Click to start auto-listening">
            <svg id="mic-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </button>

          <div class="vad-details">
            <div class="vad-title">VOICE ACTIVITY DETECTION (VAD)</div>
            <div class="vad-status" id="vad-status-text">Click mic to start auto-listening...</div>
          </div>
        </div>

        <!-- Audio Volume Visualizer -->
        <div class="meter-container" id="meter-container">
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
          <div class="meter-bar"></div>
        </div>
      </div>

      <script>
        // Configuration Parameters
        const SILENCE_THRESHOLD = {volume_threshold}; // Volume level threshold (0 - 255)
        const SILENCE_TIMEOUT = {silence_timeout_ms}; // Duration of silence before auto-stop (ms)
        const BACKEND_URL = "{backend_url}";

        let isRecording = false;
        let audioContext = null;
        let analyserNode = null;
        let mediaStream = null;
        let mediaRecorder = null;
        let audioChunks = [];
        let animationFrameId = null;
        let recognition = null;
        let liveTranscript = "";

        // VAD State Tracking
        let hasSpoken = false;
        let silenceStartTime = null;

        const btn = document.getElementById("vad-toggle-btn");
        const statusText = document.getElementById("vad-status-text");
        const meterBars = document.querySelectorAll(".meter-bar");

        async function toggleVAD() {{
          if (isRecording) {{
            stopRecording(false);
          }} else {{
            startRecording();
          }}
        }}

        async function startRecording() {{
          try {{
            liveTranscript = "";
            hasSpoken = false;
            silenceStartTime = null;

            // 1. Initialize Chrome native SpeechRecognition for instant, real-time accuracy
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRec) {{
              try {{
                recognition = new SpeechRec();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = "en-US";
                recognition.onresult = (event) => {{
                  let interim = "";
                  for (let i = 0; i < event.results.length; ++i) {{
                    interim += event.results[i][0].transcript;
                  }}
                  if (interim.trim()) {{
                    liveTranscript = interim.trim();
                    hasSpoken = true;
                    silenceStartTime = null;
                    statusText.className = "vad-status speaking";
                    statusText.innerText = `Recognized: "${{liveTranscript}}"`;
                  }}
                }};
                recognition.onerror = (err) => console.log("SpeechRecognition error:", err);
                recognition.start();
              }} catch (recErr) {{
                console.log("Speech recognition start issue:", recErr);
              }}
            }}

            // 2. Request microphone stream for volume analysis
            mediaStream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            
            // Set up Web Audio API AnalyserNode
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const sourceNode = audioContext.createMediaStreamSource(mediaStream);
            
            analyserNode = audioContext.createAnalyser();
            analyserNode.fftSize = 256;
            analyserNode.smoothingTimeConstant = 0.5;
            sourceNode.connect(analyserNode);

            // Set up MediaRecorder as fallback audio capture
            mediaRecorder = new MediaRecorder(mediaStream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {{
              if (event.data.size > 0) {{
                audioChunks.push(event.data);
              }}
            }};

            mediaRecorder.onstop = handleRecordingStopped;

            mediaRecorder.start(250);
            isRecording = true;

            btn.classList.add("active");
            statusText.className = "vad-status";
            statusText.innerText = "Listening... Speak your directive, Boss";

            // Start continuous volume analysis loop
            monitorAudioVolume();
          }} catch (err) {{
            console.error("Microphone Access Error:", err);
            statusText.innerText = "Error: Microphone permission denied in browser.";
          }}
        }}

        function monitorAudioVolume() {{
          if (!isRecording || !analyserNode) return;

          const bufferLength = analyserNode.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);
          analyserNode.getByteFrequencyData(dataArray);

          // Calculate Average Volume / Decibel Level
          let sum = 0;
          for (let i = 0; i < bufferLength; i++) {{
            sum += dataArray[i];
          }}
          const avgVolume = sum / bufferLength;

          // Update VU-Meter Bars
          updateVisualizer(avgVolume);

          // Voice Activity & Silence Detection Logic
          const currentTime = Date.now();

          if (avgVolume > SILENCE_THRESHOLD) {{
            // USER IS SPEAKING
            hasSpoken = true;
            silenceStartTime = null; // Reset silence timer
            if (!liveTranscript) {{
              statusText.className = "vad-status speaking";
              statusText.innerText = `Speaking detected (Volume: ${{Math.round(avgVolume)}})`;
            }}
          }} else {{
            // USER IS QUIET / SILENCE
            if (hasSpoken) {{
              if (!silenceStartTime) {{
                silenceStartTime = currentTime; // Start silence timer
              }}

              const elapsedSilence = currentTime - silenceStartTime;
              const remainingSec = Math.max(0, (SILENCE_TIMEOUT - elapsedSilence) / 1000).toFixed(1);

              statusText.className = "vad-status silence";
              statusText.innerText = `Silence detected... Auto-stopping in ${{remainingSec}}s`;

              if (elapsedSilence >= SILENCE_TIMEOUT) {{
                // SILENCE TIMEOUT REACHED -> AUTO-STOP RECORDING!
                console.log("Silence timeout reached. Auto-stopping recording...");
                statusText.className = "vad-status";
                statusText.innerText = "Auto-stopped! Processing directive...";
                stopRecording(true);
                return;
              }}
            }}
          }}

          animationFrameId = requestAnimationFrame(monitorAudioVolume);
        }}

        function updateVisualizer(volume) {{
          const normalized = Math.min(1.0, volume / 60);
          const activeBars = Math.round(normalized * meterBars.length);

          meterBars.forEach((bar, index) => {{
            if (index < activeBars) {{
              const height = Math.min(26, Math.max(6, (index + 1) * 3));
              bar.style.height = `${{height}}px`;
              bar.className = index > 8 ? "meter-bar hot" : "meter-bar active";
            }} else {{
              bar.style.height = "6px";
              bar.className = "meter-bar";
            }}
          }});
        }}

        function stopRecording(isAutoStopped = false) {{
          if (!isRecording) return;
          isRecording = false;

          if (animationFrameId) {{
            cancelAnimationFrame(animationFrameId);
          }}

          if (recognition) {{
            try {{ recognition.stop(); }} catch(e) {{}}
          }}

          if (mediaRecorder && mediaRecorder.state !== "inactive") {{
            mediaRecorder.stop();
          }}

          if (mediaStream) {{
            mediaStream.getTracks().forEach(track => track.stop());
          }}

          if (audioContext && audioContext.state !== "closed") {{
            audioContext.close();
          }}

          btn.classList.remove("active");
          resetVisualizer();

          if (!isAutoStopped) {{
            statusText.innerText = "Stopped manually. Processing...";
          }}
        }}

        function resetVisualizer() {{
          meterBars.forEach(bar => {{
            bar.style.height = "6px";
            bar.className = "meter-bar";
          }});
        }}

        async function handleRecordingStopped() {{
          let spokenText = liveTranscript.trim();

          // If browser speech recognizer didn't capture text, fallback to backend Gemini transcription
          if (!spokenText && audioChunks.length > 0) {{
            statusText.innerText = "Transcribing speech via F.R.I.D.A.Y. neural core...";
            const audioBlob = new Blob(audioChunks, {{ type: "audio/webm" }});
            const base64Data = await new Promise((resolve) => {{
              const reader = new FileReader();
              reader.onloadend = () => resolve(reader.result);
              reader.readAsDataURL(audioBlob);
            }});

            try {{
              const res = await fetch(`${{BACKEND_URL}}/api/audio/transcribe`, {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ audio_base64: base64Data }})
              }});

              if (res.ok) {{
                const data = await res.json();
                spokenText = data.text ? data.text.trim() : "";
              }}
            }} catch (err) {{
              console.error("Backend transcription failed:", err);
            }}
          }}

          if (spokenText) {{
            statusText.className = "vad-status speaking";
            statusText.innerText = `Dispatched: "${{spokenText}}"`;
            dispatchPromptToFriday(spokenText);
          }} else {{
            statusText.className = "vad-status";
            statusText.innerText = "Could not clearly detect speech. Click mic to speak again.";
          }}
        }}

        function dispatchPromptToFriday(text) {{
          let dispatched = false;

          // Strategy 1: Direct DOM injection into Streamlit chat input & trigger click
          try {{
            const pDoc = window.parent.document;
            const textarea = pDoc.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (textarea) {{
              const nativeSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value").set;
              nativeSetter.call(textarea, text);
              textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
              
              setTimeout(() => {{
                const submitBtn = pDoc.querySelector('button[data-testid="stChatInputSubmitButton"]');
                if (submitBtn) {{
                  submitBtn.click();
                  dispatched = true;
                }}
              }}, 150);
            }}
          }} catch(e) {{
            console.warn("Direct DOM submit failed:", e);
          }}

          // Strategy 2: Update parent location query param as reliable fallback
          setTimeout(() => {{
            if (!dispatched) {{
              try {{
                const url = new URL(window.parent.location.href);
                url.searchParams.set("voice", text);
                window.parent.location.href = url.toString();
              }} catch(e) {{
                console.error("Location param submit failed:", e);
              }}
            }}
          }}, 450);
        }}
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=False)
