from typing import List
from .base import BaseTemplate

class ViteReactTemplate(BaseTemplate):
    id = "vite_react"
    name = "Frontend SPA (Vite + React + Tailwind + TypeScript)"
    short_name = "Frontend SPA (Vite + React)"
    description = "Ultra-fast frontend Single Page Application with Vite 5, React 18, TypeScript, and Tailwind CSS."
    category = "Frontend"
    has_node = True
    has_python = False

    def scaffold(self) -> List[str]:
        files_created = []

        # package.json
        pkg_json = """{
  "name": "{{PROJECT_NAME_LOWER}}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.453.0"
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

        # vite.config.ts
        vite_config = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
  },
});
"""
        self.write_file("vite.config.ts", vite_config)
        files_created.append("vite.config.ts")

        # tsconfig.json
        tsconfig = """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}"""
        self.write_file("tsconfig.json", tsconfig)
        files_created.append("tsconfig.json")

        # index.html
        index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{PROJECT_NAME}}</title>
  </head>
  <body class="bg-slate-950 text-slate-100 min-h-screen">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
        self.write_file("index.html", index_html)
        files_created.append("index.html")

        # tailwind.config.js & postcss.config.js
        self.write_file("tailwind.config.js", """/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
""")
        self.write_file("postcss.config.js", """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
""")
        files_created.extend(["tailwind.config.js", "postcss.config.js"])

        # src/index.css
        self.write_file("src/index.css", "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")
        files_created.append("src/index.css")

        # src/main.tsx
        main_tsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
"""
        self.write_file("src/main.tsx", main_tsx)
        files_created.append("src/main.tsx")

        # src/App.tsx
        app_tsx = """import React, { useState } from 'react';
import { Sparkles, Terminal, Code2 } from 'lucide-react';

export default function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center">
      <div className="max-w-xl p-8 border border-slate-800 bg-slate-900/60 backdrop-blur rounded-2xl shadow-xl">
        <div className="flex justify-center mb-4 text-cyan-400">
          <Sparkles className="w-12 h-12 animate-pulse" />
        </div>
        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
          {{PROJECT_NAME}}
        </h1>
        <p className="mt-3 text-slate-400">
          Scaffolded with Vite, React, TypeScript, and Tailwind CSS.
        </p>

        <div className="mt-6 flex justify-center gap-4">
          <button
            onClick={() => setCount((c) => c + 1)}
            className="px-4 py-2 font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors"
          >
            Count is {count}
          </button>
        </div>
      </div>
    </div>
  );
}
"""
        self.write_file("src/App.tsx", app_tsx)
        files_created.append("src/App.tsx")

        return files_created
