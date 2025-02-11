import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "广告Bot",
  description: "有灵魂的 Bot.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className='w-full md:w-1/2 flex justify-center items-center mx-auto'>
        {children}
      </body>
    </html>
  );
}
