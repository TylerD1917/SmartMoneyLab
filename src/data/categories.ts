/**
 * Registry delle "categorie" editoriali del blog. A differenza delle serie
 * (archi narrativi ricorrenti, opzionali), la categoria è il tipo PRINCIPALE
 * di un articolo: una sola, mutuamente esclusiva. Ogni post la dichiara nel
 * frontmatter con `category: "<slug>"`.
 *
 * Alimenta:
 *  - la barra di filtri in cima alla home (filtro client-side via ?cat=)
 *  - le pagine indicizzabili /categoria/<slug> (una per categoria)
 *  - il badge categoria mostrato su ogni card articolo
 */

export interface CategoryMeta {
  slug: string;
  title: string; // titolo pieno (pagina hub + <title>)
  shortLabel: string; // etichetta breve per chip e badge
  description: string;
}

export const CATEGORIES: Record<string, CategoryMeta> = {
  strategie: {
    slug: "strategie",
    title: "Strategie & backtest",
    shortLabel: "Strategie & backtest",
    description:
      "Strategie d'investimento e portafogli — reali o famosi — messi alla " +
      "prova con lo stesso metodo: framework a 6+1 metriche, finestre mobili, " +
      "Monte Carlo, benchmark passivo. La domanda di fondo è sempre la stessa: " +
      "battono davvero un semplice indice? Include la serie “Battere il mercato?”.",
  },
  approfondimenti: {
    slug: "approfondimenti",
    title: "Studi & approfondimenti",
    shortLabel: "Studi",
    description:
      "Curiosità e analisi data-driven su asset class, segmenti di mercato, " +
      "materie prime e indicatori (CAPE, correlazioni, regimi di tasso). " +
      "Studi seri a finale aperto, senza verdetto secco: i dati, le ipotesi " +
      "dichiarate, e le conclusioni lasciate al lettore.",
  },
  "finanza-personale": {
    slug: "finanza-personale",
    title: "Finanza personale",
    shortLabel: "Finanza personale",
    description:
      "Le decisioni concrete di chi gestisce i propri soldi: accumulo e " +
      "decumulo (FIRE, quanto capitale serve per smettere di lavorare), " +
      "fondamentali (quale indice scegliere, come funziona un ETF), fiscalità " +
      "italiana (tassazione, recupero minusvalenze) e scelte di vita finanziaria " +
      "(mutuo fisso o variabile, TFR, fondo pensione).",
  },
};

// Ordine in cui mostrare i chip di filtro e le voci.
export const CATEGORY_ORDER: string[] = [
  "strategie",
  "approfondimenti",
  "finanza-personale",
];

export function getCategoryMeta(slug: string | undefined): CategoryMeta | null {
  if (!slug) return null;
  return CATEGORIES[slug] ?? null;
}
