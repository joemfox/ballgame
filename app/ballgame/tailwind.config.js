const { fontFamily } = require("tailwindcss/defaultTheme")
 
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./index.html","src/**/*.{ts,tsx,jsx}", "src/components/**/*.{ts,tsx,jsx}",'./@/**/*.{ts,tsx,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-geist-sans)'],
        mono: ['var(--font-geist-mono)'],
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
}