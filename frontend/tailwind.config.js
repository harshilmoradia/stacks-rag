/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12181F",
        "ink-raised": "#1B232C",
        parchment: "#EDE6D6",
        "parchment-dim": "#A9A296",
        signal: "#E8A33D",
        "signal-dim": "#8A6A38",
        circuit: "#4FB3A9",
        miss: "#D9634B",
        grid: "rgba(237, 230, 214, 0.08)",
      },
      fontFamily: {
        display: ["var(--font-display)", "sans-serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backgroundImage: {
        graticule:
          "linear-gradient(rgba(237,230,214,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(237,230,214,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        graticule: "24px 24px",
      },
    },
  },
  plugins: [],
};
