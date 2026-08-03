/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    // The design switches between two discrete layouts at 820px rather than
    // flowing fluidly, so `desk` is the only breakpoint the app uses.
    screens: {
      desk: '820px',
    },
    extend: {
      colors: {
        paper: '#F5EFE4',
        desk: '#E7DFD1',
        ink: '#1E1B18',
        terracotta: {
          DEFAULT: '#B4462A',
          dark: '#8E3520',
        },
        saffron: '#D99A2B',
      },
      fontFamily: {
        serif: ['var(--font-playfair)', 'Playfair Display', 'serif'],
        sans: ['var(--font-work-sans)', 'Work Sans', 'sans-serif'],
      },
      keyframes: {
        rise: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'none' },
        },
        breathe: {
          '0%, 100%': { opacity: '.25' },
          '50%': { opacity: '1' },
        },
      },
      animation: {
        rise: 'rise .4s ease both',
        breathe: 'breathe 1.2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
