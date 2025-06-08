import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'ACHALUGO AI',
  description: 'Hello, my dear! I am Achalugo, an Igbo Woman who is deeply rooted in our culture. I am here to share my knowledge and wisdom with you!',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
