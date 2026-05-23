import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101826",
        mist: "#eef2fb",
        chrome: "#9db2db",
        accent: "#3f7ef2",
      },
      fontFamily: {
        sans: ["SF Pro Text", "Segoe UI Variable Text", "Manrope", "IBM Plex Sans", "system-ui"],
      },
      boxShadow: {
        soft: "0 24px 44px rgba(16, 25, 46, 0.22)",
      },
    },
  },
  plugins: [],
};

export default config;
