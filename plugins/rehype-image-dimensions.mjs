/**
 * rehype-image-dimensions
 *
 * Inietta a build time width/height reali su ogni <img> dei post che punta a
 * un file in public/, piu' loading="lazy" e decoding="async" (tranne la prima
 * immagine di ogni pagina, candidata LCP: rimandarne il caricamento peggiora
 * proprio la metrica che si vuole difendere).
 *
 * Perche': senza width/height il browser non conosce il rapporto d'aspetto
 * dell'immagine finche' non l'ha scaricata, quindi quando arriva spinge giu'
 * il testo. E' la causa del Cumulative Layout Shift sulle pagine articolo.
 * Il preflight di Tailwind applica img{max-width:100%;height:auto}, quindi gli
 * attributi danno solo il rapporto d'aspetto e l'immagine resta responsiva.
 *
 * Gestisce tre forme di nodo, perche' i post sono sia .md sia .mdx:
 *   - element          -> immagini scritte in markdown ![alt](src)
 *   - mdxJsxFlowElement / mdxJsxTextElement -> <img /> come JSX dentro un .mdx
 *   - raw / html       -> <img> in HTML grezzo dentro un .md. Astro non passa
 *     l'HTML grezzo dei .md attraverso rehype-raw, quindi resta un singolo
 *     nodo di testo: qui si riscrive il tag nella stringa. Si e' preferito
 *     questo a introdurre rehype-raw, che cambierebbe la gestione dell'HTML
 *     grezzo per tutto il sito.
 *
 * Nessuna dipendenza: le dimensioni si leggono dall'header IHDR del PNG.
 * Tutte le immagini dei post sono PNG; per altri formati il nodo viene
 * lasciato invariato senza far fallire il build.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";

const PUBLIC_DIR = join(process.cwd(), "public");
const cache = new Map();

/** Dimensioni di un PNG dai byte 16-23 (chunk IHDR). null se non e' un PNG. */
function pngSize(buf) {
  const SIG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  if (buf.length < 24) return null;
  for (let i = 0; i < 8; i++) if (buf[i] !== SIG[i]) return null;
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

function sizeOf(src) {
  if (cache.has(src)) return cache.get(src);
  let size = null;
  try {
    // via la query string (es. "/charts/x.png?v=2") e lo slash iniziale
    const rel = src.split("?")[0].split("#")[0].replace(/^\/+/, "");
    size = pngSize(readFileSync(join(PUBLIC_DIR, rel)));
  } catch {
    size = null;
  }
  cache.set(src, size);
  return size;
}

export default function rehypeImageDimensions() {
  return (tree, file) => {
    let seen = 0;
    const stats = { done: 0, skipped: 0 };

    const visit = (node) => {
      if (!node || typeof node !== "object") return;

      const isHtmlImg = node.type === "element" && node.tagName === "img";
      const isJsxImg =
        (node.type === "mdxJsxFlowElement" || node.type === "mdxJsxTextElement") &&
        node.name === "img";

      if (isHtmlImg || isJsxImg) {
        const get = (n) =>
          isHtmlImg
            ? node.properties?.[n]
            : node.attributes?.find((a) => a.type === "mdxJsxAttribute" && a.name === n)?.value;
        const set = (n, v) => {
          if (isHtmlImg) node.properties[n] = v;
          else node.attributes.push({ type: "mdxJsxAttribute", name: n, value: String(v) });
        };

        const src = get("src");
        // solo immagini locali servite da public/; gli URL esterni si ignorano
        if (typeof src === "string" && src.startsWith("/")) {
          const isFirst = seen === 0;
          seen++;
          const size = sizeOf(src);
          if (size && get("width") == null && get("height") == null) {
            set("width", size.width);
            set("height", size.height);
            if (get("decoding") == null) set("decoding", "async");
            // la prima immagine resta eager: e' candidata LCP
            if (!isFirst && get("loading") == null) set("loading", "lazy");
            stats.done++;
          } else if (!size) {
            stats.skipped++;
          }
        }
      }

      // HTML grezzo dei .md: il tag <img> vive dentro una stringa
      if ((node.type === "raw" || node.type === "html") && typeof node.value === "string") {
        node.value = node.value.replace(/<img\s[^>]*>/gi, (tag) => {
          const src = (tag.match(/\ssrc="([^"]+)"/i) || [])[1];
          if (!src || !src.startsWith("/")) return tag;
          const isFirst = seen === 0;
          seen++;
          if (/\swidth="/i.test(tag) || /\sheight="/i.test(tag)) return tag;
          const size = sizeOf(src);
          if (!size) {
            stats.skipped++;
            return tag;
          }
          let attrs = ` width="${size.width}" height="${size.height}"`;
          if (!/\sdecoding="/i.test(tag)) attrs += ' decoding="async"';
          if (!isFirst && !/\sloading="/i.test(tag)) attrs += ' loading="lazy"';
          stats.done++;
          // inserisce prima della chiusura, preservando i tag self-closing
          return tag.replace(/\s*\/?>$/, (end) => attrs + (end.includes("/") ? " />" : ">"));
        });
      }

      const kids = node.children;
      if (Array.isArray(kids)) for (const k of kids) visit(k);
    };

    visit(tree);

    if (stats.skipped) {
      const where = file?.history?.[0] ?? "(sconosciuto)";
      console.warn(
        `[rehype-image-dimensions] ${stats.skipped} immagini senza dimensioni leggibili in ${where}`
      );
    }
  };
}
