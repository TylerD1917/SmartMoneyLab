// @ts-check
import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import mdx from "@astrojs/mdx";
import react from "@astrojs/react";

// https://astro.build/config
export default defineConfig({
  // Aggiornare con il dominio definitivo prima del go-live (es. https://smartmoneylab.it)
  site: "https://smartmoneylab.pages.dev",
  trailingSlash: "ignore",
  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
    mdx(),
    react(),
    // NOTA: @astrojs/sitemap rimosso temporaneamente per bug noto in build
    // (Cannot read properties of undefined reading 'reduce'). Da re-introdurre
    // dopo aggiornamento upstream o sostituire con generazione manuale.
  ],
  markdown: {
    shikiConfig: {
      theme: "github-dark-dimmed",
      wrap: true,
    },
  },
  build: {
    inlineStylesheets: "auto",
  },
});
