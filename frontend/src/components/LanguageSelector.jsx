const LANGUAGES = [
  { code: "en", name: "English",  flag: "🇺🇸" },
  { code: "hi", name: "Hindi",    flag: "🇮🇳" },
  { code: "kn", name: "Kannada",  flag: "🌟" },
  { code: "ta", name: "Tamil",    flag: "🌺" },
  { code: "te", name: "Telugu",   flag: "🌸" },
  { code: "bn", name: "Bengali",  flag: "🌼" },
];

export default function LanguageSelector({ selected, onChange }) {
  return (
    <div style={styles.wrapper}>
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => onChange(lang.code)}
          style={{
            ...styles.btn,
            ...(selected === lang.code ? styles.active : {}),
          }}
        >
          <span>{lang.flag}</span>
          <span>{lang.name}</span>
        </button>
      ))}
    </div>
  );
}

const styles = {
  wrapper: {
    display: "flex",
    gap: "8px",
    flexWrap: "wrap",
    justifyContent: "center",
    padding: "12px 0",
  },
  btn: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    padding: "6px 14px",
    borderRadius: "20px",
    border: "1.5px solid #334155",
    background: "transparent",
    color: "#94a3b8",
    fontSize: "13px",
    cursor: "pointer",
    transition: "all 0.2s",
    fontFamily: "inherit",
  },
  active: {
    background: "#6366f1",
    borderColor: "#6366f1",
    color: "#ffffff",
    fontWeight: "600",
  },
};
