from typing import List
from .base import BaseTemplate

class DesignSystemTemplate(BaseTemplate):
    id = "design_system"
    name = "Design System & Component Library (React + Tailwind + Motion)"
    short_name = "Design System & UI Library (React + Motion)"
    description = "Tokenized UI component library with Framer Motion, accessible primitives, and interactive showcase catalog."
    category = "Design / Components"
    has_node = True
    has_python = False

    def scaffold(self) -> List[str]:
        files_created = []

        # package.json
        pkg_json = """{
  "name": "{{PROJECT_NAME_LOWER}}",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "framer-motion": "^11.11.9",
    "lucide-react": "^0.453.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.4"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.3",
    "typescript": "^5.6.3",
    "vite": "^5.4.10",
    "tailwindcss": "^3.4.14",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.47"
  }
}"""
        self.write_file("package.json", pkg_json)
        files_created.append("package.json")

        # tokens/colors.ts
        colors_ts = """export const tokens = {
  colors: {
    brand: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      500: '#0ea5e9',
      600: '#0284c7',
      900: '#0c4a6e',
    },
    surface: {
      background: '#090d16',
      card: '#0f172a',
      border: '#1e293b',
    },
  },
  radius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    full: '9999px',
  },
  motion: {
    spring: { type: 'spring', stiffness: 350, damping: 25 },
    subtle: { duration: 0.15, ease: 'easeOut' },
  },
};
"""
        self.write_file("src/tokens/index.ts", colors_ts)
        files_created.append("src/tokens/index.ts")

        # components/Button.tsx
        btn = """import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface ButtonProps extends HTMLMotionProps<'button'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const base = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 disabled:opacity-50 disabled:pointer-events-none';
    const variants = {
      primary: 'bg-sky-500 text-white hover:bg-sky-400 active:bg-sky-600',
      secondary: 'bg-slate-800 text-slate-100 hover:bg-slate-700 active:bg-slate-900',
      outline: 'border border-slate-700 text-slate-200 hover:bg-slate-800',
      ghost: 'text-slate-300 hover:bg-slate-800/60',
    };
    const sizes = {
      sm: 'h-8 px-3 text-xs',
      md: 'h-10 px-4 text-sm',
      lg: 'h-12 px-6 text-base',
    };

    return (
      <motion.button
        ref={ref}
        whileTap={{ scale: 0.97 }}
        whileHover={{ scale: 1.01 }}
        className={twMerge(clsx(base, variants[variant], sizes[size], className))}
        {...props}
      >
        {children}
      </motion.button>
    );
  }
);
Button.displayName = 'Button';
"""
        self.write_file("src/components/Button.tsx", btn)
        files_created.append("src/components/Button.tsx")

        # src/App.tsx (Component Showcase)
        app_tsx = """import React from 'react';
import { Button } from './components/Button';
import { Sparkles, Layers, Palette } from 'lucide-react';

export default function Showcase() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-10 max-w-5xl mx-auto">
      <header className="border-b border-slate-800 pb-8 mb-10">
        <div className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-sky-400 bg-sky-950/60 px-3 py-1 rounded-full mb-3">
          <Layers className="w-3.5 h-3.5" /> Component System
        </div>
        <h1 className="text-4xl font-extrabold">{{PROJECT_NAME}}</h1>
        <p className="text-slate-400 mt-2">Design system tokens, accessible primitives, and fluid motion physics.</p>
      </header>

      <section className="space-y-6">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Palette className="w-5 h-5 text-sky-400" /> Buttons & Interactions
        </h2>
        <div className="flex flex-wrap gap-4 p-6 rounded-xl border border-slate-800 bg-slate-900/40">
          <Button variant="primary">Primary Button</Button>
          <Button variant="secondary">Secondary Button</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost Button</Button>
        </div>
      </section>
    </div>
  );
}
"""
        self.write_file("src/App.tsx", app_tsx)
        files_created.append("src/App.tsx")

        # index.html, vite.config.ts, tailwind, etc.
        self.write_file("index.html", '<!doctype html><html lang="en"><head><meta charset="UTF-8" /><title>{{PROJECT_NAME}}</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>')
        self.write_file("src/main.tsx", "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App.tsx';\nimport './index.css';\nReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);\n")
        self.write_file("src/index.css", "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")
        self.write_file("vite.config.ts", "import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\nexport default defineConfig({ plugins: [react()] });\n")
        self.write_file("tailwind.config.js", "export default { content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'], theme: { extend: {} }, plugins: [] };\n")
        self.write_file("postcss.config.js", "export default { plugins: { tailwindcss: {}, autoprefixer: {} } };\n")
        
        files_created.extend(["index.html", "src/main.tsx", "src/index.css", "vite.config.ts", "tailwind.config.js"])
        return files_created
