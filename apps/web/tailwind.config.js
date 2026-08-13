/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        card: '#111827',
        border: '#1f2937',
        primary: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
        },
      },
    },
  },
  plugins: [],
}
