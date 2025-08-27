import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
// import '../styles/link-status.css' // Temporarily disabled
import { ThemeProvider } from '@/components/ThemeProvider'
// import { LinkStatusProvider } from '@/contexts/LinkStatusContext' // Temporarily disabled

const inter = Inter({ subsets: ['latin'] })

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
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}