import type { Metadata } from 'next'
import { ClerkProvider } from '@clerk/nextjs'
import { Header } from '@/components/Header'
import './globals.css'

export const metadata: Metadata = {
  title: 'SecureScript - Security Analysis',
  description: 'AI-powered code security analysis',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body className="font-sans antialiased" suppressHydrationWarning>
          <div className="min-h-screen bg-background flex flex-col">
            <Header />
            <main className="flex-1">
              {children}
            </main>
          </div>
        </body>
      </html>
    </ClerkProvider>
  )
}
