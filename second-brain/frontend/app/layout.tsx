import "./globals.css";
import type { Metadata } from "next";
import Script from "next/script";

export const metadata: Metadata = {
  title: "Second Brain Workspace",
  description: "NotebookLM-inspired multimodal personal knowledge operating system",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Script id="theme-init" strategy="beforeInteractive">
          {`
            try {
              const key = 'second_brain_theme';
              const saved = localStorage.getItem(key);
              const theme = saved === 'light' ? 'light' : 'dark';
              document.documentElement.setAttribute('data-theme', theme);
            } catch (_) {}
          `}
        </Script>
        {children}
      </body>
    </html>
  );
}
