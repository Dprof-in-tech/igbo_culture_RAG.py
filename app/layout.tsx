import './globals.css';
import { Playfair_Display, Work_Sans } from 'next/font/google';

// The vietnamese subset carries the Igbo dotted vowels (ị ụ ọ). Without it they
// fall back mid-word to a system font.
const playfair = Playfair_Display({
  subsets: ['latin', 'latin-ext', 'vietnamese'],
  weight: ['500', '700'],
  style: ['normal', 'italic'],
  variable: '--font-playfair',
  display: 'swap',
});

const workSans = Work_Sans({
  subsets: ['latin', 'latin-ext', 'vietnamese'],
  weight: ['300', '400', '500', '600'],
  variable: '--font-work-sans',
  display: 'swap',
});

export const metadata = {
  title: 'Achalugo — Onye Amamihe',
  description:
    'Hello, I am Achalugo, your closest Igbo elder and onye Amamihe. I am here to help you understand Igbo culture, tradition and customs.',
  themeColor: '#F5EFE4',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${playfair.variable} ${workSans.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
