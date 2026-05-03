import { useState, useRef } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function MicButton({ language, onResult, onLoading }) {
  const [recording, setRecording] = useState(false);
  const [seconds,   setSeconds]   = useState(0);
  const mediaRef    = useRef(null);
  const chunksRef   = useRef([]);
  const timerRef    = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/wav" });
        stream.getTracks().forEach((t) => t.stop());
        await sendAudio(blob);
      };

      mediaRef.current = recorder;
      recorder.start();
      setRecording(true);
      setSeconds(0);

      // Count up timer
      timerRef.current = setInterval(() => {
        setSeconds((s) => s + 1);
      }, 1000);

      // Auto stop after 7 seconds
      setTimeout(() => stopRecording(), 7000);
    } catch (err) {
      alert("Microphone access denied. Please allow microphone access.");
    }
  };

  const stopRecording = () => {
    if (mediaRef.current && mediaRef.current.state === "recording") {
      mediaRef.current.stop();
    }
    clearInterval(timerRef.current);
    setRecording(false);
    setSeconds(0);
  };

  const sendAudio = async (blob) => {
    onLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", blob, "recording.wav");
      formData.append("language", language);

      const res = await axios.post(`${API}/chat/voice`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      onResult(res.data);

      // Play audio response
      const audioRes = await fetch(`${API}/audio/response`);
      const audioBlob = await audioRes.blob();
      const audioUrl  = URL.createObjectURL(audioBlob);
      const audio     = new Audio(audioUrl);
      audio.play();

    } catch (err) {
      console.error(err);
      onResult({ error: "Something went wrong. Is the backend running?" });
    } finally {
      onLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <button
        onClick={recording ? stopRecording : startRecording}
        style={{ ...styles.btn, ...(recording ? styles.recording : {}) }}
      >
        {recording ? (
          <>
            <span style={styles.dot} />
            <span>Recording... {seconds}s (tap to stop)</span>
          </>
        ) : (
          <>
            <span style={{ fontSize: "20px" }}>🎙️</span>
            <span>Hold to Speak</span>
          </>
        )}
      </button>
      {recording && (
        <p style={styles.hint}>Speak clearly • Auto-stops at 7 seconds</p>
      )}
    </div>
  );
}

const styles = {
  wrapper: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "8px",
  },
  btn: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "14px 28px",
    borderRadius: "50px",
    border: "none",
    background: "#6366f1",
    color: "#fff",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.2s",
    fontFamily: "inherit",
    boxShadow: "0 4px 20px rgba(99,102,241,0.4)",
  },
  recording: {
    background: "#ef4444",
    boxShadow: "0 4px 20px rgba(239,68,68,0.4)",
    animation: "pulse 1s infinite",
  },
  dot: {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    background: "#fff",
    display: "inline-block",
    animation: "pulse 1s infinite",
  },
  hint: {
    fontSize: "12px",
    color: "#64748b",
    margin: 0,
  },
};
