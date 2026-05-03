import { useState } from "react";
import axios from "axios";
import ChatUI from "./components/ChatUI";
import MicButton from "./components/MicButton";
import LanguageSelector from "./components/LanguageSelector";

const API = "http://localhost:8000";

export default function App() {
  const [messages,  setMessages]  = useState([]);
  const [inputText, setInputText] = useState("");
  const [language,  setLanguage]  = useState("en");
  const [loading,   setLoading]   = useState(false);

  // ── Add message to chat ──────────────────────────────────
  const addMessage = (role, text, extras = {}) => {
    setMessages((prev) => [...prev, { role, text, ...extras }]);
  };

  // ── Send text message ────────────────────────────────────
  const sendText = async () => {
    const text = inputText.trim();
    if (!text) return;

    addMessage("user", text);
    setInputText("");
    setLoading(true);

    try {
      const res = await axios.post(`${API}/chat/text`, {
        text:     text,
        language: language,
      });

      const data = res.data;
      addMessage("bot", data.translated_response, {
        intent:     data.intent,
        confidence: data.confidence,
        language:   data.language_name,
      });

      // Play audio response
      try {
        const audioRes  = await fetch(`${API}/audio/response`);
        const audioBlob = await audioRes.blob();
        const audioUrl  = URL.createObjectURL(audioBlob);
        const audio     = new Audio(audioUrl);
        audio.play();
      } catch {
        // Audio failed silently — text response is still shown
      }

    } catch (err) {
      addMessage("bot", "Sorry, I couldn't connect to the server. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  // ── Handle voice result from MicButton ──────────────────
  const handleVoiceResult = (data) => {
    if (data.error) {
      addMessage("bot", data.error);
      return;
    }
    addMessage("user", `🎙️ ${data.input_text}`);
    addMessage("bot", data.translated_response, {
      intent:     data.intent,
      confidence: data.confidence,
      language:   data.language_name,
    });
  };

  // ── Enter key sends message ──────────────────────────────
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendText();
    }
  };

  return (
    <div style={styles.app}>

      {/* ── Header ── */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logo}>📡</div>
          <div>
            <h1 style={styles.title}>Telecom AI Bot</h1>
            <p style={styles.subtitle}>Multilingual Customer Support</p>
          </div>
        </div>
        <div style={styles.statusDot} title="Backend connected" />
      </div>

      {/* ── Language Selector ── */}
      <div style={styles.langBar}>
        <span style={styles.langLabel}>Language:</span>
        <LanguageSelector selected={language} onChange={setLanguage} />
      </div>

      {/* ── Chat Area ── */}
      <div style={styles.chatArea}>
        <ChatUI messages={messages} />
      </div>

      {/* ── Loading indicator ── */}
      {loading && (
        <div style={styles.loading}>
          <span style={styles.dot} />
          <span style={styles.dot} />
          <span style={styles.dot} />
        </div>
      )}

      {/* ── Input Bar ── */}
      <div style={styles.inputBar}>
        <MicButton
          language={language}
          onResult={handleVoiceResult}
          onLoading={setLoading}
        />

        <div style={styles.textInputRow}>
          <input
            style={styles.input}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Type in ${language === "en" ? "English" : language === "hi" ? "Hindi" : language === "kn" ? "Kannada" : language === "ta" ? "Tamil" : language === "te" ? "Telugu" : "Bengali"}...`}
            disabled={loading}
          />
          <button
            style={{ ...styles.sendBtn, opacity: loading ? 0.5 : 1 }}
            onClick={sendText}
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>

    </div>
  );
}

const styles = {
  app: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    background: "#0f172a",
    color: "#f1f5f9",
    fontFamily: "'Segoe UI', system-ui, sans-serif",
    maxWidth: "780px",
    margin: "0 auto",
    boxShadow: "0 0 60px rgba(0,0,0,0.5)",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 20px",
    background: "#1e293b",
    borderBottom: "1px solid #334155",
  },
  headerLeft: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  logo: {
    fontSize: "28px",
  },
  title: {
    margin: 0,
    fontSize: "18px",
    fontWeight: "700",
    color: "#f1f5f9",
  },
  subtitle: {
    margin: 0,
    fontSize: "12px",
    color: "#64748b",
  },
  statusDot: {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    background: "#22c55e",
    boxShadow: "0 0 8px #22c55e",
  },
  langBar: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 20px",
    background: "#1e293b",
    borderBottom: "1px solid #334155",
    flexWrap: "wrap",
  },
  langLabel: {
    fontSize: "12px",
    color: "#64748b",
    fontWeight: "500",
  },
  chatArea: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
  },
  loading: {
    display: "flex",
    gap: "6px",
    justifyContent: "center",
    padding: "8px",
  },
  dot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: "#6366f1",
    animation: "bounce 0.8s infinite alternate",
  },
  inputBar: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    padding: "16px 20px",
    background: "#1e293b",
    borderTop: "1px solid #334155",
  },
  textInputRow: {
    display: "flex",
    gap: "10px",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    borderRadius: "12px",
    border: "1.5px solid #334155",
    background: "#0f172a",
    color: "#f1f5f9",
    fontSize: "14px",
    outline: "none",
    fontFamily: "inherit",
  },
  sendBtn: {
    padding: "12px 24px",
    borderRadius: "12px",
    border: "none",
    background: "#6366f1",
    color: "#fff",
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    fontFamily: "inherit",
  },
};
