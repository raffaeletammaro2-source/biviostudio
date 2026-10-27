(function(){
  // Dove inviare le richieste del modulo.
  // "/" = Netlify Forms (il sito deve essere pubblicato su Netlify con il rilevamento dei moduli attivo).
  // In alternativa: l'URL di un webhook Make/Zapier o di Web3Forms/Formspree.
  var ENDPOINT = "/";
  // In anteprima locale o su Claude non c'è un server che riceve: si mostra solo il riepilogo.
  var PREVIEW = location.protocol === 'file:' || /claude|anthropic/i.test(location.hostname);
  // Solo per Web3Forms: incolla qui la tua access key (per gli altri servizi lascia vuoto).
  var ACCESS_KEY = "";
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function(s,r){return (r||document).querySelector(s)}, $$ = function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};

  /* Menu: tendina servizi e menu mobile */
  $$('.dd').forEach(function(dd){
    var b = dd.querySelector('button');
    b.addEventListener('click', function(e){ e.stopPropagation(); var o = !dd.classList.contains('open'); dd.classList.toggle('open', o); b.setAttribute('aria-expanded', o); });
    document.addEventListener('click', function(e){ if(!dd.contains(e.target)){ dd.classList.remove('open'); b.setAttribute('aria-expanded', false); } });
    dd.addEventListener('keydown', function(e){ if(e.key==='Escape'){ dd.classList.remove('open'); b.focus(); } });
  });
  var burger = $('.burger'), mnav = $('#mnav');
  if(burger && mnav){
    burger.addEventListener('click', function(){
      var open = mnav.hidden; mnav.hidden = !open; burger.setAttribute('aria-expanded', open);
      burger.innerHTML = open ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18"/></svg>' : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
      document.body.style.overflow = open ? 'hidden' : '';
    });
    $$('a', mnav).forEach(function(a){ a.addEventListener('click', function(){ mnav.hidden = true; document.body.style.overflow=''; burger.setAttribute('aria-expanded', false); burger.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'; }); });
  }

  /* Hero: spotlight + parallax monogramma */
  var hero = $('.hero'), layers = $$('.mono-stage .layer');
  if(!reduce && hero){
    hero.addEventListener('pointermove', function(e){
      var r = hero.getBoundingClientRect(), x = (e.clientX - r.left)/r.width, y = (e.clientY - r.top)/r.height;
      hero.style.setProperty('--mx', (x*100)+'%'); hero.style.setProperty('--my', (y*100)+'%');
      layers.forEach(function(l){var d=+l.dataset.depth; l.style.transform='translate('+((x-.5)*d)+'px,'+((y-.5)*d)+'px)';});
    });
  }

  /* Bottoni magnetici */
  if(!reduce && matchMedia('(hover:hover)').matches){
    $$('.magnet').forEach(function(b){
      b.addEventListener('pointermove', function(e){var r=b.getBoundingClientRect();b.style.transform='translate('+((e.clientX-r.left-r.width/2)*.18)+'px,'+((e.clientY-r.top-r.height/2)*.3)+'px)';});
      b.addEventListener('pointerleave', function(){b.style.transform='';});
    });
  }

  /* Il bivio: due strade */
  var panel = $('#roads'), sw = $('.road-switch'), autoplay = !reduce;
  if(panel && sw){
    var roads = {
      a:{title:'Più budget, stesso caos.', v:{lead:[88,'+120%','#14161B'],lost:[72,'+65%','#D93A2B'],ore:[90,'+40%','#D93A2B'],sales:[28,'+5%','#14161B']}, ic:'✕', txt:'Si conclude che "le ads non funzionano", quando il limite era dentro l\'azienda.'},
      b:{title:'Prima la struttura, poi la spinta.', v:{lead:[76,'+90%','#7C5CFF'],lost:[10,'−70%','#1F9D6B'],ore:[34,'−35%','#1F9D6B'],sales:[82,'+60%','#FF5B1F']}, ic:'✓', txt:'Ogni lead viene seguito, il team lavora meglio e il budget va dove il ritorno è dimostrato.'}
    };
    var setRoad = function(k){
      var d = roads[k]; panel.dataset.road = k; sw.dataset.road = k;
      $('#road-a').setAttribute('aria-pressed', k==='a'); $('#road-b').setAttribute('aria-pressed', k==='b');
      $('#road-title').textContent = d.title; $('#v-ic').textContent = d.ic; $('#v-txt').textContent = d.txt;
      Object.keys(d.v).forEach(function(m){
        var bar = $('[data-k="'+m+'"]'); bar.style.setProperty('--w', d.v[m][0]+'%'); bar.style.setProperty('--col', d.v[m][2]);
        $('[data-v="'+m+'"]').textContent = d.v[m][1];
      });
    };
    $$('.road-switch button').forEach(function(b){b.addEventListener('click', function(){setRoad(b.dataset.r); autoplay=false;});});
    setRoad('a');
    if('IntersectionObserver' in window){
      var shown=false;
      new IntersectionObserver(function(es){es.forEach(function(e){
        if(e.isIntersecting && !shown){shown=true; setTimeout(function(){ if(autoplay){ setRoad('b'); } }, 1600);}
      });},{threshold:.5}).observe(panel);
    }
  }

  /* Sintomi */
  var syms = $$('.sym');
  if(syms.length){
    var msgs = ['Seleziona i sintomi per vedere da dove partire.',
      'Un segnale da non ignorare. In consulenza vediamo se è un caso isolato.',
      'Due sintomi: probabilmente c\'è un collo di bottiglia nei processi.',
      'Tre sintomi: prima di spingere sulle ads serve la Fase 01, Struttura.',
      'Quattro sintomi: il sistema va costruito. Parliamone in una call gratuita.',
      'Cinque su cinque: sei al bivio. È il momento di scegliere la strada giusta.'];
    syms.forEach(function(s){s.addEventListener('click', function(){
      s.setAttribute('aria-pressed', s.getAttribute('aria-pressed')!=='true');
      var n = syms.filter(function(x){return x.getAttribute('aria-pressed')==='true'}).length;
      $('#sc').textContent = n; $('#sc-t').textContent = msgs[n];
    });});
  }

  /* Linea del metodo */
  var ph = $('#phases');
  function track(){
    if(!ph) return;
    var r = ph.getBoundingClientRect(), vh = innerHeight;
    var p = Math.min(1, Math.max(0, (vh*.8 - r.top) / (r.height*.9)));
    ph.style.setProperty('--p', reduce ? 1 : p.toFixed(3));
  }
  if(ph){
    var vert = matchMedia('(max-width:900px)');
    var orient = function(){
      var svg = $('.track-line svg'), bg=$('.track-line .bg'), fg=$('.track-line .fg');
      if(vert.matches){svg.setAttribute('viewBox','0 0 4 1000');[bg,fg].forEach(function(l){l.setAttribute('x1',2);l.setAttribute('x2',2);l.setAttribute('y1',0);l.setAttribute('y2',1000);});fg.setAttribute('stroke','url(#gradv)');}
      else{svg.setAttribute('viewBox','0 0 1000 4');[bg,fg].forEach(function(l){l.setAttribute('x1',0);l.setAttribute('x2',1000);l.setAttribute('y1',2);l.setAttribute('y2',2);});fg.setAttribute('stroke','url(#grad)');}
    };
    orient(); vert.addEventListener && vert.addEventListener('change', orient);
  }

  /* Indice articolo + barra di lettura */
  var tocLinks = $$('.toc a[href^="#"]'), art = $('.art-body'), prog = $('.read-prog');
  function artScroll(){
    if(art && prog){ var r = art.getBoundingClientRect(); var p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height - innerHeight*.6))); prog.style.setProperty('--rp', p.toFixed(3)); }
    if(tocLinks.length){
      var cur = null;
      tocLinks.forEach(function(a){ var h = document.getElementById(a.getAttribute('href').slice(1)); if(h && h.getBoundingClientRect().top < 140) cur = a; });
      tocLinks.forEach(function(a){ a.classList.toggle('on', a===cur); });
    }
  }

  /* Filtri blog */
  var fbtns = $$('.filters button');
  fbtns.forEach(function(b){ b.addEventListener('click', function(){
    fbtns.forEach(function(x){ x.setAttribute('aria-pressed', x===b); });
    var c = b.dataset.cat;
    $$('.posts .post').forEach(function(p){ p.hidden = !(c==='all' || p.dataset.cat===c); });
  }); });

  /* Barra CTA mobile */
  var mbar = $('#mbar'), formSec = $('#consulenza'), ticking=false;
  function onScroll(){
    if(ticking) return; ticking=true;
    requestAnimationFrame(function(){
      track(); artScroll();
      if(mbar){
        var inForm = false;
        if(formSec){ var fr = formSec.getBoundingClientRect(); inForm = fr.top < innerHeight && fr.bottom > 0; }
        mbar.classList.toggle('show', scrollY > 500 && !inForm);
      }
      ticking=false;
    });
  }
  addEventListener('scroll', onScroll, {passive:true}); addEventListener('resize', onScroll); onScroll();

  /* Modulo a step */
  var form = $('#lead');
  if(!form) return;
  var steps = $$('.fstep', form), cur = 0;
  var prev = $('#prev'), next = $('#next'), bars = $$('.progress span');
  var KEY = 'bivio_lead_draft';

  function fieldOk(el){
    var v = (el.value||'').trim();
    if(el.required && !v) return false;
    if(el.type==='email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return false;
    if(el.type==='tel' && v && v.replace(/\D/g,'').length < 8) return false;
    if(el.id==='problema' && v.length < 20) return false;
    return true;
  }
  function validate(i){
    var ok = true, first = null;
    $$('input:not([type=radio]):not([type=checkbox]), select, textarea', steps[i]).forEach(function(el){
      var f = el.closest('.field'); var good = fieldOk(el);
      if(f) f.classList.toggle('bad', !good);
      if(!good){ ok=false; first = first || el; }
    });
    $$('.group[data-req]', steps[i]).forEach(function(g){
      var name = g.dataset.req, good = !!form.querySelector('[name="'+name+'"]:checked');
      g.classList.toggle('bad', !good);
      if(!good){ ok=false; first = first || g.querySelector('input'); }
    });
    if(first) first.focus({preventScroll:false});
    return ok;
  }
  form.addEventListener('input', function(e){
    var f = e.target.closest('.field'); if(f && f.classList.contains('bad') && fieldOk(e.target)) f.classList.remove('bad');
    var g = e.target.closest('.group'); if(g && g.classList.contains('bad') && e.target.checked) g.classList.remove('bad');
    saveDraft();
  });
  form.addEventListener('change', saveDraft);

  function show(i, back){
    steps[cur].classList.remove('on','back');
    cur = i;
    steps[cur].classList.add('on'); if(back) steps[cur].classList.add('back');
    bars.forEach(function(b,j){b.classList.toggle('done', j<=cur);});
    $('#stepn').textContent = cur+1; $('#stepname').textContent = steps[cur].dataset.name;
    prev.hidden = cur===0;
    next.innerHTML = cur===steps.length-1 ? 'Richiedi la consulenza <span class="arr">→</span>' : 'Continua <span class="arr">→</span>';
    var top = $('.fcard').getBoundingClientRect().top;
    if(top < 70) scrollBy({top: top-90, behavior: reduce?'auto':'smooth'});
  }
  next.addEventListener('click', function(){
    if(!validate(cur)) return;
    if(cur < steps.length-1) show(cur+1); else submit();
  });
  prev.addEventListener('click', function(){ if(cur>0) show(cur-1, true); });
  form.addEventListener('submit', function(e){ e.preventDefault(); next.click(); });
  form.addEventListener('keydown', function(e){
    if(e.key==='Enter' && e.target.tagName!=='TEXTAREA' && e.target.type!=='checkbox' && e.target.type!=='radio'){ e.preventDefault(); next.click(); }
  });

  function collect(){
    var data = {}, fd = new FormData(form);
    fd.forEach(function(v,k){ if(data[k]){ data[k] = [].concat(data[k], v); } else data[k] = v; });
    return data;
  }
  function saveDraft(){
    try{ localStorage.setItem(KEY, JSON.stringify(collect())); $('#saved').textContent = 'Bozza salvata su questo dispositivo'; }catch(e){}
  }
  function loadDraft(){
    var d; try{ d = JSON.parse(localStorage.getItem(KEY)||'null'); }catch(e){ d=null; }
    if(!d) return;
    var pre = form.dataset.pre;
    Object.keys(d).forEach(function(k){
      var vals = [].concat(d[k]);
      $$('[name="'+k+'"]', form).forEach(function(el){
        if(el.type==='radio'||el.type==='checkbox'){ el.checked = vals.indexOf(el.value) > -1 || (k==='servizi' && el.value===pre); }
        else el.value = vals[0];
      });
    });
  }
  loadDraft();

  var labels = {nome:'Nome',cognome:'Cognome',ruolo:'Ruolo',email:'Email',telefono:'Telefono',contatto:'Contatto preferito',fascia:'Fascia oraria',azienda:'Azienda',sito:'Sito / social',settore:'Settore',citta:'Città',modello:'Clienti',dipendenti:'Persone',fatturato:'Fatturato',anni_attivita:'Attività da',obiettivo:'Obiettivo',servizi:'Servizi di interesse',canali:'Canali attivi',gestione_contatti:'Gestione contatti',spesa_ads:'Spesa ads attuale',budget:'Budget previsto',tempistiche:'Partenza',fonte:'Ci ha conosciuto tramite'};
  function submit(){
    var fp = $('#f-pagina'), fd = $('#f-data');
    if(fp) fp.value = document.title + ' (' + location.pathname + ')';
    if(fd) fd.value = new Date().toLocaleString('it-IT', {dateStyle:'short', timeStyle:'short'});
    var data = collect();
    var done = function(sent){
      var rc = $('#recap'); rc.innerHTML='';
      ['nome','azienda','email','telefono','contatto','settore','obiettivo','servizi','budget','tempistiche'].forEach(function(k){
        if(!data[k]) return;
        var row = document.createElement('div'), dt=document.createElement('dt'), dd=document.createElement('dd');
        dt.textContent = labels[k]; dd.textContent = k==='nome' ? data.nome+' '+data.cognome : [].concat(data[k]).join(', ');
        row.appendChild(dt); row.appendChild(dd); rc.appendChild(row);
      });
      $('#ok-title').textContent = 'Grazie '+data.nome+'! Hai fatto la scelta giusta.';
      $('#pnote').hidden = sent;
      form.hidden = true; $('#success').classList.add('on');
      try{ localStorage.removeItem(KEY); }catch(e){}
      var t = $('.fcard').getBoundingClientRect().top; if(t<70) scrollBy({top:t-90,behavior:reduce?'auto':'smooth'});
    };
    if(!ENDPOINT || PREVIEW){ done(false); return; }
    if(data['bot-field']){ done(true); return; }
    next.disabled = true; next.textContent = 'Invio in corso…';
    // Invio come modulo standard: niente preflight CORS, accettato da Make, Zapier, Web3Forms e Formspree.
    var body = new URLSearchParams();
    Object.keys(data).forEach(function(k){ body.append(k, [].concat(data[k]).join(', ')); });
    if(ACCESS_KEY){ body.append('access_key', ACCESS_KEY); body.append('subject', 'Nuova richiesta di consulenza: ' + (data.azienda || data.nome)); body.append('from_name', 'Sito bivio.studio'); }
    if(data.email && ENDPOINT !== '/'){ body.append('replyto', data.email); }
    var fail = function(){ next.disabled=false; next.innerHTML='Riprova <span class="arr">→</span>'; $('#saved').textContent='Invio non riuscito. Controlla la connessione e riprova, oppure chiamaci allo 081 185 22008.'; };
    fetch(ENDPOINT,{method:'POST',headers:{'Accept':'application/json'},body:body})
      .then(function(r){ if(!r.ok) throw new Error('http'); done(true); })
      .catch(function(err){
        if(err && err.message==='http'){ fail(); return; }
        // Se si è offline l'invio è fallito. Altrimenti il servizio ha ricevuto la richiesta
        // ma non ha permesso di leggere la risposta (CORS): la consideriamo inviata, senza duplicarla.
        if(navigator.onLine === false){ fail(); return; }
        done(true);
      });
  }
  $('#again').addEventListener('click', function(){
    form.reset(); form.hidden = false; $('#success').classList.remove('on'); show(0, true); $('#saved').textContent='';
  });
})();
