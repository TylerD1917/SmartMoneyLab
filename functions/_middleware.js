// Redirect 301 da smartmoneylab.pages.dev al dominio canonico smartmoneylab.it.
// Cloudflare Pages esegue questa function su ogni richiesta; sul dominio .it passa oltre.
export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.hostname === "smartmoneylab.pages.dev") {
    url.hostname = "smartmoneylab.it";
    url.protocol = "https:";
    return Response.redirect(url.toString(), 301);
  }
  return context.next();
}
