# bivio.studio — sito web

Sito statico di bivio.studio, Growth Marketing Agency per PMI ed e-commerce in tutta Italia.

## Struttura

```
index.html              Home (con modulo di consulenza)
servizi/index.html      L'ecosistema dei 10 servizi
servizi/*.html          Pagine dei singoli servizi
blog/index.html         Elenco articoli con filtri
blog/*.html             20 articoli (2 per servizio)
assets/bivio.css        Stili condivisi
assets/bivio.js         Animazioni, menu e modulo a step
sitemap.xml             Sitemap per i motori di ricerca
robots.txt              Accesso a motori di ricerca e crawler AI
llms.txt                Scheda dell'agenzia per gli assistenti AI
sorgenti/               Generatore del sito (non serve pubblicarlo)
```

Il sito non ha dipendenze né build obbligatoria: si pubblica così com'è su qualsiasi hosting statico (GitHub Pages, Netlify, Vercel, hosting tradizionale).

## Modificare i contenuti

Testi di servizi e articoli si trovano in `sorgenti/`:

- `services.py` — le 10 pagine servizio (testi, FAQ, problemi, servizi collegati)
- `articles1.py`, `articles2.py` — gli articoli del blog
- `source_home.html` — le sezioni della home
- `extra.css`, `bivio.js` — stili aggiuntivi e script

Dopo una modifica, rigenera tutte le pagine dalla cartella principale del repo:

```bash
python3 sorgenti/build.py
```

## Da completare prima della messa online

- **Dominio**: gli URL canonici, la sitemap e i dati strutturati usano `https://www.biviostudio.it/`. Se il dominio è diverso, cambia `BASE` in `sorgenti/build.py` e rigenera.
- **Modulo di contatto**: in `assets/bivio.js` (e in `sorgenti/bivio.js`) inserisci l'URL del webhook o del CRM nella variabile `ENDPOINT`. Finché è vuota, il modulo mostra il riepilogo ma non invia la richiesta.
- **Dati legali**: P.IVA, privacy policy e cookie policy nel footer.
- **Immagine di anteprima** per le condivisioni social (`og:image`).
