# SmartMoneyLab

> Finanza personale e analisi quantitativa. Articoli, simulazioni e strumenti
> interattivi per investitori retail italiani con conoscenze intermedie.

## Stack

- **[Astro](https://astro.build)** (SSG) + **MDX** per gli articoli
- **Tailwind CSS** + `@tailwindcss/typography` per lo styling
- **React** per i componenti interattivi (calcolatori, simulatori)
- **Chart.js** + **Recharts** per la visualizzazione dati
- **Python** (pandas, numpy, matplotlib, yfinance) per le simulazioni
  → grafici PNG/SVG esportati in `public/charts/[slug]/`

## Struttura

```
src/
  content/posts/        # articoli .md / .mdx
  layouts/              # PostLayout.astro (include disclaimer), BaseLayout.astro
  components/           # Header, Footer, ThemeToggle, Disclaimer
  components/interactive/  # componenti React/Astro interattivi per i post
  pages/                # index, chi-siamo, posts/[slug]
  styles/global.css     # base CSS + variabili tema
scripts/                # simulazioni Python ([slug].py)
public/
  charts/[slug]/        # output grafici delle simulazioni
  favicon.svg, _headers, robots.txt
social/[slug]/          # repurposing per X / Instagram
```

## Sviluppo locale

Requisiti: **Node ≥ 20** (vedi `.nvmrc`).

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # output in dist/
npm run preview  # serve dist/ in locale
```

## Pipeline editoriale

Per ogni nuovo articolo:

1. `src/content/posts/[slug].md` con frontmatter completo
2. `scripts/[slug].py` per le simulazioni → grafici in `public/charts/[slug]/`
3. (Opzionale) componente in `src/components/interactive/[Slug].(astro|jsx)`
4. `social/[slug]/{x_thread,instagram_carousel,instagram_caption}.md`
5. `npm run build` per verificare → commit → push su `main`
6. Cloudflare Pages deploya automaticamente

Il **disclaimer** è incluso automaticamente in fondo a ogni articolo via `PostLayout.astro`.

## Deploy — Cloudflare Pages

Il sito è statico: nessun adapter SSR. Il deploy parte automaticamente su push del
branch `main` una volta connesso il repo a Cloudflare Pages.

Configurazione progetto Cloudflare Pages:

| Campo                | Valore             |
|----------------------|--------------------|
| Framework preset     | Astro              |
| Build command        | `npm run build`    |
| Build output         | `dist`             |
| Root directory       | `/`                |
| Node version         | `20` (env var `NODE_VERSION=20`) |

## Disclaimer

I contenuti di questo blog hanno finalità esclusivamente informative e divulgative.
Non costituiscono consulenza finanziaria, raccomandazione di investimento né
sollecitazione al pubblico risparmio.
