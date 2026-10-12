/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        scada: {
          dark: '#1e2124',
          panel: '#282b30',
          border: '#36393e',
          text: '#dcddde',
          primary: '#7289da',
          accent: '#43b581',
          alert: '#f04747'
        }
      }
    },
  },
  plugins: [],
}
