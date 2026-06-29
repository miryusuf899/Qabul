/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        qabul: {
          ink: '#17211d',
          muted: '#65736c',
          mist: '#f4f6f2',
          panel: '#ffffff',
          line: '#dce4dc',
          leaf: '#2f8c67',
          leafDark: '#22684d',
          wash: '#eef3ee',
          graphite: '#26302b',
          amber: '#a66f2a',
        },
      },
      boxShadow: {
        soft: '0 18px 60px rgba(38, 48, 43, 0.08)',
        insetline: 'inset 0 1px 0 rgba(255, 255, 255, 0.72)',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans Variable', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono Variable', 'SFMono-Regular', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
}
