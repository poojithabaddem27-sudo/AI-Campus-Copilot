import json
import streamlit as st
import streamlit.components.v1 as components

def render_inside_input_mic_button():
    """
    Renders a DOM-level Microphone injector script that attaches a clickable 🎤 microphone button
    DIRECTLY INSIDE Streamlit's st.chat_input box:
    [ Ask about floor plans, rooms, routes...          🎤  ➤ ]

    Behavior:
    - Zero separate Voice Assistant section or transcript boxes.
    - Zero default "Processing AI answer..." on page load.
    - Click 🎤 -> Listening (🔴) -> Transcribes speech into input field -> Auto-submits ONCE to existing AI assistant.
    - Graceful fallback for permission denied or unsupported browsers.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; padding: 0; background: transparent; }
        </style>
    </head>
    <body>
        <script>
            function attachMicToChatInput() {
                try {
                    const parentDoc = window.parent.document;
                    const chatContainer = parentDoc.querySelector('div[data-testid="stChatInput"]');
                    if (!chatContainer || parentDoc.getElementById('attached-chat-mic')) return;

                    chatContainer.style.position = 'relative';
                    const textarea = chatContainer.querySelector('textarea');
                    if (textarea) {
                        textarea.style.paddingRight = '82px';
                    }

                    const micBtn = parentDoc.createElement('button');
                    micBtn.id = 'attached-chat-mic';
                    micBtn.type = 'button';
                    micBtn.title = 'Click 🎤 to speak your question';
                    micBtn.innerHTML = '🎤';
                    
                    // Style microphone button directly inside the input container right before Send button (➤)
                    micBtn.style.position = 'absolute';
                    micBtn.style.right = '48px';
                    micBtn.style.bottom = '8px';
                    micBtn.style.zIndex = '99';
                    micBtn.style.background = 'rgba(56, 189, 248, 0.15)';
                    micBtn.style.border = '1px solid rgba(56, 189, 248, 0.3)';
                    micBtn.style.color = '#38BDF8';
                    micBtn.style.fontSize = '15px';
                    micBtn.style.cursor = 'pointer';
                    micBtn.style.width = '32px';
                    micBtn.style.height = '32px';
                    micBtn.style.borderRadius = '50%';
                    micBtn.style.display = 'flex';
                    micBtn.style.alignItems = 'center';
                    micBtn.style.justifyContent = 'center';
                    micBtn.style.transition = 'all 0.2s ease-in-out';

                    micBtn.onmouseover = function() {
                        micBtn.style.transform = 'scale(1.1)';
                        micBtn.style.background = 'rgba(56, 189, 248, 0.3)';
                    };
                    micBtn.onmouseout = function() {
                        micBtn.style.transform = 'scale(1)';
                        micBtn.style.background = 'rgba(56, 189, 248, 0.15)';
                    };

                    chatContainer.appendChild(micBtn);

                    // Setup Speech Recognition
                    let recognition = null;
                    let isListening = false;
                    let finalSpeech = "";
                    let isSubmitting = false;

                    if ('SpeechRecognition' in window.parent || 'webkitSpeechRecognition' in window.parent) {
                        const SpeechRecognition = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
                        recognition = new SpeechRecognition();
                        recognition.continuous = false;
                        recognition.interimResults = true;
                        recognition.lang = 'en-US';

                        recognition.onstart = function() {
                            isListening = true;
                            isSubmitting = false;
                            micBtn.style.background = 'rgba(239, 68, 68, 0.25)';
                            micBtn.style.borderColor = '#EF4444';
                            micBtn.style.color = '#F87171';
                            micBtn.innerHTML = '🔴';
                            micBtn.title = 'Listening... Speak now';
                        };

                        recognition.onresult = function(e) {
                            let interim = '';
                            for (let i = e.resultIndex; i < e.results.length; ++i) {
                                if (e.results[i].isFinal) {
                                    finalSpeech += e.results[i][0].transcript;
                                } else {
                                    interim += e.results[i][0].transcript;
                                }
                            }
                            let currentText = finalSpeech || interim;
                            if (textarea && currentText) {
                                textarea.value = currentText;
                                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        };

                        recognition.onerror = function(e) {
                            isListening = false;
                            micBtn.style.background = 'rgba(56, 189, 248, 0.15)';
                            micBtn.style.borderColor = 'rgba(56, 189, 248, 0.3)';
                            micBtn.style.color = '#38BDF8';
                            micBtn.innerHTML = '🎤';

                            if (e.error === 'not-allowed' || e.error === 'permission-denied') {
                                alert("Microphone access blocked. Please grant microphone permission in your browser address bar.");
                            } else if (e.error !== 'no-speech') {
                                console.warn("Speech recognition error:", e.error);
                            }
                        };

                        recognition.onend = function() {
                            isListening = false;
                            micBtn.style.background = 'rgba(56, 189, 248, 0.15)';
                            micBtn.style.borderColor = 'rgba(56, 189, 248, 0.3)';
                            micBtn.style.color = '#38BDF8';
                            micBtn.innerHTML = '🎤';

                            if (finalSpeech && finalSpeech.trim() && !isSubmitting) {
                                isSubmitting = true;
                                const textToSubmit = finalSpeech.trim();
                                finalSpeech = "";

                                // Submit ONCE to parent window URL parameter for Streamlit execution
                                try {
                                    const parentUrl = new URL(window.parent.location.href);
                                    parentUrl.searchParams.set("vq", textToSubmit);
                                    window.parent.location.href = parentUrl.href;
                                } catch(err) {
                                    console.error("Auto submission error:", err);
                                }
                            }
                        };

                        micBtn.onclick = function() {
                            if (isListening) {
                                recognition.stop();
                            } else {
                                finalSpeech = "";
                                isSubmitting = false;
                                recognition.start();
                            }
                        };
                    } else {
                        micBtn.onclick = function() {
                            alert("Voice input is not supported in this browser. Please use Chrome, Edge, or Safari.");
                        };
                    }
                } catch(err) {
                    console.error("Error attaching mic button:", err);
                }
            }

            // Run attachment polling
            setInterval(attachMicToChatInput, 400);
        </script>
    </body>
    </html>
    """

