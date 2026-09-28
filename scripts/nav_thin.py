#!/usr/bin/env python3
"""Riduzione della risoluzione delle serie NAV per la pubblicazione.

Perche'
-------
Le serie sono giornaliere. Un grafico su telefono ha circa 350 px utili: a un
anno si e' a 0,7 punti per pixel, a due anni 1,4, a cinque 3,6. Oltre il pareggio
si spedisce al browser piu' dati di quanti lo schermo possa mostrare, e il JSON
cresce senza che si veda nulla in piu' (l'arena passerebbe da 24 KB a 245 KB in
cinque anni).

Regola: dettaglio pieno dove serve, sintesi dove non si vedrebbe comunque.
  - ultimi GIORNI_PIENI giorni: ogni seduta
  - piu' indietro: ultima seduta di ogni settimana
  - oltre ANNI_SETTIMANALI anni: ultima seduta di ogni mese
Primo punto, ultimo punto e le date marcate (riallocazioni, ribilanci) restano
sempre, perche' sono gli estremi e gli eventi del grafico.

ATTENZIONE: questa funzione serve SOLO alla visualizzazione. Volatilita', Sharpe
e soprattutto il massimo drawdown vanno calcolati sulla serie giornaliera
completa: su dati settimanali il minimo di un crollo sparisce e si pubblicherebbe
un drawdown piu' piccolo del vero.
"""
import datetime as dt

GIORNI_PIENI = 90          # finestra a risoluzione giornaliera
ANNI_SETTIMANALI = 2       # oltre questa eta' si passa al mensile


def thin(dates, tieni=(), giorni_pieni=GIORNI_PIENI, anni_settimanali=ANNI_SETTIMANALI,
         oggi=None):
    """Sottoinsieme di date da pubblicare. Ritorna un set di stringhe ISO."""
    if not dates:
        return set()
    ds = sorted(set(dates))
    oggi = dt.date.fromisoformat(oggi) if oggi else dt.date.fromisoformat(ds[-1])
    limite_giorni = oggi - dt.timedelta(days=giorni_pieni)
    limite_mesi = oggi - dt.timedelta(days=int(365.25 * anni_settimanali))

    # per ogni bucket (settimana o mese) si tiene l'ULTIMA seduta: e' la
    # chiusura di periodo, la convenzione di qualunque grafico finanziario
    ultimo_di = {}
    for s in ds:
        d = dt.date.fromisoformat(s)
        if d >= limite_giorni:
            continue
        chiave = (d.year, d.month) if d < limite_mesi else d.isocalendar()[:2]
        ultimo_di[chiave] = s

    out = {s for s in ds if dt.date.fromisoformat(s) >= limite_giorni}
    out |= set(ultimo_di.values())
    out |= {ds[0], ds[-1]}
    out |= {s for s in tieni if s in set(ds)}
    return out


def thin_pairs(serie, tieni=(), **kw):
    """serie: lista di (data, valore) o [data, valore]. Ritorna la lista ridotta."""
    keep = thin([p[0] for p in serie], tieni, **kw)
    return [p for p in serie if p[0] in keep]


def thin_dicts(serie, campo="d", tieni=(), **kw):
    """serie: lista di dict con la data nel campo indicato."""
    keep = thin([p[campo] for p in serie], tieni, **kw)
    return [p for p in serie if p[campo] in keep]
