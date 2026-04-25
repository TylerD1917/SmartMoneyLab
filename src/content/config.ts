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
    }),
});

export const collections = { posts };
