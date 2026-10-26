from typing import List
from .base import BaseTemplate

class SaasFullstackTemplate(BaseTemplate):
    id = "saas_fullstack"
    name = "Full-Stack SaaS Boilerplate (Next.js 15 + Prisma + Stripe + Auth)"
    description = "Production-grade SaaS starter with Next.js 15 App Router, Tailwind CSS, Prisma DB, Stripe payments, and Auth."
    category = "SaaS / Full-Stack"
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
    "lint": "next lint",
    "db:push": "prisma db push",
    "db:studio": "prisma studio"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@prisma/client": "^5.21.1",
    "stripe": "^17.2.1",
    "lucide-react": "^0.453.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.4"
  },
  "devDependencies": {
    "prisma": "^5.21.1",
    "typescript": "^5.6.3",
    "@types/node": "^22.8.1",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.14",
    "autoprefixer": "^10.4.20"
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
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}"""
        self.write_file("tsconfig.json", tsconfig)
        files_created.append("tsconfig.json")

        # prisma/schema.prisma
        schema_prisma = """datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String?   @unique
  emailVerified DateTime?
  image         String?
  stripeCustomerId String? @unique
  subscriptionId   String? @unique
  priceId          String?
  status           String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}
"""
        self.write_file("prisma/schema.prisma", schema_prisma)
        files_created.append("prisma/schema.prisma")

        # app/layout.tsx
        layout = """import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "{{PROJECT_NAME}} — Modern SaaS",
  description: "Built with Next.js 15 and Aayush's DevKit",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
"""
        self.write_file("app/layout.tsx", layout)
        files_created.append("app/layout.tsx")

        # app/page.tsx (Landing & Pricing Table)
        page = """import { Check, ArrowRight, Zap, Shield, Sparkles } from "lucide-react";

export default function SaaSPage() {
  return (
    <main className="flex flex-col items-center justify-center px-6 py-20">
      {/* Hero */}
      <div className="max-w-4xl text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium text-indigo-400 bg-indigo-950/60 border border-indigo-800/60 rounded-full">
          <Sparkles className="w-3.5 h-3.5" /> Next.js 15 & Stripe Ready
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl bg-gradient-to-br from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
          Supercharge your workflow with {{PROJECT_NAME}}
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          The ultimate foundation for modern web applications. Pre-configured with Prisma ORM, Stripe subscriptions, and shadcn styling.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <a href="#pricing" className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-semibold text-white transition-all shadow-lg shadow-indigo-500/20 inline-flex items-center gap-2">
            Get Started <ArrowRight className="w-4 h-4" />
          </a>
          <a href="/dashboard" className="px-6 py-3 rounded-xl border border-slate-800 hover:bg-slate-900 font-semibold text-slate-300 transition-colors">
            View Dashboard
          </a>
        </div>
      </div>

      {/* Pricing Section */}
      <section id="pricing" className="mt-24 max-w-5xl w-full">
        <h2 className="text-3xl font-bold text-center mb-12">Simple, Predictable Pricing</h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800">
            <h3 className="text-xl font-bold">Starter</h3>
            <p className="text-sm text-slate-400 mt-1">For indie hackers and prototypes</p>
            <div className="mt-6 text-4xl font-extrabold">$19<span className="text-base text-slate-400 font-normal">/mo</span></div>
            <ul className="mt-6 space-y-3 text-sm text-slate-300">
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Unlimited Projects</li>
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Community Support</li>
            </ul>
            <button className="w-full mt-8 py-2.5 rounded-lg border border-slate-700 hover:bg-slate-800 font-medium">Choose Starter</button>
          </div>

          <div className="p-8 rounded-2xl bg-indigo-950/20 border border-indigo-500/40 relative shadow-2xl">
            <span className="absolute -top-3 right-6 px-3 py-0.5 text-xs font-semibold bg-indigo-600 text-white rounded-full">POPULAR</span>
            <h3 className="text-xl font-bold">Pro</h3>
            <p className="text-sm text-slate-400 mt-1">For growing startups and teams</p>
            <div className="mt-6 text-4xl font-extrabold">$49<span className="text-base text-slate-400 font-normal">/mo</span></div>
            <ul className="mt-6 space-y-3 text-sm text-slate-300">
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Everything in Starter</li>
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Priority 24/7 Support</li>
              <li className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-400" /> Custom Domain & Analytics</li>
            </ul>
            <button className="w-full mt-8 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-white transition-colors">Upgrade to Pro</button>
          </div>
        </div>
      </section>
    </main>
  );
}
"""
        self.write_file("app/page.tsx", page)
        files_created.append("app/page.tsx")

        # app/globals.css & tailwind
        self.write_file("app/globals.css", "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")
        files_created.append("app/globals.css")
        
        self.write_file("tailwind.config.ts", """import type { Config } from "tailwindcss";
const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
export default config;
""")
        files_created.append("tailwind.config.ts")

        # .env.example
        self.write_file(".env.example", "DATABASE_URL=\"file:./dev.db\"\nSTRIPE_SECRET_KEY=\"sk_test_...\"\nSTRIPE_WEBHOOK_SECRET=\"whsec_...\"\nNEXTAUTH_SECRET=\"supersecret\"\n")
        files_created.append(".env.example")

        return files_created
