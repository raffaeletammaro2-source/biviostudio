/*
 * API Conversioni di Meta per i moduli Netlify del sito bivio.studio.
 *
 * Netlify esegue questa funzione in automatico a ogni invio verificato di un modulo
 * (evento "submission-created"). La funzione invia a Meta un evento "Lead" dal server,
 * con lo stesso event_id del pixel nel browser: Meta tiene un solo evento (deduplica).
 *
 * Variabili d'ambiente da impostare su Netlify (Site configuration → Environment variables):
 *   META_PIXEL_ID          ID del pixel (3016146428727785)
 *   META_ACCESS_TOKEN      token generato in Gestione eventi → Impostazioni → API Conversioni
 *   META_TEST_EVENT_CODE   facoltativo, solo durante i test (es. TEST12345), poi da rimuovere
 *   META_API_VERSION       facoltativo, versione della Graph API (predefinita v23.0)
 *
 * L'evento parte solo se il visitatore ha dato il consenso marketing nel banner iubenda
 * (campo nascosto "consenso_ads" = "si"), come il pixel.
 */
const crypto = require('crypto');

const FORMS = ['consulenza', 'all-upside-challenge'];

const norm = (v) => (v == null ? '' : String(v).trim().toLowerCase());
const sha256 = (v) => {
  const s = norm(v);
  return s ? crypto.createHash('sha256').update(s).digest('hex') : undefined;
};
const phoneDigits = (v) => {
  let d = String(v || '').replace(/\D/g, '');
  if (!d) return '';
  if (d.startsWith('00')) d = d.slice(2);
  if (!d.startsWith('39') && d.length <= 10) d = '39' + d; // numero italiano senza prefisso
  return d;
};
const clean = (obj) => {
  Object.keys(obj).forEach((k) => (obj[k] === undefined || obj[k] === '') && delete obj[k]);
  return obj;
};

exports.handler = async (event) => {
  try {
    const { payload } = JSON.parse(event.body || '{}');
    if (!payload) return { statusCode: 200, body: 'nessun payload' };

    const formName = payload.form_name || (payload.data && payload.data['form-name']);
    if (!FORMS.includes(formName)) return { statusCode: 200, body: 'modulo ignorato' };

    const d = payload.data || {};
    const PIXEL = process.env.META_PIXEL_ID;
    const TOKEN = process.env.META_ACCESS_TOKEN;
    if (!PIXEL || !TOKEN) {
      console.log('API Conversioni non configurata: mancano META_PIXEL_ID o META_ACCESS_TOKEN');
      return { statusCode: 200, body: 'non configurata' };
    }
    if (d.consenso_ads !== 'si') {
      console.log(`Lead ${d.event_id || ''} non inviato a Meta: consenso marketing assente`);
      return { statusCode: 200, body: 'nessun consenso' };
    }

    // Nome e cognome: campi separati (consulenza) o un unico campo (challenge)
    let first = d.nome, last = d.cognome;
    if (!first && d.nome_cognome) {
      const parts = String(d.nome_cognome).trim().split(/\s+/);
      first = parts.shift();
      last = parts.join(' ');
    }
    const phone = phoneDigits(d.telefono || d.whatsapp);
    const pageUrl = d.referrer || payload.site_url || '';
    const servizio = (String(pageUrl).match(/\/servizi\/([a-z0-9-]+)\.html/) || [])[1];

    const user_data = clean({
      em: sha256(d.email) ? [sha256(d.email)] : undefined,
      ph: phone ? [crypto.createHash('sha256').update(phone).digest('hex')] : undefined,
      fn: sha256(first) ? [sha256(first)] : undefined,
      ln: sha256(last) ? [sha256(last)] : undefined,
      country: [sha256('it')],
      client_ip_address: d.ip || undefined,
      client_user_agent: d.user_agent || undefined,
      fbp: d.fbp || undefined,
      fbc: d.fbc || undefined,
    });

    const metaEvent = clean({
      event_name: 'Lead',
      event_time: Math.floor(Date.now() / 1000),
      event_id: d.event_id || undefined,
      action_source: 'website',
      event_source_url: pageUrl || undefined,
      user_data,
      custom_data: clean({ content_name: formName, content_category: servizio }),
    });

    const body = { data: [metaEvent] };
    if (process.env.META_TEST_EVENT_CODE) body.test_event_code = process.env.META_TEST_EVENT_CODE;

    const version = process.env.META_API_VERSION || 'v23.0';
    const res = await fetch(`https://graph.facebook.com/${version}/${PIXEL}/events?access_token=${encodeURIComponent(TOKEN)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const text = await res.text();
    console.log(`Meta CAPI ${res.status} · ${formName} · ${d.event_id || 'senza event_id'} · ${text}`);
    return { statusCode: 200, body: 'ok' };
  } catch (err) {
    console.log('Errore API Conversioni:', err && err.message);
    return { statusCode: 200, body: 'errore' };
  }
};
