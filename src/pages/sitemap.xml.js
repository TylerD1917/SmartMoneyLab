import { getCollection } from "astro:content";

// Sitemap generata a build time dalle content collection (senza @astrojs/sitemap,
// rimosso per bug upstream). Prerender statico come rss.xml.js.
export const prerender = true;

export async function GET(context) {
  const site = context.site; // URL da astro.config (https://smartmoneylab.pages.dev)

  const posts = await getCollection("posts", ({ data }) => !data.draft);
  const tools = await getCollection("tools", ({ data }) => !data.draft);

  // Slug delle serie presenti negli articoli (per le pagine /serie/[series])
  const seriesSlugs = [...new Set(posts.map((p) => p.data.series).filter(Boolean))];

  const entries = [];
  const add = (path, date) =>
    entries.push({ loc: new URL(path, site).href, lastmod: date });

  const iso = (d) => (d ? new Date(d).toISOString().split("T")[0] : undefined);

  // Pagine statiche
  add("", undefined);
  add("chi-siamo/", undefined);
  add("strumenti/", undefined);

  // Articoli
  for (const p of posts) add(`posts/${p.slug}/`, iso(p.data.updatedDate ?? p.data.pubDate));
  // Strumenti
  for (const t of tools) add(`strumenti/${t.slug}/`, iso(t.data.updatedDate ?? t.data.pubDate));
  // Serie
  for (const s of seriesSlugs) add(`serie/${s}/`, undefined);

  const body =
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    entries
      .map(
        (e) =>
          `  <url><loc>${e.loc}</loc>` +
          (e.lastmod ? `<lastmod>${e.lastmod}</lastmod>` : "") +
          `</url>`
      )
      .join("\n") +
    `\n</urlset>\n`;

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
}
