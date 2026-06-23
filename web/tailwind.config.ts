import type { Config } from "tailwindcss";

/**
 * ROBARK design system — monochrome (black + paper-white) with a single
 * "dog" accent (rust) used sparingly, CryptoPunk-discipline. Pixel-tech.
 */
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        robark: {
          black: "#0a0a0b",
          ink: "#121214",
          panel: "#17171a",
          raise: "#1e1e22",
          line: "#2a2a30",
          mute: "#6a6b72",
          soft: "#9a9ba2",
          fog: "#cdced3",
          paper: "#f4f1e8", // warm cream-white (dog paper)
          white: "#ffffff",
          rust: "#d64a2f", // the dog accent
          ember: "#f0876b",
          rustdk: "#a23320",
          cream: "#efe5cd",
          gold: "#c79a44",
          green: "#35d07f", // eligible
          greendk: "#1f9d5c",
          red: "#f0503a", // not eligible
          reddk: "#b8341f",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "ui-sans-serif", "system-ui"],
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
        pixel: ["var(--font-pixel)", "monospace"],
      },
      letterSpacing: { ultra: "0.35em" },
      backgroundImage: {
        "grid-mono":
          "linear-gradient(to right, rgba(255,255,255,0.045) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.045) 1px, transparent 1px)",
        "dot-mono":
          "radial-gradient(rgba(255,255,255,0.08) 1px, transparent 1px)",
      },
      keyframes: {
        marquee: { "0%": { transform: "translateX(0)" }, "100%": { transform: "translateX(-50%)" } },
        "marquee-rev": { "0%": { transform: "translateX(-50%)" }, "100%": { transform: "translateX(0)" } },
        blink: { "0%,49%": { opacity: "1" }, "50%,100%": { opacity: "0" } },
        rise: { "0%": { opacity: "0", transform: "translateY(12px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
      },
      animation: {
        marquee: "marquee 40s linear infinite",
        "marquee-rev": "marquee-rev 50s linear infinite",
        blink: "blink 1.1s steps(1) infinite",
        rise: "rise 0.6s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
