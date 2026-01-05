/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,svelte}",
    "./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}"
  ],
  theme: {
    extend: {
      colors: {
        // Finnish colors
        'finnish-blue': {
          50: '#e6f0ff',
          100: '#cce7ff',
          200: '#99d1ff',
          300: '#66b8ff',
          400: '#339eff',
          500: '#0080ff', // Vibrant primary Finnish blue
          600: '#0066e6',
          700: '#004dcc',
          800: '#003399',
          900: '#002266',
        },
        'finnish-gold': {
          50: '#fff8e1',
          100: '#ffecb3',
          200: '#ffd54f',
          300: '#ffbf00',
          400: '#ffa000',
          500: '#FFB81C', // Primary Finnish gold
          600: '#e6a700',
          700: '#cc8a00',
          800: '#b26d00',
          900: '#995200',
        },
        'nordic-blue': {
          50: '#e3f2fd',
          100: '#bbdefb',
          200: '#90caf9',
          300: '#64b5f6',
          400: '#42a5f5',
          500: '#2196f3',
          600: '#1e88e5',
          700: '#1976d2',
          800: '#1565c0',
          900: '#0d47a1',
        },
        'forest-green': {
          50: '#e8f5e8',
          100: '#c8e6c9',
          200: '#a5d6a7',
          300: '#81c784',
          400: '#66bb6a',
          500: '#4caf50',
          600: '#43a047',
          700: '#388e3c',
          800: '#2e7d32',
          900: '#1b5e20',
        },
        'success-green': '#2D5A27',
        'warning-orange': '#FF8C00',
        'error-red': '#D00000',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
        'mono': ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '104': '26rem',
        '128': '32rem',
      },
      boxShadow: {
        'light': '0 2px 4px rgba(0, 0, 0, 0.05)',
        'medium': '0 4px 12px rgba(0, 0, 0, 0.08)',
        'heavy': '0 8px 24px rgba(0, 0, 0, 0.12)',
        'gold': '0 4px 20px rgba(255, 184, 28, 0.3)',
        'blue': '0 4px 20px rgba(0, 128, 255, 0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}