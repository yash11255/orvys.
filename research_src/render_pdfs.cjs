// Renders watermarked PDFs for research pages through the local web server,
// so the site's CSS, fonts and images load. Usage: node render_pdfs.cjs <targets.json> [baseUrl]
const fs = require('fs'), path = require('path');
const { chromium } = require(path.resolve(__dirname, '../../node_modules/playwright'));
const targets = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const base = process.argv[3] || 'http://localhost:8810';
const footer = `<div style="width:100%;font-size:8px;font-family:Helvetica,Arial,sans-serif;color:#6b7685;padding:0 14mm;display:flex;justify-content:space-between">
<span>Orvys Research · www.orvys.in · partner@orvys.in</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`;
(async () => {
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  let ok = 0;
  {
    const sp = await browser.newPage();
    const tiles = Array.from({ length: 24 }, (_, i) => `<div style="position:absolute;left:${(i % 3) * 75 - 20}mm;top:${Math.floor(i / 3) * 42 - 10}mm;transform:rotate(-32deg);font:800 46px/1 Helvetica,Arial,sans-serif;letter-spacing:.18em;color:rgba(14,26,41,.055)">ORVYS</div>`).join('');
    await sp.setContent(`<html><body style="margin:0;background:transparent"><div style="position:relative;width:210mm;height:297mm;overflow:hidden">${tiles}<div style="position:absolute;right:8mm;top:4mm;font:600 7px Helvetica,Arial,sans-serif;color:rgba(14,26,41,.35)">© 2026 Orvys · www.orvys.in</div></div></body></html>`);
    await sp.pdf({ path: path.resolve(__dirname, 'stamp.pdf'), format: 'A4', omitBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 } });
    await sp.close();
  }
  const work = async (t) => {
    const page = await browser.newPage();
    await page.goto(base + t.url, { waitUntil: 'networkidle', timeout: 60000 });
    await page.evaluate(async () => {
      document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager');
      document.querySelectorAll('.rv').forEach(e => e.classList.add('in'));
      document.documentElement.classList.add('ld-done', 'ld-skip');
      await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
      await document.fonts.ready;
    });
    await page.evaluate(() => {
      // Branded cover page built from the page's own title, summary and image.
      const h1 = (document.querySelector('h1') || {}).innerText || document.title;
      const lede = (document.querySelector('meta[name="description"]') || {}).content || '';
      const og = (document.querySelector('meta[property="og:image"]') || {}).content || '';
      const img = og ? '/' + og.split('/').slice(3).join('/') : '/assets/img/golghar.jpg';
      const c = document.createElement('section');
      c.className = 'pdf-cover';
      c.innerHTML = `<div style="height:255mm;display:flex;flex-direction:column;background:#0e1a29;color:#fff;margin:0 14mm;break-after:page;page-break-after:always;overflow:hidden">
        <div style="height:105mm;background:linear-gradient(180deg,rgba(14,26,41,.15),#0e1a29),url('${img}') center/cover"></div>
        <div style="padding:14mm 14mm 0;flex:1;display:flex;flex-direction:column">
          <div style="background:#fff;display:inline-block;align-self:flex-start;padding:8px 14px;border-radius:3px"><img src="/assets/orvys-logo.webp" style="height:30px;display:block"></div>
          <div style="margin-top:12mm;font:600 11px/1 'DM Sans',sans-serif;letter-spacing:.2em;color:#c9a96e">ORVYS RESEARCH · BIHAR CSR SERIES</div>
          <div style="margin-top:5mm;font:800 34px/1.12 'Plus Jakarta Sans',sans-serif;letter-spacing:-.02em">${h1}</div>
          <div style="width:40mm;height:2px;background:#a8864f;margin:7mm 0"></div>
          <div style="font:400 14px/1.55 'DM Sans',sans-serif;color:#cdd4de;max-width:150mm">${lede}</div>
          <div style="margin-top:auto;padding-bottom:12mm;display:flex;justify-content:space-between;font:500 11px/1.5 'DM Sans',sans-serif;color:#9eaaba">
            <span>Published November 2026<br>Data: Ministry of Corporate Affairs, Census 2011, NFHS-5</span><span style="text-align:right">www.orvys.in<br>partner@orvys.in</span></div>
        </div></div>`;
      document.body.prepend(c);
    });
    await page.emulateMedia({ media: 'print' });
    fs.mkdirSync(path.dirname(t.out), { recursive: true });
    await page.pdf({ path: t.out, format: 'A4', printBackground: true, displayHeaderFooter: true,
      headerTemplate: '<span></span>', footerTemplate: footer, margin: { top: '12mm', bottom: '16mm', left: '0', right: '0' } });
    await page.close(); ok++;
  };
  const queue = [...targets];
  await Promise.all(Array.from({ length: 4 }, async () => { while (queue.length) { const t = queue.shift(); try { await work(t); } catch (e) { console.log('ERROR', t.url, e.message); } } }));
  await browser.close();
  console.log(`Rendered ${ok}/${targets.length} PDFs`);
})();
