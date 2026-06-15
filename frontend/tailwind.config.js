/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        cream: '#FAF6EE',
        ink: '#15140F',
        coral: '#FF5C39',
        lime: '#D6F23C',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
      },
      boxShadow: {
        hard: '6px 6px 0 0 #15140F',
        'hard-sm': '4px 4px 0 0 #15140F',
        'hard-lg': '10px 10px 0 0 #15140F',
      },
    },
  },
  plugins: [],
}
