const { fontFamily } = require("tailwindcss/defaultTheme")
 
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./index.html","app/**/*.{ts,tsx,jsx}", "components/**/*.{ts,tsx,jsx}"],
  theme: {},
  plugins: [require("tailwindcss-animate")],
}