import { useEffect, useRef } from "react";

export default function ChatUI({ messages }) {
  const bottomRef = useRef(null);

  // Auto scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div style={styles.empty}>
        <div style={styles.emptyIcon}>📱</div>
        <p style={styles.emptyText}>Start a conversation!</p>
        <p style={styles.emptyHint}>
          Type a message or tap the mic button to speak in your language
        </p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {messages.map((msg, i) => (
        <div
          key={i}
          style={{
            ...styles.row,
            justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
          }}
        >
          {msg.role === "bot" && (
            <div style={styles.avatar}>🤖</div>
          )}

          <div
            style={{
              ...styles.bubble,
              ...(msg.role === "user" ? styles.userBubble : styles.botBubble),
            }}
          >
            {/* Main message text */}
            <p style={styles.text}>{msg.text}</p>

            {/* Bot extra info */}
            {msg.role === "bot" && msg.intent && (
              <div style={styles.meta}>
                <span style={styles.tag}>
                  🎯 {msg.intent}
                </span>
                <span style={styles.tag}>
                  📊 {msg.confidence}%
                </span>
                {msg.language && (
                  <span style={styles.tag}>
                    🌐 {msg.language}
                  </span>
                )}
              </div>
            )}
          </div>

          {msg.role === "user" && (
            <div style={styles.avatar}>👤</div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    padding: "16px",
    overflowY: "auto",
    flex: 1,
  },
  row: {
    display: "flex",
    alignItems: "flex-end",
    gap: "8px",
  },
  avatar: {
    fontSize: "22px",
    flexShrink: 0,
  },
  bubble: {
    maxWidth: "70%",
    padding: "12px 16px",
    borderRadius: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  userBubble: {
    background: "#6366f1",
    borderBottomRightRadius: "4px",
  },
  botBubble: {
    background: "#1e293b",
    borderBottomLeftRadius: "4px",
    border: "1px solid #334155",
  },
  text: {
    margin: 0,
    fontSize: "14px",
    lineHeight: "1.5",
    color: "#f1f5f9",
  },
  meta: {
    display: "flex",
    gap: "6px",
    flexWrap: "wrap",
  },
  tag: {
    fontSize: "11px",
    background: "#0f172a",
    color: "#64748b",
    padding: "2px 8px",
    borderRadius: "10px",
    border: "1px solid #1e293b",
  },
  empty: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "12px",
    padding: "40px",
  },
  emptyIcon: {
    fontSize: "48px",
  },
  emptyText: {
    fontSize: "18px",
    fontWeight: "600",
    color: "#e2e8f0",
    margin: 0,
  },
  emptyHint: {
    fontSize: "13px",
    color: "#64748b",
    textAlign: "center",
    margin: 0,
    maxWidth: "280px",
    lineHeight: "1.6",
  },
};
