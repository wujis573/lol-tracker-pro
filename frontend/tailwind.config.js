/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#fefce8',
          100: '#fef9c3',
          200: '#fef08a',
          300: '#fde047',
          400: '#facc15',
          500: '#eab308',
          600: '#ca8a04',
          700: '#a16207',
          800: '#854d0e',
          900: '#713f12',
        },
        lol: {
          blue: '#0ac8b9',
          gold: '#c8aa6e',
          red: '#c23b3b',
          dark: '#091428',
          navy: '#1e282d',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'Microsoft YaHei', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
