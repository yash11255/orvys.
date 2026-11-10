(function () {
  // Loading screen: hide on load, max 1.2s
  var root = document.documentElement;
  function hideLoader() { root.classList.add('ld-done'); }
  if (document.readyState === 'complete') hideLoader(); else window.addEventListener('load', hideLoader);
  setTimeout(hideLoader, 1200);

  // Header: transparent over heroes, solid after scroll
  var head = document.getElementById('head');
  var hasHero = !head.classList.contains('light');
  function onScroll() { if (hasHero) head.classList.toggle('solid', window.scrollY > 60); }
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile menu
  var burger = document.getElementById('burger'), nav = document.getElementById('nav');
  burger.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
    head.classList.toggle('solid', open || window.scrollY > 60 || !hasHero);
  });

  // Reveal on scroll
  var els = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  // Forms -> Google Sheets (Apps Script web app)
  function msgFor(form) {
    var m = form.querySelector('.form-msg');
    if (!m && form.nextElementSibling && form.nextElementSibling.classList.contains('form-msg')) m = form.nextElementSibling;
    return m;
  }
  document.querySelectorAll('form[data-sheet]').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var msg = msgFor(form);
      msg.className = 'form-msg';
      form.querySelectorAll('.err-text').forEach(function (e) { e.remove(); });
      form.querySelectorAll('.invalid').forEach(function (e) { e.classList.remove('invalid'); });
      var bad = Array.prototype.filter.call(form.elements, function (el) { return el.willValidate && !el.checkValidity(); });
      if (bad.length) {
        bad.forEach(function (el) {
          el.classList.add('invalid');
          var t = document.createElement('span'); t.className = 'err-text';
          t.textContent = el.validity.valueMissing ? (el.type === 'checkbox' ? 'Please tick this box to continue.' : 'This field is required.')
            : el.type === 'email' ? 'Please enter a valid email address.' : el.type === 'tel' ? 'Please enter a valid phone number.' : 'Please check this field.';
          if (form.classList.contains('news')) { msg.textContent = t.textContent; msg.className = 'form-msg err'; }
          else (el.type === 'checkbox' ? el.parentNode : el.parentNode).appendChild(t);
          el.addEventListener('input', function clr() { el.classList.remove('invalid'); var n = el.parentNode.querySelector('.err-text'); if (n) n.remove(); el.removeEventListener('input', clr); });
        });
        bad[0].focus(); return;
      }
      var hp = form.querySelector('[name="website"]');
      if (hp && hp.value) return; // bot

      var url = window.ORVYS_SHEET_URL;
      if (!url) {
        msg.textContent = 'Form not connected yet: add your Google Apps Script URL in assets/config.js.';
        msg.className = 'form-msg err'; return;
      }
      var data = new URLSearchParams();
      new FormData(form).forEach(function (v, k) { if (k !== 'website') data.append(k, v); });
      data.append('formType', form.dataset.sheet);
      data.append('page', location.pathname.split('/').pop() || 'index.html');
      data.append('submittedAt', new Date().toISOString());

      var btn = form.querySelector('[type="submit"]'), label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Sending…';
      fetch(url, { method: 'POST', mode: 'no-cors', body: data })
        .then(function () {
          msg.textContent = form.dataset.success || 'Thank you. We have received your message and will be in touch shortly.';
          msg.className = 'form-msg ok';
          if (form.dataset.download) {
            var a = document.createElement('a'); a.href = form.dataset.download; a.download = ''; document.body.appendChild(a); a.click(); a.remove();
          }
          form.reset();
        })
        .catch(function () {
          msg.textContent = 'Something went wrong. Please check your connection and try again.';
          msg.className = 'form-msg err';
        })
        .finally(function () { btn.disabled = false; btn.textContent = label; });
    });
  });

  // Blog category filter
  document.querySelectorAll('.filters .chip').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.filters .chip').forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      var c = b.dataset.cat;
      document.querySelectorAll('.post-card[data-cat]').forEach(function (a) { a.style.display = (c === 'all' || a.dataset.cat === c) ? '' : 'none'; });
    });
  });

  // LinkedIn Carousel
  document.querySelectorAll('.li-carousel-wrap').forEach(function (wrap) {
    var slides = wrap.querySelectorAll('.li-slide');
    var dots = wrap.querySelectorAll('.li-dot');
    var prev = wrap.querySelector('.li-btn.prev');
    var next = wrap.querySelector('.li-btn.next');
    var cur = 0;
    function show(idx) {
      cur = (idx + slides.length) % slides.length;
      slides.forEach(function (s, i) { s.classList.toggle('on', i === cur); });
      dots.forEach(function (d, i) { d.classList.toggle('on', i === cur); });
    }
    if (prev) prev.addEventListener('click', function () { show(cur - 1); });
    if (next) next.addEventListener('click', function () { show(cur + 1); });
    dots.forEach(function (d, i) {
      d.addEventListener('click', function () { show(i); });
    });
  });
})();
