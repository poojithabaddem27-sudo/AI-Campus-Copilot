import json
import streamlit as st
import streamlit.components.v1 as components

def render_inside_input_mic_button():
    """
    Renders a DOM-level Microphone injector script that attaches a clickable 🎤 microphone button
    DIRECTLY INSIDE Streamlit's st.chat_input box:
    [ Ask about floor plans, rooms, routes...          🎤  ➤ ]

    Features:
    - Compatible with Google Chrome and Microsoft Edge (Web Speech API).
    - Asks for browser microphone permission normally.
    - Shows "🎤 Listening... Speak now" visual badge when active.
    - Accurately inserts recognized speech into the React-controlled chat input field.
    - Automatically triggers submission to the existing Gemini AI Assistant.
    - Handles permission denial gracefully.
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
            function setReactInputValue(inputElem, val) {
                try {
                    const proto = window.parent.HTMLTextAreaElement.prototype;
                    const descriptor = Object.getOwnPropertyDescriptor(proto, 'value');
                    if (descriptor && descriptor.set) {
                        descriptor.set.call(inputElem, val);
                    } else {
                        inputElem.value = val;
                    }
                    inputElem.dispatchEvent(new window.parent.Event('input', { bubbles: true }));
                    inputElem.dispatchEvent(new window.parent.Event('change', { bubbles: true }));
                } catch(e) {
                    inputElem.value = val;
                }
            }

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

                    // Create Floating Status Badge: "🎤 Listening... Speak now"
                    let statusBadge = parentDoc.getElementById('voice-status-badge');
                    if (!statusBadge) {
                        statusBadge = parentDoc.createElement('div');
                        statusBadge.id = 'voice-status-badge';
                        statusBadge.style.position = 'absolute';
                        statusBadge.style.top = '-36px';
                        statusBadge.style.left = '12px';
                        statusBadge.style.background = 'linear-gradient(135deg, #EF4444, #DC2626)';
                        statusBadge.style.color = '#FFFFFF';
                        statusBadge.style.padding = '5px 14px';
                        statusBadge.style.borderRadius = '20px';
                        statusBadge.style.fontSize = '12px';
                        statusBadge.style.fontWeight = '700';
                        statusBadge.style.boxShadow = '0 4px 14px rgba(239, 68, 68, 0.4)';
                        statusBadge.style.zIndex = '999';
                        statusBadge.style.display = 'none';
                        statusBadge.style.alignItems = 'center';
                        statusBadge.style.gap = '6px';
                        statusBadge.innerHTML = '🎤 Listening... Speak now';
                        chatContainer.appendChild(statusBadge);
                    }

                    const micBtn = parentDoc.createElement('button');
                    micBtn.id = 'attached-chat-mic';
                    micBtn.type = 'button';
                    micBtn.title = 'Click 🎤 to speak your question';
                    micBtn.innerHTML = '🎤';
                    
                    // Style microphone button inside input container right before Send (➤)
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

                    // Setup Web Speech Recognition
                    const SpeechRec = window.parent.SpeechRecognition ||
                                      window.parent.webkitSpeechRecognition ||
                                      window.SpeechRecognition ||
                                      window.webkitSpeechRecognition;

                    if (SpeechRec) {
                        const recognition = new SpeechRec();
                        recognition.continuous = false;
                        recognition.interimResults = true;
                        recognition.lang = 'en-US';

                        let isListening = false;
                        let recognizedText = '';

                        recognition.onstart = function() {
                            isListening = true;
                            recognizedText = '';
                            micBtn.style.background = 'rgba(239, 68, 68, 0.25)';
                            micBtn.style.borderColor = '#EF4444';
                            micBtn.style.color = '#F87171';
                            micBtn.innerHTML = '🔴';
                            micBtn.title = '🎤 Listening... Speak now';
                            if (statusBadge) statusBadge.style.display = 'flex';
                        };

                        recognition.onresult = function(e) {
                            let interimTranscript = '';
                            let finalTranscript = '';
                            for (let i = e.resultIndex; i < e.results.length; ++i) {
                                if (e.results[i].isFinal) {
                                    finalTranscript += e.results[i][0].transcript;
                                } else {
                                    interimTranscript += e.results[i][0].transcript;
                                }
                            }
                            recognizedText = (finalTranscript || interimTranscript).trim();
                            if (textarea && recognizedText) {
                                setReactInputValue(textarea, recognizedText);
                            }
                        };

                        recognition.onerror = function(e) {
                            isListening = false;
                            micBtn.style.background = 'rgba(56, 189, 248, 0.15)';
                            micBtn.style.borderColor = 'rgba(56, 189, 248, 0.3)';
                            micBtn.style.color = '#38BDF8';
                            micBtn.innerHTML = '🎤';
                            micBtn.title = 'Click 🎤 to speak your question';
                            if (statusBadge) statusBadge.style.display = 'none';

                            if (e.error === 'not-allowed' || e.error === 'permission-denied') {
                                alert("Microphone permission was denied. Please allow microphone access in your browser address bar.");
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
                            micBtn.title = 'Click 🎤 to speak your question';
                            if (statusBadge) statusBadge.style.display = 'none';

                            if (textarea && recognizedText && recognizedText.trim()) {
                                setReactInputValue(textarea, recognizedText.trim());
                                textarea.focus();

                                // Automatically trigger submission to existing Gemini AI assistant
                                setTimeout(function() {
                                    const submitBtn = chatContainer.querySelector('button[data-testid="stChatInputSubmitButton"]') ||
                                                      chatContainer.querySelector('button:not(#attached-chat-mic)');
                                    if (submitBtn && !submitBtn.disabled) {
                                        submitBtn.click();
                                    } else {
                                        const enterEvt = new window.parent.KeyboardEvent('keydown', {
                                            key: 'Enter',
                                            code: 'Enter',
                                            keyCode: 13,
                                            which: 13,
                                            bubbles: true,
                                            cancelable: true
                                        });
                                        textarea.dispatchEvent(enterEvt);
                                    }
                                }, 150);
                            }
                        };

                        micBtn.onclick = function() {
                            if (isListening) {
                                recognition.stop();
                            } else {
                                recognizedText = '';
                                recognition.start();
                            }
                        };
                    } else {
                        micBtn.onclick = function() {
                            alert("Voice input is not supported in this browser. Please use Chrome or Edge, or type your question.");
                        };
                    }
                } catch(err) {
                    console.error("Error attaching mic button:", err);
                }
            }

            // Run attachment polling
            setInterval(attachMicToChatInput, 350);
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
