import { defineCollection, z } from "astro:content";

const posts = defineCollection({
  type: "content",
  schema: ({ image }) =>
    z.object({
      title: z.string().max(120),
      description: z.string().max(220),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      tags: z.array(z.string()).default([]),
      author: z.string().default("SmartMoneyLab"),
      ogImage: image().optional(),
      heroImage: image().optional(),
      draft: z.boolean().default(false),
      // Slug del progetto Python associato (se presente) — corrisponde a scripts/[slug].py
      simulationSlug: z.string().optional(),
      // Appartenenza a una "serie" tematica trasversale (es. "battere-il-mercato")
      series: z.string().optional(),
      seriesOrder: z.number().int().positive().optional(),
      // Verdict opzionale per articoli-strategia (vince/parziale/non vince)
      verdict: z.enum(["vince", "parziale", "non-vince"]).optional(),
      // FAQ per lo schema markup JSON-LD (FAQPage). Le stesse domande vanno
      // comunque scritte nel corpo dell'articolo: qui servono solo a Google.
      faq: z
        .array(z.object({ q: z.string(), a: z.string() }))
        .optional(),
      // Quale grafico mettere dentro la card di anteprima social, come path
      // pubblico (es. "/charts/slug/02_montanti.png"). Se omesso, lo script
      // scripts/make_og_images.py usa il primo grafico della cartella.
      // NON e' l'og:image finale: quella e' sempre /og/<slug>.png, generata.
      seoImage: z.string().optional(),
    }),
});

// Collection "tools": strumenti gratuiti per l'investitore (fogli Excel,
// calcolatori, dashboard live, liste di letture). Layout dedicato con
// bottone download in evidenza.
const tools = defineCollection({
  type: "content",
  schema: ({ image }) =>
    z.object({
      title: z.string().max(120),
      description: z.string().max(220),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      tags: z.array(z.string()).default([]),
      author: z.string().default("SmartMoneyLab"),
      ogImage: image().optional(),
      heroImage: image().optional(),
      draft: z.boolean().default(false),
      // Tipologia dello strumento (per icona/categoria nella index)
      toolType: z
        .enum(["excel", "google-sheets", "calculator", "dashboard", "reading-list", "other"])
        .default("excel"),
      // Path relativo al file scaricabile in public/, es. "/tools/tracker-investimenti.xlsx"
      downloadUrl: z.string().optional(),
      // Nome del file da suggerire al browser quando si scarica
      downloadFilename: z.string().optional(),
      // Dimensione del file leggibile (es. "68 kB")
      downloadSize: z.string().optional(),
      // Tier dello strumento — per future versioni Pro a pagamento
      tier: z.enum(["free", "pro"]).default("free"),
      // Nota di licenza/uso (default: uso personale, non rivendibile)
      license: z
        .string()
        .default(
          "Uso personale e modifica liberi. Non rivendibile o redistribuibile in versione modificata senza autorizzazione."
        ),
    }),
});

export const collections = { posts, tools };
