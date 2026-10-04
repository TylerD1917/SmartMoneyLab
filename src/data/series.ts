/**
 * Registry delle "serie" trasversali del blog. Una serie e' un insieme di
 * articoli che seguono lo stesso format ricorrente. Ogni post puo' opzionalmente
 * dichiarare nel frontmatter `series: "<slug>"` e `seriesOrder: <n>` per
 * comparire nella pagina indice della serie e mostrare un badge.
 */

export interface SeriesMeta {
  slug: string;
  title: string;
  shortLabel: string; // versione abbreviata per il badge inline
  description: string;
}

export const SERIES: Record<string, SeriesMeta> = {
  "le-basi": {
    slug: "le-basi",
    title: "Le basi: dodici episodi per partire da zero",
    shortLabel: "Le basi",
    description:
      "Dodici episodi in quattro blocchi — perche' investire e con quali " +
      "soldi, dove si puo' mettere il denaro, gli strumenti e quanto " +
      "costano, come si leggono i numeri. Vanno letti in ordine: ogni " +
      "blocco da' per noto il precedente.",
  },
  "battere-il-mercato": {
    slug: "battere-il-mercato",
    title: "Strategie per battere il mercato?",
    shortLabel: "Battere il mercato?",
    description:
      "Test di backtest su strategie di investimento famose o meno famose, " +
      "applicando il framework SmartMoneyLab a 6+1 metriche (CAGR, win rate, " +
      "volatilita', max drawdown, Sharpe, Calmar, Sortino) per rispondere alla " +
      "domanda fondamentale: questa strategia batte davvero un investimento " +
      "passivo nel mercato?",
  },
};

export function getSeriesMeta(slug: string | undefined): SeriesMeta | null {
  if (!slug) return null;
  return SERIES[slug] ?? null;
}
