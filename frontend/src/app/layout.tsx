import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "web-defense-ai V2 | Consola de seguridad",
  description: "Consola de ciberseguridad web-defense-ai V2. Interfaz en modo demostración con datos sintéticos.",
  applicationName: "web-defense-ai V2",
};

export const viewport: Viewport = {
  themeColor: "#0a1116",
  colorScheme: "dark",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es"><body>{children}</body></html>;
}
