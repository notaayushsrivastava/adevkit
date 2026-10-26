from typing import List
from .base import BaseTemplate

class NextjsTemplate(BaseTemplate):
    id = "nextjs"
    name = "Full-Stack Next.js (TypeScript + Tailwind + shadcn)"
    short_name = "Next.js Full-Stack (App Router)"
    description = "Modern Next.js 14/15 App Router, React 19, TypeScript, Tailwind CSS, Lucide Icons, and shadcn setup."
    category = "Full-Stack"
    has_node = True
    has_python = False

    def scaffold(self) -> List[str]:
        files_created = []

        # package.json
        pkg_json = """{
  "name": "{{PROJECT_NAME_LOWER}}",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.2.15",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.453.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.4"
  },
  "devDependencies": {
    "typescript": "^5.6.3",
    "@types/node": "^22.8.1",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.14",
    "autoprefixer": "^10.4.20",
    "eslint": "^8.57.1",
    "eslint-config-next": "14.2.15"
  }
}"""
        self.write_file("package.json", pkg_json)
        files_created.append("package.json")

        # tsconfig.json
        tsconfig = """{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}"""
        self.write_file("tsconfig.json", tsconfig)
        files_created.append("tsconfig.json")

        # next.config.mjs
        next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
"""
        self.write_file("next.config.mjs", next_config)
        files_created.append("next.config.mjs")

        # tailwind.config.ts
        tailwind_config = """import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
};
export default config;
"""
        self.write_file("tailwind.config.ts", tailwind_config)
        files_created.append("tailwind.config.ts")

        # postcss.config.mjs
        postcss_config = """const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
export default config;
"""
        self.write_file("postcss.config.mjs", postcss_config)
        files_created.append("postcss.config.mjs")

        # app/globals.css
        globals_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #ffffff;
  --foreground: #0f172a;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #090d16;
    --foreground: #f8fafc;
  }
}

body {
  color: var(--foreground);
  background: var(--background);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
"""
        self.write_file("app/globals.css", globals_css)
        files_created.append("app/globals.css")

        # app/layout.tsx
        layout_tsx = """import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "{{PROJECT_NAME}}",
  description: "Built with Aayush's DevKit",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  );
}
"""
        self.write_file("app/layout.tsx", layout_tsx)
        files_created.append("app/layout.tsx")

        # app/page.tsx
        page_tsx = """export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 text-center">
      <div className="max-w-2xl bg-slate-900/40 border border-slate-800 rounded-2xl p-10 shadow-2xl backdrop-blur-sm">
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
          {{PROJECT_NAME}}
        </h1>
        <p className="mt-4 text-lg text-slate-300">
          Initialized seamlessly with <span className="font-semibold text-white">Aayush's DevKit</span>.
        </p>
        <div className="mt-8 flex flex-wrap gap-4 justify-center">
          <a
            href="https://nextjs.org/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-medium text-white transition-colors"
          >
            Next.js Docs
          </a>
          <a
            href="#agents"
            className="px-5 py-2.5 rounded-lg border border-slate-700 hover:bg-slate-800 font-medium text-slate-200 transition-colors"
          >
            Check AGENTS.md
          </a>
        </div>
      </div>
    </main>
  );
}
"""
        self.write_file("app/page.tsx", page_tsx)
        files_created.append("app/page.tsx")

        # .env.example
        self.write_file(".env.example", "NEXT_PUBLIC_APP_NAME={{PROJECT_NAME}}\nPORT=3000\n")
        files_created.append(".env.example")

        return files_created
