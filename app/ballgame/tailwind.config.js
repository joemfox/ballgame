const { fontFamily } = require("tailwindcss/defaultTheme")
 
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./index.html","src/**/*.{ts,tsx,jsx}", "src/components/**/*.{ts,tsx,jsx}",'./@/**/*.{ts,tsx,jsx}'],
  theme: {
    extend: {
      fontFamily:{
        customfontname: ['Segoe UI', 
                       'Helvetica Neue', 
                       'Arial',
                       'sans-serif',
                       /*...*/ fontFamily.customfontname],
      },
      }
    },
  plugins: [require("tailwindcss-animate")],
}