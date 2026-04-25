import rss from "@astrojs/rss";
import { getCollection } from "astro:content";

// Forza la pre-renderizzazione statica (in modalità `output: "static"` dovrebbe
// essere il default, ma lo rendiamo esplicito per evitare che venga trattato
// come endpoint SSR — comportamento che confondeva @astrojs/sitemap < 3.3).
export const prerender = true;

export async function GET(context) {
  const posts = await getCollection("posts", ({ data }) => !data.draft);
  posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  return rss({
    title: "SmartMoneyLab",
    description:
      "Finanza personale e analisi quantitativa. Articoli, simulazioni e strumenti interattivi per investitori retail italiani.",
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/posts/${post.slug}/`,
      categories: post.data.tags,
    })),
    customData: `<language>it-it</language>`,
  });
}
