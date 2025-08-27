/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // Engineering-specific color palette
        engineering: {
          blue: {
            50: '#eff6ff',
            100: '#dbeafe',
            500: '#3b82f6',
            600: '#2563eb',
            700: '#1d4ed8',
            900: '#1e3a8a',
          },
          gray: {
            50: '#f9fafb',
            100: '#f3f4f6',
            200: '#e5e7eb',
            300: '#d1d5db',
            400: '#9ca3af',
            500: '#6b7280',
            600: '#4b5563',
            700: '#374151',
            800: '#1f2937',
            900: '#111827',
          },
        },
      },
      // Modern viewport units
      spacing: {
        'dvh': '100dvh',
        'dvw': '100dvw',
        'svh': '100svh',
        'svw': '100svw',
        'lvh': '100lvh',
        'lvw': '100lvw',
        'header': '4rem',
        'footer': '3.5rem',
        'sidebar': '20rem',
        'sidebar-lg': '24rem',
      },
      // Responsive breakpoints with container queries
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
        '3xl': '1920px',
        // Container query breakpoints
        '@xs': '20rem',
        '@sm': '24rem', 
        '@md': '32rem',
        '@lg': '40rem',
        '@xl': '48rem',
        '@2xl': '56rem',
      },
      // Animation improvements
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-up': 'scaleUp 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleUp: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      // Advanced responsive typography
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        // Responsive text sizes
        'responsive-sm': 'clamp(0.875rem, 2vw, 1rem)',
        'responsive-base': 'clamp(1rem, 2.5vw, 1.125rem)',
        'responsive-lg': 'clamp(1.125rem, 3vw, 1.25rem)',
        'responsive-xl': 'clamp(1.25rem, 3.5vw, 1.5rem)',
      },
      // Grid system
      gridTemplateColumns: {
        'mobile': '1fr',
        'tablet': 'minmax(300px, 1fr) 1fr',
        'desktop': 'minmax(320px, 360px) minmax(600px, 1fr) minmax(350px, 420px)',
        'auto-fit': 'repeat(auto-fit, minmax(280px, 1fr))',
        'auto-fill': 'repeat(auto-fill, minmax(280px, 1fr))',
      },
      // Modern shadows
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        'glow': '0 0 20px rgb(59 130 246 / 0.3)',
      },
      // Backdrop blur
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
    },
  },
  plugins: [
    // Container queries plugin
    function({ addUtilities, theme, variants }) {
      const containerQueries = {
        '.container-query': {
          'container-type': 'inline-size',
        },
        // Mobile-first container queries
        '@container (min-width: 20rem)': {
          '.cq-xs\\:block': { display: 'block' },
          '.cq-xs\\:hidden': { display: 'none' },
          '.cq-xs\\:grid-cols-2': { 'grid-template-columns': 'repeat(2, minmax(0, 1fr))' },
        },
        '@container (min-width: 24rem)': {
          '.cq-sm\\:block': { display: 'block' },
          '.cq-sm\\:hidden': { display: 'none' },
          '.cq-sm\\:grid-cols-2': { 'grid-template-columns': 'repeat(2, minmax(0, 1fr))' },
          '.cq-sm\\:grid-cols-3': { 'grid-template-columns': 'repeat(3, minmax(0, 1fr))' },
        },
        '@container (min-width: 32rem)': {
          '.cq-md\\:block': { display: 'block' },
          '.cq-md\\:hidden': { display: 'none' },
          '.cq-md\\:grid-cols-2': { 'grid-template-columns': 'repeat(2, minmax(0, 1fr))' },
          '.cq-md\\:grid-cols-3': { 'grid-template-columns': 'repeat(3, minmax(0, 1fr))' },
          '.cq-md\\:flex-row': { 'flex-direction': 'row' },
        },
        '@container (min-width: 40rem)': {
          '.cq-lg\\:block': { display: 'block' },
          '.cq-lg\\:hidden': { display: 'none' },
          '.cq-lg\\:grid-cols-3': { 'grid-template-columns': 'repeat(3, minmax(0, 1fr))' },
          '.cq-lg\\:grid-cols-4': { 'grid-template-columns': 'repeat(4, minmax(0, 1fr))' },
        },
      }
      addUtilities(containerQueries)
    },
    // Responsive design utilities
    function({ addUtilities }) {
      const responsiveUtilities = {
        // Viewport-based sizing
        '.h-screen-safe': {
          height: '100vh',
          height: '100dvh',
        },
        '.min-h-screen-safe': {
          'min-height': '100vh',
          'min-height': '100dvh',
        },
        '.w-screen-safe': {
          width: '100vw',
          width: '100dvw',
        },
        // No-scroll containers
        '.no-scroll': {
          overflow: 'hidden',
          height: '100%',
          'max-height': '100%',
        },
        '.scroll-area': {
          'overflow-y': 'auto',
          'overflow-x': 'hidden',
          'scroll-behavior': 'smooth',
        },
        // Performance optimizations
        '.gpu-layer': {
          'will-change': 'transform',
          transform: 'translateZ(0)',
        },
        '.optimize-legibility': {
          'text-rendering': 'optimizeLegibility',
          '-webkit-font-smoothing': 'antialiased',
          '-moz-osx-font-smoothing': 'grayscale',
        },
        // Touch-friendly targets
        '.touch-target': {
          'min-height': '44px',
          'min-width': '44px',
        },
        '.touch-target-lg': {
          'min-height': '48px',
          'min-width': '48px',
        },
      }
      addUtilities(responsiveUtilities)
    },
  ],
}