def render_speech_synthesis_player(text_to_speak, element_id="tts-player"):
    """
    Renders an HTML/JS Web SpeechSynthesis Text-to-Speech audio reader button.
    Allows user to click 🔊 Read Aloud to hear the AI response in a natural voice.
    """
    escaped_text = json.dumps(text_to_speak)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; background: transparent; font-family: sans-serif; }}
            .tts-btn {{
                background: rgba(56, 189, 248, 0.12);
                color: #38BDF8;
                border: 1px solid rgba(56, 189, 248, 0.3);
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s;
            }}
            .tts-btn:hover {{
                background: rgba(56, 189, 248, 0.25);
                border-color: #38BDF8;
            }}
            .tts-btn.speaking {{
                background: rgba(239, 68, 68, 0.15);
                color: #F87171;
                border-color: rgba(239, 68, 68, 0.4);
                animation: tts-glow 1s infinite alternate;
            }}
            @keyframes tts-glow {{
                from {{ opacity: 0.8; }}
                to {{ opacity: 1.0; }}
            }}
        </style>
    </head>
    <body>
        <button id="{element_id}" class="tts-btn" onclick="speakText()">
            <span>🔊 Read Aloud</span>
        </button>

        <script>
            const textToSpeak = {escaped_text};

            function speakText() {{
                if (!('speechSynthesis' in window)) {{
                    alert("Text-to-Speech is not supported in this browser.");
                    return;
                }}

                if (window.speechSynthesis.speaking) {{
                    window.speechSynthesis.cancel();
                    document.getElementById("{element_id}").className = "tts-btn";
                    document.getElementById("{element_id}").innerHTML = "<span>🔊 Read Aloud</span>";
                    return;
                }}

                const cleanText = textToSpeak.replace(/[*_#`~]/g, '');
                const utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;

                utterance.onstart = function() {{
                    document.getElementById("{element_id}").className = "tts-btn speaking";
                    document.getElementById("{element_id}").innerHTML = "<span>⏹️ Stop Speaking</span>";
                }};

                utterance.onend = function() {{
                    document.getElementById("{element_id}").className = "tts-btn";
                    document.getElementById("{element_id}").innerHTML = "<span>🔊 Read Aloud</span>";
                }};

                utterance.onerror = function(e) {{
                    console.error("TTS Error:", e);
                    document.getElementById("{element_id}").className = "tts-btn";
                    document.getElementById("{element_id}").innerHTML = "<span>🔊 Read Aloud</span>";
                }};

                window.speechSynthesis.speak(utterance);
            }}
        </script>
    </body>
    </html>
    """
