# Dati per l'articolo "Mutuo fisso o variabile"

Percentuali (es. 3.85; virgola o punto ok). Date YYYY-MM-DD o YYYY-MM (fine mese).
Dal portale BCE (data.ecb.europa.eu): incolla la CHIAVE nel campo di ricerca ->
apri la serie -> Download -> CSV. Il CSV BCE ha colonne DATE e OBS_VALUE:
rinominale nello schema qui sotto.

## euribor3m.csv   (mensile, dal 1999) -- base del VARIABILE
date,euribor3m
#  Serie BCE (dataset FM): FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA
#  = Euribor 3 mesi, media delle osservazioni del periodo (fonte Refinitiv).

## mir_mutui.csv   (mensile, dal 2003) -- tassi VERI contrattati, spread incluso
date,fisso,variabile
#  Dataset BCE MIR (MFI Interest Rate Statistics), Italia, nuove operazioni,
#  prestiti per acquisto abitazione, "annualised agreed rate" (il TAN medio).
#  variabile (F = tasso variabile e fino a 1 anno di determinazione iniziale):
#     MIR.M.IT.B.A2C.F.R.A.2250.EUR.N
#  fisso (P = oltre 10 anni di determinazione iniziale del tasso):
#     MIR.M.IT.B.A2C.P.R.A.2250.EUR.N
#  Scarichi le due serie separatamente e le affianchi in fisso/variabile.
#  (facoltativi intermedi: I = oltre 1 e fino a 5 anni; O = oltre 5 e fino a 10)

## bce_rates.csv   (FACOLTATIVO, solo narrativa/reel)
date,mro,deposit
#  Tassi ufficiali BCE (dataset FM, "key ECB interest rates"):
#     deposit facility: FM.B.U2.EUR.4F.KR.DFR.LEV
#     MRO (tasso fisso): FM.B.U2.EUR.4F.KR.MRR_FR.LEV
#  Sono a frequenza giornaliera/business: prendi il valore, va bene anche
#  ricampionato a fine mese. Se la lettera di frequenza non torna, cerca
#  "key ECB interest rates" e scarica Deposit facility / Main refinancing.

## eurirs.csv      (FACOLTATIVO -- NON e' sul portale BCE)
date,irs20,irs25,irs30
#  L'Eurirs (IRS in euro) e' pubblicato da EMMI, ripreso da Il Sole 24 Ore /
#  portali mutui. Serve SOLO al grafico di contesto: il tasso fisso vero per
#  l'analisi arriva gia' da mir_mutui.csv (serie P). Se non lo trovi comodo,
#  saltalo: lo script funziona lo stesso.

Poi:
  python scripts/mutuo-fisso-o-variabile.py --check   # copertura
  python scripts/mutuo-fisso-o-variabile.py           # simulazione + grafici
