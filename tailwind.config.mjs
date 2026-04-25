import typography from "@tailwindcss/typography";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Palette "finance-clean" — accento navy, neutri slate
        brand: {
          50: "#f1f5f9",
          100: "#e2e8f0",
          200: "#cbd5e1",
          300: "#94a3b8",
          400: "#64748b",
          500: "#475569",
          600: "#334155",
          700: "#1e293b", // slate-800/700 mix — base testi
          800: "#0f172a",
          900: "#020617",
        },
        accent: {
          // blue-900 / blue-400 (light/dark)
          DEFAULT: "#1e3a8a",
          light: "#60a5fa",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
        serif: ["Source Serif Pro", "Georgia", "serif"],
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            "--tw-prose-body": theme("colors.slate.700"),
            "--tw-prose-headings": theme("colors.slate.900"),
            "--tw-prose-links": theme("colors.blue.900"),
            "--tw-prose-bold": theme("colors.slate.900"),
            "--tw-prose-quotes": theme("colors.slate.700"),
            "--tw-prose-code": theme("colors.slate.800"),
            "--tw-prose-th-borders": theme("colors.slate.300"),
            "--tw-prose-td-borders": theme("colors.slate.200"),
            "--tw-prose-invert-body": theme("colors.slate.300"),
            "--tw-prose-invert-headings": theme("colors.slate.50"),
            "--tw-prose-invert-links": theme("colors.blue.400"),
            "--tw-prose-invert-bold": theme("colors.slate.50"),
            "--tw-prose-invert-quotes": theme("colors.slate.300"),
            "--tw-prose-invert-code": theme("colors.slate.100"),
            "--tw-prose-invert-th-borders": theme("colors.slate.600"),
            "--tw-prose-invert-td-borders": theme("colors.slate.700"),
            maxWidth: "72ch",
            a: { textDecoration: "underline", textUnderlineOffset: "3px" },
            "table thead th": { textAlign: "left" },
          },
        },
      }),
    },
  },
  plugins: [typography],
};
