# bivio.studio — sito web

Sito statico di bivio.studio, Growth Marketing Agency per PMI ed e-commerce in tutta Italia.

## Struttura

```
index.html              Home (con modulo di consulenza)
all-upside-challenge.html  Landing della All Upside Challenge (con modulo di candidatura)
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
- `all-upside-challenge.html` — la landing della challenge; `build.py` aggiunge SEO, link al sito e collegamento a Netlify Forms

Dopo una modifica, rigenera tutte le pagine dalla cartella principale del repo:

```bash
python3 sorgenti/build.py
```

## Da completare prima della messa online

- **Dominio**: gli URL canonici, la sitemap e i dati strutturati usano `https://www.biviostudio.it/`. Se il dominio è diverso, cambia `BASE` in `sorgenti/build.py` e rigenera.
- **Moduli (Netlify Forms)**: i moduli sono due, `consulenza` (home, servizi, blog) e `all-upside-challenge` (landing della challenge). Entrambi sono già configurati per Netlify (`data-netlify="true"`, campo nascosto `form-name`, honeypot anti-spam). Su Netlify attiva *Site configuration → Forms → Enable form detection*, poi rifai il deploy. Le notifiche si impostano in *Forms → Form notifications*.
- **Altri servizi**: in alternativa, in `sorgenti/bivio.js` inserisci l'indirizzo del webhook (Make, Zapier) o del servizio di invio (Web3Forms, Formspree) nella variabile `ENDPOINT`, e per Web3Forms la chiave in `ACCESS_KEY`. Poi rigenera con `python3 sorgenti/build.py`. Finché `ENDPOINT` è vuota, il modulo mostra il riepilogo ma non invia la richiesta. I dati arrivano come modulo standard (form-urlencoded), con un campo per ogni domanda.
- **Immagine di anteprima** per le condivisioni social (`og:image`).

## Tracciamento (Google Tag Manager)

Contenitore GTM: `GTM-MSNJJSQV` (in `GTM_ID` in `sorgenti/build.py`). Lo snippet viene aggiunto in tutte le pagine subito dopo il banner cookie di iubenda.

Il sito invia questi eventi al `dataLayer`:

| Evento | Quando | Parametri |
|---|---|---|
| `cta_click` | clic su un pulsante verso il modulo o la challenge | `cta_text`, `cta_location`, `cta_destination`, `page_type` |
| `contact_click` | clic su telefono, WhatsApp o email | `contact_method` |
| `form_start` | primo campo compilato | `form_name`, `page_type`, `service` |
| `form_step` | passaggio allo step successivo (modulo consulenza) | `form_name`, `form_step`, `form_step_name` |
| `generate_lead` | richiesta inviata con successo | `form_name` (`consulenza` o `all-upside-challenge`), `event_id`, `page_type`, `service`, `settore`, `obiettivo`, `budget`, `spesa_ads`, `user_data` (email, telefono, nome per Enhanced Conversions e Advanced Matching) |
