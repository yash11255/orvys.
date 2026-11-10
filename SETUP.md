# Orvys website: setup

## Site structure

| Page | File |
| --- | --- |
| Home | `index.html` |
| About | `about.html` |
| What We Do | `what-we-do.html` |
| Partner With Us (partnership form) | `partner.html` |
| Insights (report download form) | `insights.html` |
| Contact (enquiry form) | `contact.html` |

Edit pages in `src/pages/`, and the shared header and footer in `src/_layout.html`. Then rebuild:

```bash
python3 build.py
```

## Connect the forms to Google Sheets (about 5 minutes)

All forms (Enquiries, Partnerships, Report Downloads, Newsletter, Research Registry, NGO Suggestions) save to one Google Sheet. Each form gets its own tab.

1. Create a new Google Sheet, for example "Orvys Website Leads".
2. In the Sheet, open **Extensions → Apps Script**.
3. Delete the sample code, paste in everything from `apps-script/Code.gs`, and click **Save**.
   - Optional: set `NOTIFY_EMAIL` to receive an email for each new submission.
4. Click **Deploy → New deployment** → the gear icon → **Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Click **Deploy**, then authorise the script with your Google account.
6. Copy the **Web app URL** (it ends in `/exec`).
7. Paste it into `assets/config.js`:
   ```js
   window.ORVYS_SHEET_URL = "https://script.google.com/macros/s/XXXX/exec";
   ```
8. Submit a test form on the site. A new row appears in the matching tab.

If you edit `Code.gs` later, use **Deploy → Manage deployments → Edit → New version** so the URL stays the same.

## Go live

Upload the whole folder to any static host, such as Netlify, Vercel, GitHub Pages or cPanel hosting. The `src/`, `apps-script/` and `build.py` files do not need to be public.

## Photo credits

The photos are from Wikimedia Commons under CC BY-SA licences, and are credited in the site footer. Keep those credits, or replace the photos with your own.

## Get every page indexed by Google

The site already includes `sitemap.xml` (36 URLs), `robots.txt`, canonical tags, Open Graph tags and structured data (Organization, BlogPosting, BreadcrumbList, FAQPage).

1. Deploy the site on your domain. If it is not `https://www.orvys.in`, change `SITE_URL` in `build.py`, run `python3 build.py`, and push.
2. Open Google Search Console (search.google.com/search-console), add your domain, and verify it through DNS.
3. Go to **Sitemaps**, enter `sitemap.xml` and click **Submit**.
4. Use **URL Inspection → Request indexing** for the most important pages first: `/`, `/bihar-csr.html`, `/insights.html` and `/blog/`.
5. Do the same in Bing Webmaster Tools; you can import the site straight from Search Console.

## Ranking for "Bihar CSR"

`/bihar-csr.html` is the main page targeting this search. It is linked from the main menu, the footer and every blog post. To rank, Google also needs signals from outside the site:

- Set up a **Google Business Profile** for Orvys in Patna.
- Get links to the Bihar CSR report from news sites, CSR portals, NGOs and LinkedIn posts.
- Publish one or two new posts a month, and update the Bihar CSR page when new MCA data is released.
- Ranking usually takes 2-6 months after indexing.
