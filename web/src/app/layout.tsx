import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
// import '../styles/link-status.css' // Temporarily disabled
import { ThemeProvider } from '@/components/ThemeProvider'
// import { LinkStatusProvider } from '@/contexts/LinkStatusContext' // Temporarily disabled

// Configure Inter font with display swap for better loading
const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  preload: true,
  fallback: ['system-ui', 'Arial', 'sans-serif']
})

export const metadata: Metadata = {
  title: 'AutoCrate V12 - Professional Crate Design System',
  description: 'ASTM-compliant wooden crate design and calculation system with 3D visualization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className={`${inter.className} font-sans antialiased`} suppressHydrationWarning>
        <ThemeProvider>
          {children}
        </ThemeProvider>
        <script dangerouslySetInnerHTML={{
          __html: `
            // Fix visibility issue on load
            if (typeof window !== 'undefined') {
              window.addEventListener('load', function() {
                document.querySelectorAll('[style*="visibility"]').forEach(function(el) {
                  el.style.visibility = 'visible';
                });
              });
              // Also fix immediately
              document.querySelectorAll('[style*="visibility"]').forEach(function(el) {
                el.style.visibility = 'visible';
              });
            }
          `
        }} />
      </body>
    </html>
  )
}