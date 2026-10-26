from typing import List
from .base import BaseTemplate

class ContentSiteTemplate(BaseTemplate):
    id = "content_site"
    name = "Modern Content & Marketing Site (Astro / Typography Polish)"
    short_name = "Content & Marketing Site (Astro)"
    description = "Blazing-fast content and marketing website with Astro 4, Tailwind Typography, SEO metadata, and zero JS by default."
    category = "Content / Marketing"
    has_node = True
    has_python = False

    def scaffold(self) -> List[str]:
        files_created = []

        # package.json
        pkg_json = """{
  "name": "{{PROJECT_NAME_LOWER}}",
  "type": "module",
  "version": "0.1.0",
  "scripts": {
    "dev": "astro dev",
    "start": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^4.16.0",
    "@astrojs/tailwind": "^5.1.2",
    "tailwindcss": "^3.4.14",
    "@tailwindcss/typography": "^0.5.15"
  }
}"""
        self.write_file("package.json", pkg_json)
        files_created.append("package.json")

        # astro.config.mjs
        astro_cfg = """import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind()],
});
"""
        self.write_file("astro.config.mjs", astro_cfg)
        files_created.append("astro.config.mjs")

        # src/pages/index.astro
        index_astro = """---
const title = "{{PROJECT_NAME}} — Editorial & Content";
const description = "Crafted with intentional typography, whitespace, and high-aesthetic art direction.";
---

<html lang="en" class="bg-[#0c0e14] text-slate-100 antialiased selection:bg-amber-500/20 selection:text-amber-300">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>{title}</title>
    <meta name="description" content={description} />
  </head>
  <body class="min-h-screen flex flex-col justify-between max-w-4xl mx-auto px-6 py-16">
    <header class="flex items-center justify-between border-b border-white/5 pb-8">
      <span class="font-serif text-2xl font-bold tracking-tight text-white">{{PROJECT_NAME}}</span>
      <nav class="flex gap-6 text-sm text-slate-400">
        <a href="#articles" class="hover:text-white transition-colors">Essays</a>
        <a href="#about" class="hover:text-white transition-colors">About</a>
      </nav>
    </header>

    <main class="my-20">
      <p class="text-xs font-mono uppercase tracking-widest text-amber-400/90 mb-4">Volume I · Issue 01</p>
      <h1 class="font-serif text-5xl md:text-6xl font-normal tracking-tight text-slate-50 leading-[1.15] max-w-3xl">
        Design is what remains after every unnecessary decision has been discarded.
      </h1>
      <p class="mt-8 text-xl text-slate-400 font-light leading-relaxed max-w-2xl">
        An aesthetic publication and product space crafted with deliberate rhythm, proportional negative space, and typographic authority.
      </p>

      <section id="articles" class="mt-24 space-y-12">
        <h2 class="text-sm font-mono uppercase tracking-wider text-slate-400 border-b border-white/10 pb-3">Featured Essays</h2>
        
        <article class="group cursor-pointer">
          <time class="text-xs font-mono text-slate-500">OCTOBER 2026</time>
          <h3 class="text-2xl font-serif text-white group-hover:text-amber-300 transition-colors mt-1">
            The Death of Generic Interfaces
          </h3>
          <p class="text-slate-400 mt-2 font-light">Why modern software is escaping AI homogeny and rediscovering craft.</p>
        </article>
      </section>
    </main>

    <footer class="border-t border-white/5 pt-8 text-xs text-slate-400 flex justify-between">
      <span>© 2026 {{PROJECT_NAME}}</span>
      <span>Scaffolded by Aayush's DevKit</span>
    </footer>
  </body>
</html>
"""
        self.write_file("src/pages/index.astro", index_astro)
        files_created.append("src/pages/index.astro")

        # tailwind.config.cjs
        self.write_file("tailwind.config.cjs", """module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Georgia', 'Cambria', 'serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
""")
        files_created.append("tailwind.config.cjs")

        return files_created
