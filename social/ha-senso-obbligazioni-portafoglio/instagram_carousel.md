# Carosello Instagram — Ha ancora senso inserire obbligazioni in portafoglio?

**Account**: @smartmoneylab_it
**Numero slide**: 8 (Cover + 6 contenuto + CTA finale)
**Formato**: 1080×1350 px (4:5, ottimale per il feed IG)
**Palette**: navy (#1e3a8a) come accento, sfondo bianco / dark navy alternato per ritmo visivo
**Tipografia**: Inter / sans-serif sobria, gerarchia chiara (titolo 56-64pt, corpo 32-36pt)
**Strumento di produzione**: Canva o Figma. Esportare in PNG ad alta risoluzione.

---

## Slide 1 — COVER

**Background**: navy scuro pieno (#1e3a8a)
**Testo principale (centrato, bianco, 64pt bold)**:

> Ha ancora senso
> avere obbligazioni
> in portafoglio?

**Sottotitolo (sotto, 28pt, bianco/slate-200)**:

> 25 anni di dati. 3 portafogli a confronto.
> La risposta non è quella delle banche.

**Footer (in fondo, 18pt, slate-300)**: smartmoneylab.pages.dev

**Indizio visivo (top right corner)**: piccolo logo SML su sfondo trasparente

---

## Slide 2 — IL DOGMA E LA DOMANDA

**Background**: bianco sporco (#f8fafc)
**Titolo (38pt, navy, allineato a sinistra)**:

> Il dogma del 60/40

**Corpo (24pt, slate-700)**:

> Per decenni il consulente standard ha proposto la stessa cosa:
> 60% azioni, 40% obbligazioni.
>
> Dopo il 2022 — quando azioni e bond sono crollati insieme — qualcuno ha detto che è morto.
>
> **Ma cosa dicono davvero i numeri?**

---

## Slide 3 — IL METODO

**Background**: navy chiaro (#dbeafe)
**Titolo (38pt, navy)**: Il metodo

**Corpo (testo strutturato a punti, 22pt)**:

> 25 anni di dati: 2001-2025
>
> 3 portafogli BUY & HOLD:
> ⬛ 100% azionario (S&P 500)
> ⬛ 60/40
> ⬛ 40/60
>
> Niente rebalancing → niente costi di transazione da inventare.
>
> Confronto su TUTTE le finestre 5y e 10y, step 3 mesi.
> Non un singolo punto di partenza cherry-picked.

**Footer**: piccolo box "Codice Python pubblico → smartmoneylab.pages.dev"

---

## Slide 4 — RISULTATI 10 ANNI

**Background**: bianco
**Titolo (38pt, navy)**: A 10 anni l'azionario domina in mediana

**Corpo principale**:

> CAGR mediano su finestre rolling 10y:
>
> 100% azionario: 10.09%
> 60/40: 7.73%
> 40/60: 6.24%

**Sotto, riquadro evidenziato (sfondo navy chiaro, testo navy bold)**:

> Spread ~2.4 punti l'anno tra 100E e 60/40.
> Su 30 anni di accumulo: 1€ → 17.7€ col 100E,
> 9.3€ col 60/40.
> Il 60/40 finisce con circa metà del capitale.

**Visivo**: includere o riprodurre il grafico 01_boxplot_cagr_10y.png in basso

---

## Slide 5 — LA SORPRESA NEI P5

**Background**: bianco
**Titolo (38pt, navy)**: Ma nelle 10y peggiori il quadro si capovolge

**Corpo (24pt, slate-700)**:

> 5° percentile del CAGR a 10 anni:
>
> 100% azionario: 3.10%
> 60/40: 4.05%
> 40/60: **4.50%**

**Riquadro highlight (sfondo navy chiaro)**:

> Nelle finestre 10y peggiori — quelle che includono dot-com + GFC ravvicinati — i portafogli più obbligazionari hanno VINTO il pure-equity in CAGR finale.
>
> Non è solo questione di volatilità. È un risultato vero.

---

## Slide 6 — IL VERO MOTIVO: DRAWDOWN

**Background**: navy scuro (#1e3a8a), testo bianco
**Titolo (44pt bianco bold)**: Il punto è il viaggio, non l'arrivo

**Corpo (24pt, bianco)**:

> % di finestre 10y con drawdown peggiore del -30%:
>
> 100% azionario → 51.7%
> 60/40 → 0%
> 40/60 → 0%

**Riquadro highlight (sfondo blu più chiaro, testo bianco)**:

> Nella metà delle finestre 10y il pure-equity ha visto un drawdown peggiore del -30%.
>
> Il 60/40 in nessuna. Mai.

---

## Slide 7 — QUANDO HANNO SENSO

**Background**: bianco
**Titolo (38pt, navy)**: Quando hanno senso davvero

**Due colonne**:

**Colonna sinistra**:
> ✓ Hanno senso se:
> • capitale ti serve in 5-7 anni
> • stai entrando in decumulo
> • -40% comprometterebbe il piano
> • sei un investitore mentalmente "corto"

**Colonna destra (slate-400)**:
> ✗ Hanno meno senso se:
> • ti mancano 15+ anni
> • versi regolarmente
> • sopporti la volatilità
> • il piano è di accumulo puro

**Footer (24pt, navy, allineato centro)**:
> Non sono uno strumento di rendimento.
> Sono uno strumento di copertura sul percorso.

---

## Slide 8 — CTA

**Background**: navy scuro (#1e3a8a)
**Titolo (44pt, bianco bold)**:

> L'analisi completa è sul blog

**Corpo (28pt, bianco)**:

> + Tabelle complete dei percentili
> + Il sequence-of-returns risk
> + Il concetto di glide path
> + Codice Python riproducibile

**Mega CTA (in basso, 36pt bianco bold, su underline)**:

> smartmoneylab.pages.dev
> @smartmoneylab_it

**Footer minimo (18pt slate-300)**: SmartMoneyLab — Finanza personale e analisi quantitativa

---

## Note operative

- **Coerenza visiva tra slide**: stesso footer minimal, stessa palette, stessi font weight.
- **Ritmo**: alternare sfondi chiari e scuri (1 dark, 2-5 light, 6 dark, 7 light, 8 dark) — in feed crea pattern visivo.
- **Densità testo**: tenere ogni slide leggibile in 3-4 secondi. Se una slide è troppo piena, splittare in due.
- **Grafici nelle slide 4 e 6**: ridisegnarli in Canva con la stessa palette delle slide, NON usare il PNG generato da matplotlib direttamente (i caratteri di matplotlib stonano col resto). Riprodurre solo lo schema, mantenendo l'accuratezza visiva.
- **Hashtag**: NON nel carosello (vanno solo nella caption).
- **Tag account**: nessun tag salvo @smartmoneylab_it nella slide CTA.
