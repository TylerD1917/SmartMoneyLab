/**
 * /api/fred/[series]
 *
 * Cloudflare Pages Function che fa da proxy per gli endpoint CSV pubblici
 * di FRED (Federal Reserve Bank of St. Louis). Serve al FedRegimeMonitor
 * per aggirare il blocco CORS che FRED impone quando il fetch avviene
 * direttamente dal browser dell'utente.
 *
 * Perche' esiste:
 *   - Il browser blocca il fetch cross-origin verso fred.stlouisfed.org.
 *   - Server-side (Cloudflare Worker/Pages Function) il CORS non si applica.
 *   - Aggiungiamo noi gli header Access-Control-Allow-Origin: * nella risposta,
 *     cosi' il browser accetta i dati come se venissero dal nostro dominio.
 *
 * Sicurezza:
 *   - Whitelist esplicita delle serie ammesse. Non permettiamo che qualcuno
 *     usi questa function per proxyare traffico arbitrario.
 *
 * Cache:
 *   - FRED aggiorna FEDFUNDS e CPIAUCSL mensilmente. Cache 12 ore all'edge
 *     e' abbondante e riduce le richieste in uscita.
 *
 * Endpoint:
 *   GET /api/fred/FEDFUNDS  -> https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS
 *   GET /api/fred/CPIAUCSL  -> stesso pattern
 *
 * Autore: SmartMoneyLab - 2026.
 */

const ALLOWED_SERIES = new Set(["FEDFUNDS", "CPIAUCSL"]);
const CACHE_MAX_AGE_SECONDS = 60 * 60 * 12; // 12h

export async function onRequestGet(context) {
  const { params } = context;
  const series = String(params.series || "").toUpperCase();

  if (!ALLOWED_SERIES.has(series)) {
    return new Response(
      `Series not allowed. Allowed: ${[...ALLOWED_SERIES].join(", ")}`,
      { status: 400, headers: corsHeaders() }
    );
  }

  const upstream = `https://fred.stlouisfed.org/graph/fredgraph.csv?id=${series}`;

  try {
    const upstreamResp = await fetch(upstream, {
      // Cloudflare edge cache per default; forziamo comportamento cacheable.
      cf: { cacheTtl: CACHE_MAX_AGE_SECONDS, cacheEverything: true },
      headers: { "User-Agent": "SmartMoneyLab/1.0 (+https://smartmoneylab.pages.dev)" },
    });

    if (!upstreamResp.ok) {
      return new Response(
        `FRED upstream error: ${upstreamResp.status} ${upstreamResp.statusText}`,
        { status: 502, headers: corsHeaders() }
      );
    }

    const csv = await upstreamResp.text();
    return new Response(csv, {
      status: 200,
      headers: {
        ...corsHeaders(),
        "Content-Type": "text/csv; charset=utf-8",
        "Cache-Control": `public, max-age=${CACHE_MAX_AGE_SECONDS}`,
      },
    });
  } catch (e) {
    return new Response(
      `Proxy fetch failed: ${e?.message || String(e)}`,
      { status: 502, headers: corsHeaders() }
    );
  }
}

// Preflight (utile se in futuro passiamo a POST o custom headers)
export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: corsHeaders() });
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}
