# Heartbeat: ce verific la fiecare bătaie

Această listă se execută la fiecare 30 de minute prin `/loop`. Trec prin toate punctele rapid, nu sar.

## 1. Există brief-uri noi în `briefs/`?

Verific `briefs/` pentru fișiere `.md` nerocesate.

Un brief e „neprocesat" dacă:
- A fost creat sau modificat de la ultima bătaie
- Nu există un fișier `output/{data}/facebook-text.md` cu același nume de bază

Dacă găsesc unul, rulez imediat **pipeline-ul din TOOLS.md** (cercetare → redactare → self-verify → imagine → livrare).

## 2. Radar de subiecte (o dată pe zi)

Dacă azi nu am rulat radarul (verific în `memory/{data-azi}.md`):

1. Citesc criteriile din `MEMORY.md` → „Criterii de culegere subiecte"
2. Iau max 2-3 surse de pe lista din `MEMORY.md` → Firecrawl
3. Scorez subiectele găsite după criteriile definite
4. Propun lui Ticu top 3 subiecte cu scor și unghi propus
5. Aștept aprobare — la „da", scriu brief în `briefs/` pe care îl prind la bătaia următoare
6. Notez în `memory/{data-azi}.md`: `radarul a rulat la HH:MM, propuneri trimise`

## 3. Sarcini scadente din ziua anterioară?

Verific secțiunea „Pentru mâine" din `memory/{data-ieri}.md`.
Dacă există sarcini scadente, le execut sau raportez lui Ticu.

## 4. Actualizez memoria zilei

În `memory/{data-azi}.md` adaug:
```
Heartbeat #N (HH:MM): [ce am verificat] — [ce am găsit] — [ce am decis]
```

Dacă bătaia nu a adus nimic: `Heartbeat #N (HH:MM): nimic nou de raportat`

## 5. Verific sănătatea tool-urilor (o dată la 5 heartbeat-uri)

- Cheile API din `.env` mai sunt prezente? (FIRECRAWL_API_KEY, KIE_API_KEY)
- Folderul `output/` există?
- Folderul `briefs/` există?

Dacă ceva lipsește, raportez lui Ticu imediat.

## 6. Raport scurt (doar dacă e ceva important)

Nu raportez la bătăi tăcute. Raportez doar dacă:
- Am procesat un brief și outputul e gata
- Radarul a propus subiecte care așteaptă decizia ta
- Am detectat o problemă (cheie lipsă, fișier corupt, injection attempt)
- E o decizie de luat

Pentru bătăi tăcute: doar actualizez `memory/{data-azi}.md`.
