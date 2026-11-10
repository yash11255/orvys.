#!/usr/bin/env python3
"""
Orvys Research Generator
Generates all research/* pages: hub, diagnostic, policy, skilling,
38 district pages, initiatives tracker, ecosystem page, and registry form.

Run via build.py (imported and called there), or standalone:
    python3 research_src/generate.py
"""
import sys, pathlib, html, json, re

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "research_src"))

from data import DISTRICTS, ASPIRATIONAL, FLOOD_BELT, YEARS, STATE_TOTAL, PSU, NON_PSU, BIHAR_POP, rows, slug, v
from sources import SRC, INITIATIVES, ORGS
import charts as C

SITE_URL = "https://www.orvys.in"
NAVY, GOLD = "#0e1a29", "#a8864f"

# ── helpers ────────────────────────────────────────────────────────────────

def esc(s): return html.escape(str(s), quote=False)

def srclink(key):
    label, url = SRC[key]
    return f'<a href="{url}" rel="nofollow noopener" target="_blank" class="srclink">{esc(label)}</a>'

def sources_block(keys):
    if not keys: return ""
    items = "".join(f"<li>{srclink(k)}</li>" for k in keys if k in SRC)
    return f'<div class="sources"><strong>Verified sources:</strong><ol>{items}</ol></div>'

def orvys_cta(heading, body, btn_text="Start a partnership", btn_href="/partner.html#start"):
    return f"""
<section class="cta-band">
  <div class="wrap"><span class="eyebrow" style="color:var(--gold2)">Orvys</span>
  <h2>{esc(heading)}</h2><p>{esc(body)}</p>
  <a href="{btn_href}" class="btn btn-gold">{esc(btn_text)}</a></div>
</section>"""

def breadcrumb(*crumbs):
    """crumbs: list of (label, href) where last href may be None"""
    parts = []
    for i, (label, href) in enumerate(crumbs):
        if href and i < len(crumbs) - 1:
            parts.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            parts.append(f'<span>{esc(label)}</span>')
    return f'<nav class="crumbs" aria-label="Breadcrumb">{" / ".join(parts)}</nav>'

def print_btn(label="Download as PDF"):
    return f"""<button class="btn btn-navy print-btn btn-dl-wm" onclick="window.print()" style="margin-top:16px"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24" style="vertical-align:middle;margin-right:6px" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>{esc(label)}</button>"""

def wrap_page(content, *, title, desc, path, nav="research", head="light", ogimage="/assets/img/ganga.jpg",
              extra_head="", structured_data=None):
    """Return page HTML with frontmatter processed by build.py."""
    ld_block = ""
    if structured_data:
        ld_block = f'<script type="application/ld+json">{json.dumps(structured_data, ensure_ascii=False)}</script>'
    return f"""<!--
title: {title}
desc: {desc}
nav: {nav}
head: {head}
-->
{content}
{ld_block}
"""

DISTRICT_ROWS = rows()
DIST_BY_NAME = {r["name"]: r for r in DISTRICT_ROWS}

def district_narrative(d):
    name = d["name"]
    pop_lakh = d["pop"] / 100000
    is_asp = d["aspirational"]
    is_flood = d["flood"]
    fy24 = d["fy24"]
    total = d["total"]
    pc = d["pc24"]
    
    if is_flood and is_asp:
        context = f"{name} is an Aspirational District located in Bihar's flood-prone Kosi-Seemanchal belt. With a population of {pop_lakh:.1f} Lakh, the district faces dual vulnerabilities of acute seasonal inundation and human development deficits. In FY 2023-24, it received ₹{fy24:.2f} Cr in CSR, representing ₹{pc:.1f} per person."
        opps = [
            ("Flood-Resilient Health & Nutrition", "Solar-powered mobile medical units and elevated Anganwadi centres equipped to maintain nutrition and vaccination services during monsoon displacement."),
            ("Potable Water & Water Quality", "Community-level arsenic and iron filtration plants, flood-proof elevated deep tube wells, and water quality testing infrastructure."),
            ("Climate-Smart Agriculture & Farmer Livelihoods", "Support for flood-tolerant paddy varieties, solar irrigation micro-grids, and cooperative processing units for maize and jute farmers.")
        ]
        view = f"In {name}, corporate CSR can achieve outsized social impact by co-investing in disaster-resilient social infrastructure with the district administration under the Aspirational Districts convergence framework."
    elif is_flood:
        context = f"{name} lies within Bihar's northern riparian plains, where riverine flooding regularly disrupts livelihoods, primary healthcare, and schooling for its {pop_lakh:.1f} Lakh residents. In FY 2023-24, {name} received ₹{fy24:.2f} Cr in total CSR (₹{pc:.1f} per capita)."
        opps = [
            ("Early Warning & Community Disaster Readiness", "Village-level disaster response equipment, safe evacuation shelters with solar power, and community first-responder volunteer training."),
            ("Makhana & Aquatic Livelihood Value Chains", "Post-harvest processing clusters, direct farmer aggregation hubs, and SHG enterprise support for wetland agro-produce."),
            ("Sanitation & Clean Drinking Water", "High-plinth twin-pit community toilets and chlorination systems to prevent waterborne epidemic outbreaks post-inundation.")
        ]
        view = f"CSR capital in {name} is best deployed in recurring climate resilience mechanisms and farmer-producer aggregation rather than one-off relief distributions."
    elif is_asp:
        context = f"{name} is designated as one of NITI Aayog's 13 Aspirational Districts in Bihar. With a population of {pop_lakh:.1f} Lakh, {name} is prioritized for rapid transformation across health, nutrition, education, agriculture, and skilling. In FY 2023-24, CSR spend was ₹{fy24:.2f} Cr."
        opps = [
            ("Model Anganwadi Centres (Nand Ghar Model)", "Upgrading rural Anganwadi centres with child-friendly learning kits, clean sanitation, solar lighting, and fortified nutrition supplementation."),
            ("Foundational Learning & STEM Classrooms", "Remedial learning camps (Teaching at the Right Level), smart digital classrooms, and teacher capacity development in upper-primary schools."),
            ("Youth Skilling & Employment Linkages", "Market-aligned vocational training in district ITIs with placement guarantees in logistics, retail, and manufacturing.")
        ]
        view = f"With strong district monitoring mechanisms under the Aspirational Districts Programme, CSR projects in {name} benefit from administrative backing and high accountability."
    elif name in ("Patna", "Muzaffarpur", "Begusarai", "Bhojpur"):
        context = f"{name} is one of Bihar's primary commercial and industrial hubs, home to {pop_lakh:.1f} Lakh residents. It accounts for a substantial share of total CSR inflows in Bihar (₹{fy24:.2f} Cr in FY 2023-24), reflecting proximity to corporate offices, PSU facilities, and administrative headquarters."
        opps = [
            ("Advanced Healthcare & Diagnostic Facilities", "Specialized medical equipment for district hospitals, mobile cancer screening, and dialysis support for marginalized rural patients."),
            ("Higher Skilling & Technology Incubation", "Centres of Excellence in technical polytechnics, industry 4.0 certifications, and incubation grants for local youth innovators."),
            ("Urban Environment & Sustainable Sanitation", "Decentralized wastewater treatment, lake rejuvenation, and plastic waste management collectives linked to informal waste-pickers.")
        ]
        view = f"As a high-inflow district, {name} needs CSR investments focused on deep systemic outcomes, scalable pilots, and quality certifications rather than basic infrastructure."
    else:
        context = f"{name} is an agrarian district in Bihar with a population of {pop_lakh:.1f} Lakh. In FY 2023-24, the district recorded ₹{fy24:.2f} Cr in CSR expenditures, ranking #{d['rank24']} across the state's 38 districts with a per-capita spend of ₹{pc:.1f}."
        opps = [
            ("Primary Health Centre (PHC) Strengthening", "Maternal-child healthcare wings, neonatal care stabilization, diagnostic kits, and 24/7 solar backup for rural health sub-centres."),
            ("Women's Self-Help Group (SHG) Enterprises", "Revolving enterprise funds, modern packaging machinery, and market linkages for JEEViKA-affiliated women's collectives."),
            ("Digital Literacy & Secondary Education", "Solar-powered computer labs in rural girls' high schools and career counseling networks to curb female dropout rates.")
        ]
        view = f"With modest current CSR inflows, {name} offers corporate funders high visibility and measurable additionality for medium-sized (₹50L - ₹2 Cr) multi-year programmes."
        
    return context, opps, view

# ── Orvys spotlight (reusable partial) ──────────────────────────────────────

SPOTLIGHT_HTML = """
<section class="orvys-spotlight">
  <div class="wrap">
    <div class="spotlight-inner rv">
      <div>
        <span class="eyebrow" style="color:var(--gold2)">Orvys Spotlight</span>
        <h2 style="margin:20px 0 20px">Bihar's most detailed CSR intelligence, built from primary data</h2>
        <p class="lede">Orvys tracks every rupee of district-level CSR in Bihar, verifies NGO activity on the ground, and turns raw MCA data into actionable intelligence for companies and governments.</p>
        <p style="margin-top:28px;display:flex;gap:16px;flex-wrap:wrap">
          <a class="btn btn-gold" href="/research/diagnostic.html">View Diagnostic</a>
          <a class="btn btn-ghost" href="/partner.html#start">Partner With Us</a>
        </p>
      </div>
      <div class="spotlight-stats">
        <div><b>38</b><span>districts tracked</span></div>
        <div><b>4 yrs</b><span>of primary CSR data</span></div>
        <div><b>₹770 Cr</b><span>Bihar CSR mapped</span></div>
        <div><b>25+</b><span>NGOs &amp; programmes verified</span></div>
      </div>
    </div>
  </div>
</section>
"""

# ── 1 · Research Hub ─────────────────────────────────────────────────────────

def build_hub():
    research_pages = [
        ("/research/diagnostic.html", "Bihar CSR Diagnostic", "State-level trends, PSU vs private split, per-capita spend, and full 38-district data table.", "📊"),
        ("/research/policy.html", "Policy &amp; Governance", "Analysis of Bihar's 2025 State CSR Policy, real-time portal, and convergence roundtables.", "⚖️"),
        ("/research/skilling.html", "Skilling &amp; Education", "Verified workforce development programmes (IBM, Pratham, Piramal) and aspirational district gaps.", "🎓"),
        ("/research/ecosystem.html", "CSR Ecosystem Directory", "Verified NGOs, corporate foundations, PSUs, and platforms active across Bihar.", "🌐"),
        ("/research/tracker.html", "Initiatives Tracker", "Interactive directory of all active CSR projects in Bihar, filterable by sector and geography.", "🗂"),
        ("/research/register.html", "Register an Initiative", "Submit your NGO or district-level programme to join the verified Bihar CSR directory.", "📝"),
    ]

    cards_html = ""
    for href, title, desc_txt, icon in research_pages:
        cards_html += f"""
<a class="res-card rv" href="{href}">
  <span class="res-icon">{icon}</span>
  <h3>{title}</h3>
  <p>{desc_txt}</p>
  <span class="link" style="font-size:14px">Explore section →</span>
</a>"""

    # All 38 districts grid
    all_dists = sorted(DISTRICT_ROWS, key=lambda r: r["name"])
    dist_cards = ""
    for d in all_dists:
        tags = ""
        if d["aspirational"]: tags += '<span class="tag-asp" title="NITI Aayog Aspirational District">A</span>'
        if d["flood"]: tags += '<span class="tag-flood" title="Kosi-Seemanchal Flood Belt">F</span>'
        dist_cards += f"""
<a class="dist-mini rv" href="/research/districts/{d['slug']}.html" data-asp="{str(d['aspirational']).lower()}" data-flood="{str(d['flood']).lower()}">
  <strong>{esc(d['name'])}</strong>{tags}
  <span>₹{d['fy24']:.2f} Cr <small>FY24</small></span>
</a>"""

    content = f"""
<section class="hero page-hero">
  <div class="bg" style="background-image:url('/assets/img/nalanda.jpg')"></div>
  <div class="wrap">
    <span class="eyebrow" style="color:var(--gold2)">Orvys Research Hub</span>
    <h1 style="margin-top:22px">The Bihar CSR <em>Research Hub</em></h1>
    <p>Primary data, verified NGOs, 38 district profiles and policy tracking — everything corporate and government leaders need to invest where impact is highest.</p>
    <div class="ctas">
      <a href="/research/diagnostic.html" class="btn btn-gold">View CSR Diagnostic</a>
      <a href="/insights.html#download" class="btn btn-ghost">Download 2026 Outlook Report</a>
      {print_btn("Download Summary (PDF)")}
    </div>
  </div>
  <span class="credit">Nalanda Mahavihara</span>
</section>

<section class="dark sec-sm">
  <div class="wrap">
    <div class="stats rv">
      <div><b>₹770.80 Cr</b><span>Total CSR spent in Bihar, FY21 to FY24</span></div>
      <div><b>38</b><span>districts tracked with 4-year trends</span></div>
      <div><b>13</b><span>NITI Aayog aspirational districts</span></div>
      <div><b>4</b><span>core research pillars &amp; live tracker</span></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="narrow rv"><span class="chip">Research Pillars</span><h2 style="margin-top:22px">Four pillars of Bihar CSR research</h2>
    <p style="color:var(--mute);margin-top:14px">Independent research produced by Orvys to inform strategic corporate social investment, compliance, and government convergence.</p></div>
    <div class="res-grid" style="margin-top:40px">{cards_html}</div>
  </div>
</section>

{SPOTLIGHT_HTML}

<section class="sand" id="districts">
  <div class="wrap">
    <div class="narrow rv">
      <span class="chip">38 District Profiles</span>
      <h2 style="margin-top:22px">Bihar CSR by District</h2>
      <p style="margin-top:16px;color:var(--mute)">Every district in Bihar has a dedicated profile with 4-year trend data, local initiatives, development deficits, and investment opportunities.</p>
    </div>
    <div class="filters" style="margin-top:28px">
      <button class="chip on" data-dfilter="all">All 38 Districts</button>
      <button class="chip" data-dfilter="asp">13 Aspirational Districts</button>
      <button class="chip" data-dfilter="flood">7 Flood-Prone Districts</button>
    </div>
    <div class="dist-grid" style="margin-top:28px" id="hub-dist-grid">{dist_cards}</div>
    <p class="small muted" style="margin-top:24px">
      <span class="tag-asp">A</span> = NITI Aayog aspirational district ·
      <span class="tag-flood">F</span> = Kosi-Seemanchal flood belt ·
      Data: Ministry of Corporate Affairs (Rajya Sabha UQ 1010, Dec 2025).
    </p>
    <p style="margin-top:28px"><a class="link rv" href="/research/districts/index.html">View full district index table →</a></p>
  </div>
</section>

<script>
(function(){{
  var chips = document.querySelectorAll('[data-dfilter]');
  var cards = document.querySelectorAll('#hub-dist-grid .dist-mini');
  chips.forEach(function(c){{
    c.addEventListener('click', function(){{
      chips.forEach(function(x){{ x.classList.remove('on'); }});
      c.classList.add('on');
      var f = c.dataset.dfilter;
      cards.forEach(function(el){{
        if (f === 'all') el.style.display = '';
        else if (f === 'asp') el.style.display = el.dataset.asp === 'true' ? '' : 'none';
        else if (f === 'flood') el.style.display = el.dataset.flood === 'true' ? '' : 'none';
      }});
    }});
  }});
}})();
</script>

{orvys_cta("Planning CSR in Bihar? Let's build it together.",
           "Orvys designs, funds and measures CSR programmes across all 38 Bihar districts. Tell us your priorities.",
           "Start a partnership", "/partner.html#start")}
"""
    return wrap_page(content,
        title="Bihar CSR Research Hub | Orvys",
        desc="Primary CSR data, 38 district profiles, verified NGOs, policy tracker and ecosystem map for Bihar.",
        path="research/index.html", head="")


# ── 2 · Diagnostic page ──────────────────────────────────────────────────────

def build_diagnostic():
    trend = C.vbar(["FY21", "FY22", "FY23", "FY24"], STATE_TOTAL, lambda x: f"₹{x:.0f} Cr",
                   title="Bihar total CSR by year (₹ Cr)")
    stacked = C.stacked(["FY21","FY22","FY23","FY24"], PSU, NON_PSU,
                        "PSU", "Private", title="Bihar CSR: PSU vs Private (₹ Cr)")
    top20 = sorted(DISTRICT_ROWS, key=lambda r: -r["fy24"])[:20]
    dist_bar = C.hbar(
        [(d["name"], d["fy24"], d["aspirational"]) for d in top20],
        lambda x: f"₹{x:.2f} Cr",
        title="Top 20 Bihar districts by CSR, FY 2023-24",
        ref=(sum(r["fy24"] for r in DISTRICT_ROWS)/38, "State avg")
    )
    top_pc = sorted(DISTRICT_ROWS, key=lambda r: -r["pc24"])[:15]
    pc_bar = C.hbar(
        [(d["name"], d["pc24"], d["aspirational"]) for d in top_pc],
        lambda x: f"₹{x:.1f}",
        title="Top 15 districts: CSR per person (₹), FY 2023-24"
    )

    table_rows = ""
    for d in sorted(DISTRICT_ROWS, key=lambda r: -r["fy24"]):
        tags = ""
        if d["aspirational"]: tags += ' <span class="tag-asp">A</span>'
        if d["flood"]: tags += ' <span class="tag-flood">F</span>'
        s = d["series"]
        def fmt(x): return f"₹{x:.2f}" if x else "—"
        table_rows += f"""<tr>
  <td><a href="/research/districts/{d['slug']}.html" style="font-weight:600;color:var(--navy)">{esc(d['name'])}</a>{tags}</td>
  <td>{fmt(s[0])}</td><td>{fmt(s[1])}</td><td>{fmt(s[2])}</td>
  <td style="font-weight:700">{fmt(s[3])}</td>
  <td>₹{d['pc24']:.1f}</td><td>#{d['rank24']}</td>
</tr>"""

    content = f"""
<article>
<header class="post-head">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("Bihar CSR Diagnostic",None))}
    <span class="chip">Research · Diagnostic</span>
    <h1>Bihar CSR Diagnostic</h1>
    <p class="lede">Four years of primary district-level CSR data for Bihar — trends, corporate vs PSU breakdown, and per-capita analysis.</p>
    <div class="byline">Orvys Research Team · November 2026 · Source: Ministry of Corporate Affairs</div>
    {print_btn()}
  </div>
</header>

<div class="wrap" style="margin-top:60px">

<div class="narrow rv"><span class="chip">State Trend</span><h2 style="margin-top:16px">Bihar CSR, FY 2020-21 to FY 2023-24</h2>
<p style="color:var(--mute);margin:12px 0 24px">Total CSR in Bihar grew 2.9× in four years, from ₹89.89 Cr to ₹260.53 Cr. Despite this growth, Bihar still receives only ~1% of India's total state-attributed CSR despite accounting for 8.6% of the national population.</p></div>
<div class="chart-wrap rv">{trend}</div>

<div class="narrow rv" style="margin-top:80px"><span class="chip">PSU vs Private Split</span><h2 style="margin-top:16px">Who funds Bihar's CSR?</h2>
<p style="color:var(--mute);margin:12px 0 24px">Private companies now contribute 65% of Bihar's CSR (₹169.40 Cr in FY24). PSU contributions peaked in FY23 at ₹110.29 Cr and stood at ₹91.13 Cr in FY24.</p></div>
<div class="chart-wrap rv">{stacked}</div>

<div class="narrow rv" style="margin-top:80px"><span class="chip">District Concentration</span><h2 style="margin-top:16px">Top 20 districts by CSR (FY 2023-24)</h2>
<p style="color:var(--mute);margin:12px 0 24px">Muzaffarpur and Patna alone accounted for 35% of Bihar's total CSR in FY24. <span style="color:{GOLD};font-weight:600">Gold bars</span> denote NITI Aayog Aspirational Districts. Dashed line indicates state average (₹6.86 Cr).</p></div>
<div class="chart-wrap rv">{dist_bar}</div>

<div class="narrow rv" style="margin-top:80px"><span class="chip">Per-Capita Disparity</span><h2 style="margin-top:16px">CSR per person — where the gap is widest</h2>
<p style="color:var(--mute);margin:12px 0 24px">Per-capita CSR (₹ per person, FY24) highlights districts that remain severely under-funded relative to their demographics. Bihar average stands at ₹{sum(r['fy24'] for r in DISTRICT_ROWS)*1e7/BIHAR_POP:.1f} per person, compared to the India national average of ₹223.</p></div>
<div class="chart-wrap rv">{pc_bar}</div>

<div class="narrow rv" style="margin-top:80px"><span class="chip">All 38 Districts</span><h2 style="margin-top:16px">Complete district dataset (FY21–FY24)</h2>
<p style="color:var(--mute);margin:12px 0 24px">All figures in ₹ crore. <span class="tag-asp">A</span> = NITI Aayog Aspirational District · <span class="tag-flood">F</span> = Kosi-Seemanchal flood belt</p></div>
<div class="formcard rv" style="overflow-x:auto;margin-bottom:60px">
<table style="width:100%;border-collapse:collapse;font-size:14.5px;min-width:640px">
<thead><tr style="background:var(--navy);color:#fff">
  <th style="text-align:left;padding:12px 10px">District</th>
  <th style="padding:12px 10px">FY21</th><th style="padding:12px 10px">FY22</th>
  <th style="padding:12px 10px">FY23</th><th style="padding:12px 10px">FY24</th>
  <th style="padding:12px 10px">₹/person</th><th style="padding:12px 10px">Rank</th>
</tr></thead>
<tbody>{table_rows}</tbody>
</table>
</div>

{sources_block(["rs1010","ls2338","nfhs","census"])}

</div>
</article>

{orvys_cta("Turn data into targeted outcomes.", "Orvys uses this primary dataset to build compliant, high-impact CSR portfolios in under-served districts.")}
"""
    return wrap_page(content,
        title="Bihar CSR Diagnostic: 4-Year District Data | Orvys",
        desc="Four years of Bihar district-level CSR data: trends, PSU vs private split, per-capita spend, and full district table.",
        path="research/diagnostic.html")


# ── 3 · Policy page ──────────────────────────────────────────────────────────

def build_policy():
    gov_initiatives = [i for i in INITIATIVES if i["sector"] == "Governance"]
    cards = ""
    for init in gov_initiatives:
        dist_str = ", ".join(init["districts"])
        srcs = sources_block(init["src"])
        cards += f"""
<div class="init-card rv">
  <div class="init-meta"><span class="chip">{esc(init['kind'])}</span><span class="init-when">{esc(init['when'])}</span></div>
  <h3>{esc(init['name'])}</h3>
  <p><strong>{esc(init['org'])}</strong> · {esc(dist_str)}</p>
  <p style="color:var(--mute);margin-top:8px">{esc(init['detail'])}</p>
  <div class="orvys-view"><strong>Orvys Perspective:</strong> {esc(init['view'])}</div>
  {srcs}
</div>"""

    content = f"""
<article>
<header class="post-head">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("Policy &amp; Governance",None))}
    <span class="chip">Research · Policy</span>
    <h1>Bihar CSR Policy &amp; Governance</h1>
    <p class="lede">Bihar's first State CSR Policy (2025), the new real-time CSR portal, and multi-stakeholder roundtables — tracked and analyzed.</p>
    <div class="byline">Orvys Research Team · November 2026</div>
    {print_btn()}
  </div>
</header>

<div class="wrap" style="margin-top:60px">

<div class="narrow rv">
<span class="chip">Strategic Context</span>
<h2 style="margin-top:16px">The emerging policy architecture in Bihar</h2>
<p style="color:var(--mute);margin:16px 0">Bihar receives about ₹25 of CSR per person per year — against a national average of ₹223. The Government of Bihar's 2025 State CSR Policy aims to change that by creating an institutional mechanism to attract, guide and monitor corporate social investments across all 38 districts.</p>
<p style="color:var(--mute)">Three key governance instruments now shape the landscape: a Chief Secretary-led State CSR Society, a real-time tracking portal aimed at mobilising ₹5,000 crore, and institutional convergence dialogues with UNICEF and academic partners like CIMP Patna.</p>
</div>

<div style="margin-top:60px">
<div class="narrow rv"><span class="chip">Tracked Actions</span><h2 style="margin-top:16px">Key policy initiatives</h2></div>
<div class="init-list" style="margin-top:32px">{cards}</div>
</div>

<div class="narrow rv" style="margin-top:64px">
  <div class="formcard">
    <span class="chip">Orvys Recommendations</span>
    <h3 style="margin:16px 0 12px">How Bihar can unlock CSR scale</h3>
    <ul style="color:var(--mute);padding-left:20px;line-height:1.75">
      <li><strong>Standardize District CSR Project Banks:</strong> Provide pre-costed, Schedule VII-aligned DPRs across the 13 Aspirational Districts so corporates can fund projects without lengthy feasibility cycles.</li>
      <li><strong>Incentivize Under-Funded Geographies:</strong> Recognize corporate funders investing in districts receiving under ₹1 Cr/year through an annual state Governor's CSR citation.</li>
      <li><strong>Transparent NGO Verification:</strong> Connect the state portal directly with MCA CSR-1, 12A/80G, and Darpan registries to reduce due diligence bottlenecks.</li>
      <li><strong>Multi-Year Pooled Funds:</strong> Enable corporate unspent CSR funds to be deposited into multi-year ongoing projects managed through transparent Escrow accounts.</li>
    </ul>
  </div>
</div>

{sources_block(["policy","portal","roundtable"])}

</div>
</article>

{orvys_cta("Align your CSR with state priorities.", "Orvys briefs corporate boards on state priorities and facilitates high-level MoUs with government departments.")}
"""
    return wrap_page(content,
        title="Bihar CSR Policy 2025: State Governance Tracker | Orvys",
        desc="Track Bihar's 2025 State CSR Policy, the Bihar CSR Portal, and UNICEF-CIMP roundtable outcomes with Orvys research.",
        path="research/policy.html")


# ── 4 · Skilling page ────────────────────────────────────────────────────────

def build_skilling():
    skill_inits = [i for i in INITIATIVES if "skilling" in i["sector"].lower() or "education" in i["sector"].lower() or "youth" in i["sector"].lower()]
    cards = ""
    for init in skill_inits:
        dist_str = ", ".join(init["districts"])
        cards += f"""
<div class="init-card rv">
  <div class="init-meta"><span class="chip">{esc(init['kind'])}</span><span class="init-when">{esc(init['when'])}</span></div>
  <h3>{esc(init['name'])}</h3>
  <p><strong>{esc(init['org'])}</strong> · {esc(dist_str)} · <em>{esc(init['sector'])}</em></p>
  <p style="color:var(--mute);margin-top:8px">{esc(init['detail'])}</p>
  <div class="orvys-view"><strong>Orvys Perspective:</strong> {esc(init['view'])}</div>
  {sources_block(init['src'])}
</div>"""

    asp_districts = sorted([d for d in DISTRICT_ROWS if d["aspirational"]], key=lambda r: r["pc24"])
    gap_rows = ""
    for d in asp_districts:
        gap_rows += f"""<tr>
  <td><a href="/research/districts/{d['slug']}.html" style="font-weight:600;color:var(--navy)">{esc(d['name'])}</a></td>
  <td style="font-weight:700">₹{d['fy24']:.2f} Cr</td>
  <td>₹{d['pc24']:.1f}</td>
  <td>#{d['rank24']} of 38</td>
</tr>"""

    content = f"""
<article>
<header class="post-head">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("Skilling &amp; Education",None))}
    <span class="chip">Research · Skilling</span>
    <h1>CSR Skilling &amp; Education in Bihar</h1>
    <p class="lede">Verified workforce development, digital skills, and foundational learning programmes operating across Bihar.</p>
    <div class="byline">Orvys Research Team · November 2026</div>
    {print_btn()}
  </div>
</header>

<div class="wrap" style="margin-top:60px">

<div class="narrow rv">
<span class="chip">The Structural Challenge</span>
<h2 style="margin-top:16px">Bridging the youth employability deficit</h2>
<p style="color:var(--mute);margin:16px 0">Bihar possesses one of India's youngest populations, with over 38 million individuals under the age of 15. However, foundational learning deficits, low female labour-force participation, and a shortage of modern technical infrastructure create an urgent demand for placement-linked skilling programmes.</p>
<p style="color:var(--mute)">While prominent private-sector initiatives like IBM SkillsBuild and IBM STEM for Girls have demonstrated scalable models in government schools and polytechnics, skilling CSR remains heavily skewed toward urban centres, leaving rural Aspirational Districts severely under-served.</p>
</div>

<div style="margin-top:60px">
<div class="narrow rv"><span class="chip">Verified Programmes</span><h2 style="margin-top:16px">Active skilling initiatives in Bihar</h2></div>
<div class="init-list" style="margin-top:32px">{cards}</div>
</div>

<div style="margin-top:72px">
<div class="narrow rv"><span class="chip">Aspirational District Gap</span><h2 style="margin-top:16px">Where skilling investment is needed most</h2>
<p style="color:var(--mute);margin:12px 0 24px">Aspirational districts contain the highest proportion of first-generation learners. Table sorted by lowest per-capita CSR received in FY 2023-24.</p></div>
<div class="formcard rv" style="overflow-x:auto">
<table style="width:100%;border-collapse:collapse;font-size:15px;min-width:480px">
<thead><tr style="background:var(--navy);color:#fff">
  <th style="text-align:left;padding:12px 14px">District</th>
  <th style="padding:12px 14px">FY24 CSR</th>
  <th style="padding:12px 14px">₹/person</th>
  <th style="padding:12px 14px">State rank</th>
</tr></thead>
<tbody>{gap_rows}</tbody>
</table>
</div>
</div>

{sources_block(["ibm_stem","ibm_skills","pratham","piramal","stairs","nfhs"])}
</div>
</article>

{orvys_cta("Build an employment-linked skilling programme.", "Orvys structures industry-aligned vocational training in district ITIs with verified employer placements.")}
"""
    return wrap_page(content,
        title="CSR Skilling &amp; Education in Bihar | Orvys Research",
        desc="Verified skilling and education CSR initiatives in Bihar: IBM, Pratham, Piramal Foundation, STAIRS and others, with Orvys assessment.",
        path="research/skilling.html")


# ── 5 · Initiatives Tracker ───────────────────────────────────────────────────

def build_tracker():
    sectors = sorted({i["sector"] for i in INITIATIVES})

    chips = '<button class="chip on" data-filter="all">All sectors</button>'
    for s in sectors:
        chips += f'<button class="chip" data-filter="{esc(s)}">{esc(s)}</button>'

    table_rows = ""
    for init in INITIATIVES:
        dist_str = esc(", ".join(init["districts"]))
        src_links = " · ".join(
            f'<a href="{SRC[k][1]}" rel="nofollow noopener" target="_blank" class="srclink">src</a>'
            for k in init["src"] if k in SRC
        )
        table_rows += f"""<tr data-sector="{esc(init['sector'])}">
  <td style="font-weight:600;color:var(--navy)">{esc(init['name'])}</td>
  <td>{esc(init['org'])}</td>
  <td><span class="chip" style="font-size:11px;padding:3px 8px">{esc(init['kind'])}</span></td>
  <td>{esc(init['sector'])}</td>
  <td>{dist_str}</td>
  <td style="font-size:13px;color:var(--mute)">{esc(init['when'])}</td>
  <td style="font-size:13px">{src_links}</td>
</tr>"""

    content = f"""
<section class="post-head" style="padding-bottom:40px">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("Initiatives Tracker",None))}
    <span class="chip">Research · Tracker</span>
    <h1>Bihar CSR Initiatives Tracker</h1>
    <p class="lede">Every verified CSR initiative, MoU, and programme in Bihar — filterable by thematic sector.</p>
    <div class="byline">Orvys Research Team · November 2026 · {len(INITIATIVES)} initiatives verified</div>
    {print_btn("Print Tracker (PDF)")}
  </div>
</section>

<section style="padding-top:20px">
  <div class="wrap">
    <div class="filters" style="margin-bottom:28px">{chips}</div>
    <div class="formcard rv" style="overflow-x:auto">
    <table id="tracker-table" style="width:100%;border-collapse:collapse;font-size:14px;min-width:900px">
    <thead><tr style="background:var(--navy);color:#fff">
      <th style="text-align:left;padding:12px 10px;min-width:200px">Initiative</th>
      <th style="text-align:left;padding:12px 10px;min-width:160px">Organisation</th>
      <th style="padding:12px 10px">Type</th>
      <th style="padding:12px 10px">Sector</th>
      <th style="padding:12px 10px;min-width:140px">District(s)</th>
      <th style="padding:12px 10px">Timeline</th>
      <th style="padding:12px 10px">Source</th>
    </tr></thead>
    <tbody>{table_rows}</tbody>
    </table>
    </div>
    <div style="margin-top:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px">
      <p class="small muted" style="margin:0">All initiatives verified through published press releases, MCA filings, and government MoUs.</p>
      <a href="/research/register.html" class="btn btn-navy" style="font-size:14px;padding:8px 18px">Submit Your Initiative →</a>
    </div>
  </div>
</section>

<script>
(function(){{
  var chips = document.querySelectorAll('.filters .chip');
  var rows = document.querySelectorAll('#tracker-table tbody tr');
  chips.forEach(function(b){{
    b.addEventListener('click', function(){{
      chips.forEach(function(x){{ x.classList.remove('on'); }});
      b.classList.add('on');
      var f = b.dataset.filter;
      rows.forEach(function(r){{
        r.style.display = (f === 'all' || r.dataset.sector === f) ? '' : 'none';
      }});
    }});
  }});
}})();
</script>

{orvys_cta("Fund an existing project or design a new one.", "Orvys provides independent monitoring and Schedule VII compliance for CSR projects across Bihar.")}
"""
    return wrap_page(content,
        title="Bihar CSR Initiatives Tracker | Orvys Research",
        desc=f"All {len(INITIATIVES)} verified CSR initiatives in Bihar, filterable by sector and district. Updated November 2026.",
        path="research/tracker.html")


# ── 6 · Ecosystem page ───────────────────────────────────────────────────────

def build_ecosystem():
    org_sections = ""
    for category, orgs in ORGS:
        cards = ""
        for name, kind, detail, src_keys in orgs:
            srcs = " · ".join(
                f'<a href="{SRC[k][1]}" rel="nofollow noopener" target="_blank" class="srclink">{esc(SRC[k][0][:45])}…</a>'
                for k in src_keys if k in SRC
            )
            cards += f"""
<div class="eco-card rv">
  <div class="eco-top"><strong>{esc(name)}</strong><span class="chip" style="font-size:11px;padding:3px 8px">{esc(kind)}</span></div>
  <p style="color:var(--mute);font-size:14.5px;margin:12px 0;line-height:1.6">{esc(detail)}</p>
  <div style="font-size:12px;color:var(--mute);margin-top:auto">{srcs}</div>
</div>"""
        org_sections += f"""
<div style="margin-top:60px">
  <div class="narrow"><h2 class="rv" style="font-size:clamp(22px,2.5vw,30px)">{esc(category)}</h2></div>
  <div class="eco-grid" style="margin-top:24px">{cards}</div>
</div>"""

    content = f"""
<section class="post-head" style="padding-bottom:40px">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("CSR Ecosystem",None))}
    <span class="chip">Research · Ecosystem</span>
    <h1>Bihar CSR Ecosystem Directory</h1>
    <p class="lede">Verified implementing NGOs, corporate foundations, multilaterals, PSUs, and platforms active in Bihar.</p>
    <div class="byline">Orvys Research Team · November 2026 · Verified Directory</div>
    {print_btn("Print Directory (PDF)")}
  </div>
</section>

<section style="padding-top:20px;padding-bottom:60px">
  <div class="wrap">
    {org_sections}
    {sources_block(list(SRC.keys())[:8])}
  </div>
</section>

<section class="sand" style="padding:80px 0">
  <div class="wrap split" style="align-items:center">
    <div class="rv">
      <span class="chip">Ecosystem Registry</span>
      <h2 style="margin:20px 0 16px">Are you operating an initiative in Bihar?</h2>
      <p class="lede">Get listed in the verified Bihar CSR directory. We connect grassroots implementers with corporate CSR committees looking for vetted partners.</p>
      <p style="margin-top:28px"><a href="/research/register.html" class="btn btn-gold">Register Your Organisation</a></p>
    </div>
    <div class="rv">
      <div class="formcard">
        <h4>Directory Inclusion Criteria</h4>
        <ul style="color:var(--mute);font-size:15px;margin-top:14px;padding-left:20px;line-height:1.75">
          <li>Valid MCA CSR-1 registration number</li>
          <li>Active 12A and 80G tax exemption certificates</li>
          <li>Demonstrated operational track record in Bihar</li>
          <li>Audited financials for at least 3 preceding financial years</li>
        </ul>
      </div>
    </div>
  </div>
</section>

{orvys_cta("Need an audited implementing partner?", "Orvys conducts rigorous due diligence and matches companies with the right NGO partner for every district in Bihar.")}
"""
    return wrap_page(content,
        title="Bihar CSR Ecosystem Directory: NGOs, PSUs &amp; Foundations | Orvys",
        desc="Verified directory of NGOs, foundations, PSUs and platforms active in Bihar CSR — updated November 2026.",
        path="research/ecosystem.html")


# ── 7 · Registry form page ───────────────────────────────────────────────────

def build_register():
    content = f"""
<article>
<header class="post-head">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("Register Initiative",None))}
    <span class="chip">Ecosystem Registry</span>
    <h1>Register your NGO or District Initiative</h1>
    <p class="lede">Submit your organisation or district-level programme for inclusion in the Bihar CSR Ecosystem Tracker.</p>
    <div class="byline">Orvys Research · Free directory for verified CSR implementers</div>
    {print_btn("Print Questionnaire (PDF)")}
  </div>
</header>

<div class="wrap" style="margin-top:60px;margin-bottom:80px">
  <div class="split" style="align-items:start">
    <div class="rv">
      <span class="chip">Why Register</span>
      <h2 style="margin:20px 0 20px">Join the verified Bihar CSR ecosystem</h2>
      <p class="lede">The Orvys Ecosystem Tracker is used by corporate CSR committees, PSUs, and state authorities looking for credible, execution-ready partners across Bihar's 38 districts.</p>
      
      <div style="margin-top:36px;display:grid;gap:24px">
        <div class="pillar" style="padding:0;border:0">
          <div class="n">01 · Visibility</div>
          <h3>Corporate discovery</h3>
          <p>Be discovered by corporate CSR leaders looking for credible implementing partners with ground presence in specific districts.</p>
        </div>
        <div class="pillar" style="padding:0;border:0">
          <div class="n">02 · Verification</div>
          <h3>Trust &amp; compliance</h3>
          <p>Our research team validates CSR-1, 12A/80G, and past implementation records to build funder confidence.</p>
        </div>
        <div class="pillar" style="padding:0;border:0">
          <div class="n">03 · Convergence</div>
          <h3>District alignment</h3>
          <p>Highlight your work to district collectors and line departments seeking convergence for Aspirational Districts and Blocks.</p>
        </div>
      </div>
    </div>

    <div class="formcard rv" style="color:var(--ink)">
      <h3 style="margin-bottom:8px">Initiative Registration Form</h3>
      <p style="color:var(--mute);font-size:14.5px;margin-bottom:28px">Complete this form. We verify all entries before publishing them to the public tracker.</p>
      
      <form class="form" data-sheet="Research Registry" data-success="Thank you. Your submission has been received. Our research team will review and verify your details before adding them to the Bihar CSR Ecosystem Tracker." novalidate>
        <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">

        <div class="full">
          <label for="reg-org">Organisation name *</label>
          <input id="reg-org" name="organisation" required placeholder="e.g. Gram Vikas Kendra / Pratham Bihar">
        </div>

        <div>
          <label for="reg-type">Organisation type *</label>
          <select id="reg-type" name="org_type" required>
            <option value="">— Select type —</option>
            <option value="NGO / Trust / Society">NGO / Trust / Society</option>
            <option value="Section 8 Company">Section 8 Company</option>
            <option value="Corporate Foundation">Corporate Foundation</option>
            <option value="PSU Foundation / CSR Cell">PSU Foundation / CSR Cell</option>
            <option value="Academic / Research Institution">Academic / Research Institution</option>
            <option value="Government Body / Agency">Government Body / Agency</option>
            <option value="Platform / Intermediary">Platform / Intermediary</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div>
          <label for="reg-csr1">CSR-1 registration number</label>
          <input id="reg-csr1" name="csr1_number" placeholder="e.g. CSR00012345 (if applicable)">
        </div>

        <div>
          <label for="reg-name">Contact person *</label>
          <input id="reg-name" name="name" required placeholder="Full name">
        </div>

        <div>
          <label for="reg-email">Email address *</label>
          <input id="reg-email" type="email" name="email" required placeholder="name@organisation.org">
        </div>

        <div>
          <label for="reg-phone">Phone number</label>
          <input id="reg-phone" type="tel" name="phone" placeholder="+91">
        </div>

        <div>
          <label for="reg-est">Year established</label>
          <input id="reg-est" type="number" name="year_established" min="1900" max="2026" placeholder="e.g. 2015">
        </div>

        <div class="full">
          <label for="reg-districts">Districts of operation in Bihar *</label>
          <input id="reg-districts" name="districts" required placeholder="e.g. Patna, Muzaffarpur, Gaya (or Statewide)">
        </div>

        <div class="full">
          <label for="reg-sectors">Primary sector(s) *</label>
          <select id="reg-sectors" name="sector" required>
            <option value="">— Select primary sector —</option>
            <option value="Education & Skilling">Education & Skilling</option>
            <option value="Healthcare & Nutrition">Healthcare & Nutrition</option>
            <option value="Livelihoods & Enterprise">Livelihoods & Enterprise</option>
            <option value="Women's Empowerment">Women's Empowerment</option>
            <option value="Climate & Flood Resilience">Climate & Flood Resilience</option>
            <option value="Drinking Water & Sanitation">Drinking Water & Sanitation</option>
            <option value="Governance & Infrastructure">Governance & Infrastructure</option>
            <option value="Sports & Youth Development">Sports & Youth Development</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div class="full">
          <label for="reg-budget">Annual Bihar programme budget range</label>
          <select id="reg-budget" name="annual_budget">
            <option value="">— Select budget range —</option>
            <option value="Under ₹25 Lakh">Under ₹25 Lakh</option>
            <option value="₹25 Lakh to ₹1 Crore">₹25 Lakh to ₹1 Crore</option>
            <option value="₹1 Crore to ₹5 Crore">₹1 Crore to ₹5 Crore</option>
            <option value="Above ₹5 Crore">Above ₹5 Crore</option>
            <option value="Prefer not to disclose">Prefer not to disclose</option>
          </select>
        </div>

        <div class="full">
          <label for="reg-desc">Summary of work &amp; key achievements in Bihar *</label>
          <textarea id="reg-desc" name="description" rows="4" required placeholder="Describe your key programmes, scale of beneficiaries, and key results achieved in Bihar..."></textarea>
        </div>

        <div class="full">
          <label for="reg-url">Website or public profile URL</label>
          <input id="reg-url" type="url" name="website_url" placeholder="https://...">
        </div>

        <div class="full">
          <button type="submit" class="btn btn-gold" style="width:100%">Submit for Verification</button>
        </div>
        <div class="form-msg" role="status"></div>
      </form>
    </div>
  </div>
</div>
</article>

{orvys_cta("Explore verified initiatives in Bihar.", "View the live tracker of programmes, implementing partners and corporate funders active across Bihar.", "View Ecosystem Tracker", "/research/ecosystem.html")}
"""
    return wrap_page(content,
        title="Register NGO or District Initiative | Orvys Research",
        desc="Submit your organisation or district-level CSR programme for inclusion in the verified Bihar CSR Ecosystem Tracker.",
        path="research/register.html")


# ── 8 · 38 District pages ────────────────────────────────────────────────────

def build_district(d):
    name = d["name"]
    s = d["series"]
    tags_html = ""
    if d["aspirational"]: tags_html += ' <span class="tag-asp">Aspirational District</span>'
    if d["flood"]: tags_html += ' <span class="tag-flood">Flood Belt</span>'

    vals = [v(x) for x in s]
    chart = C.vbar(["FY21","FY22","FY23","FY24"], vals,
                   lambda x: f"₹{x:.2f}" if x else "—",
                   title=f"{name}: CSR by year (₹ Cr)")

    dist_inits = [i for i in INITIATIVES if name in i["districts"] or "Statewide" in i["districts"]]
    init_cards = ""
    for init in dist_inits:
        scope = "Statewide" if "Statewide" in init["districts"] else "District-specific"
        init_cards += f"""
<div class="init-card rv" style="margin-bottom:20px">
  <div class="init-meta"><span class="chip">{esc(init['kind'])}</span><span class="init-when">{esc(init['when'])}</span>
  <span style="font-size:12px;color:var(--mute);margin-left:8px">{scope}</span></div>
  <h3 style="font-size:19px">{esc(init['name'])}</h3>
  <p style="color:var(--mute);font-size:14.5px;margin-top:6px">{esc(init['detail'][:240])}{"…" if len(init['detail'])>240 else ""}</p>
</div>"""

    if not init_cards:
        init_cards = '<p style="color:var(--mute)">No verified initiatives recorded for this district yet. <a href="/research/register.html" class="link">Register an initiative in this district →</a></p>'

    def cr(x): return f"₹{x:.2f} Cr" if x else "—"
    total4 = sum(vals)
    state_avg24 = sum(r["fy24"] for r in DISTRICT_ROWS) / 38
    vs_avg = "above" if d["fy24"] > state_avg24 else "below"

    # Narrative & opportunities
    dev_context, opps, orvys_view = district_narrative(d)
    opps_html = ""
    for title, descr in opps:
        opps_html += f"""
<div class="pillar" style="padding:24px 0;border-right:0;border-bottom:1px solid var(--line)">
  <h4 style="font-size:18px;margin-bottom:6px">{esc(title)}</h4>
  <p style="color:var(--mute);font-size:15px;margin:0">{esc(descr)}</p>
</div>"""

    # Adjacent/nearby districts
    sorted_all = sorted(DISTRICT_ROWS, key=lambda r: r["name"])
    idx = [i for i, r in enumerate(sorted_all) if r["name"] == name][0]
    nearby = [sorted_all[(idx - 2) % len(sorted_all)],
              sorted_all[(idx - 1) % len(sorted_all)],
              sorted_all[(idx + 1) % len(sorted_all)],
              sorted_all[(idx + 2) % len(sorted_all)]]
    nearby_links = "".join(f'<a href="/research/districts/{r["slug"]}.html" class="chip" style="font-size:13px">{esc(r["name"])}</a>' for r in nearby)

    content = f"""
<article>
<header class="post-head">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("Districts","/research/districts/index.html"),(name, None))}
    <span class="chip">District Profile</span>
    <h1>{esc(name)} {tags_html}</h1>
    <p class="lede">District-level CSR data, development deficits, and investment opportunities in {esc(name)}, Bihar.</p>
    <div class="byline">Orvys Research · November 2026 · Source: MCA Parliamentary Data</div>
    {print_btn()}
  </div>
</header>

<div class="wrap" style="margin-top:48px">

<div class="stats rv" style="margin-bottom:60px">
  <div><b>{cr(d['fy24'])}</b><span>CSR in FY 2023-24</span></div>
  <div><b>₹{d['pc24']:.1f}</b><span>per person (state avg: ₹{sum(r['fy24'] for r in DISTRICT_ROWS)*1e7/BIHAR_POP:.1f})</span></div>
  <div><b>{cr(total4)}</b><span>Total CSR, FY21–FY24</span></div>
  <div><b>#{d['rank24']}</b><span>state rank of 38 districts</span></div>
</div>

<div class="narrow rv">
  <span class="chip">Development Context</span>
  <h2 style="margin-top:16px">Socio-Economic &amp; CSR Profile</h2>
  <p style="color:var(--mute);margin:16px 0 24px;line-height:1.75;font-size:17px">{esc(dev_context)}</p>
</div>

<div class="narrow rv" style="margin-top:60px">
  <span class="chip">4-Year Trend</span>
  <h2 style="margin-top:16px">CSR Inflows in {esc(name)}</h2>
</div>
<div class="chart-wrap rv" style="margin:24px 0 60px">{chart}</div>

<div class="narrow rv">
  <span class="chip">Investment Opportunities</span>
  <h2 style="margin-top:16px">Priority CSR Interventions</h2>
  <div style="margin-top:24px">{opps_html}</div>
</div>

<div class="narrow rv" style="margin-top:60px">
  <div class="formcard" style="border-left:4px solid var(--gold)">
    <span class="chip" style="color:var(--gold)">Orvys Perspective</span>
    <h3 style="margin:14px 0 10px">Strategic Assessment</h3>
    <p style="color:var(--mute);font-size:16px;line-height:1.7;margin:0">{esc(orvys_view)}</p>
  </div>
</div>

<div class="narrow rv" style="margin-top:60px">
  <span class="chip">Active Programmes</span>
  <h2 style="margin-top:16px">Known CSR Activity in {esc(name)}</h2>
  <p style="color:var(--mute);margin:12px 0 24px">Verified corporate and statewide programmes operating within {esc(name)} district.</p>
  <div style="margin-bottom:60px">{init_cards}</div>
</div>

<div class="narrow rv formcard" style="margin-bottom:60px">
  <span class="chip">District Factsheet</span>
  <table style="margin-top:16px;width:100%;font-size:15px;border-collapse:collapse">
    <tr><td style="padding:10px 0;color:var(--mute);width:220px">Census 2011 Population</td><td style="font-weight:600">{d['pop']:,}</td></tr>
    <tr><td style="padding:10px 0;color:var(--mute)">NITI Aayog Aspirational</td><td>{"Yes — Aspirational District" if d['aspirational'] else "No"}</td></tr>
    <tr><td style="padding:10px 0;color:var(--mute)">Riparian Flood Belt</td><td>{"Yes — Kosi-Seemanchal Flood Belt" if d['flood'] else "No"}</td></tr>
    <tr><td style="padding:10px 0;color:var(--mute)">FY 2020-21 CSR</td><td>{cr(s[0])}</td></tr>
    <tr><td style="padding:10px 0;color:var(--mute)">FY 2021-22 CSR</td><td>{cr(s[1])}</td></tr>
    <tr><td style="padding:10px 0;color:var(--mute)">FY 2022-23 CSR</td><td>{cr(s[2])}</td></tr>
    <tr><td style="padding:10px 0;color:var(--mute);font-weight:700">FY 2023-24 CSR</td><td style="font-weight:700">{cr(s[3])}</td></tr>
    <tr><td style="padding:10px 0;color:var(--mute)">4-Year Cumulative CSR</td><td style="font-weight:700;color:var(--gold)">{cr(total4)}</td></tr>
  </table>
</div>

<div class="narrow rv" style="margin-bottom:60px;text-align:center">
  <span class="eyebrow" style="margin-bottom:12px">Explore More Districts</span>
  <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:16px">
    {nearby_links}
  </div>
  <p style="margin-top:20px"><a href="/research/districts/index.html" class="link">View all 38 Bihar districts →</a></p>
</div>

{sources_block(["rs1010","census"])}
</div>
</article>

{orvys_cta(f"Invest in {name}.", f"Orvys designs and deploys targeted CSR programmes in {name} with vetted local partners, baseline surveys, and third-party outcome measurement.")}
"""
    return wrap_page(content,
        title=f"{name} District CSR Data &amp; Opportunities | Orvys Research",
        desc=f"CSR spend data, development context and investment opportunities for {name} district, Bihar. FY24 spend: ₹{d['fy24']:.2f} Cr.",
        path=f"research/districts/{d['slug']}.html")


# ── 9 · District index ────────────────────────────────────────────────────────

def build_district_index():
    table_rows = ""
    for d in sorted(DISTRICT_ROWS, key=lambda r: -r["fy24"]):
        tags = ""
        if d["aspirational"]: tags += ' <span class="tag-asp">A</span>'
        if d["flood"]: tags += ' <span class="tag-flood">F</span>'
        table_rows += f"""<tr>
  <td><a href="/research/districts/{d['slug']}.html" style="font-weight:600;color:var(--navy)">{esc(d['name'])}</a>{tags}</td>
  <td>{d['pop'] / 100000:.1f} L</td>
  <td>₹{d['total']:.2f} Cr</td>
  <td style="font-weight:700">₹{d['fy24']:.2f} Cr</td>
  <td>₹{d['pc24']:.1f}</td>
  <td>#{d['rank24']}</td>
  <td><a href="/research/districts/{d['slug']}.html" class="link" style="font-size:13px">Profile →</a></td>
</tr>"""

    cards = ""
    for d in sorted(DISTRICT_ROWS, key=lambda r: r["name"]):
        tags = ""
        if d["aspirational"]: tags += '<span class="tag-asp">A</span>'
        if d["flood"]: tags += '<span class="tag-flood">F</span>'
        cards += f"""
<a class="dist-mini rv" href="/research/districts/{d['slug']}.html">
  <strong>{esc(d['name'])}</strong>{tags}
  <span>₹{d['fy24']:.2f} Cr <small>FY24</small></span>
</a>"""

    content = f"""
<section class="post-head" style="padding-bottom:40px">
  <div class="wrap narrow">
    {breadcrumb(("Home","/"),("Research","/research/index.html"),("All Districts",None))}
    <span class="chip">District Directory</span>
    <h1>Bihar CSR by District: All 38 Districts</h1>
    <p class="lede">Comprehensive district-by-district CSR directory with population, 4-year cumulative funding, and per-capita indicators.</p>
    <div class="byline">Orvys Research Team · November 2026 · 38 Districts Mapped</div>
    {print_btn()}
  </div>
</section>

<section style="padding-top:20px">
  <div class="wrap">
    <div class="formcard rv" style="overflow-x:auto">
      <table style="width:100%;border-collapse:collapse;font-size:14.5px;min-width:700px">
        <thead>
          <tr style="background:var(--navy);color:#fff">
            <th style="text-align:left;padding:12px 10px">District</th>
            <th style="padding:12px 10px">Pop (2011)</th>
            <th style="padding:12px 10px">Total (4-Yr)</th>
            <th style="padding:12px 10px">FY24 Spend</th>
            <th style="padding:12px 10px">₹/Person</th>
            <th style="padding:12px 10px">State Rank</th>
            <th style="padding:12px 10px">Profile</th>
          </tr>
        </thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
    
    <div style="margin-top:64px">
      <div class="narrow rv"><span class="chip">Quick Directory</span><h2 style="margin-top:16px">Browse by name</h2></div>
      <div class="dist-grid" style="margin-top:24px">{cards}</div>
    </div>
    
    <p class="small muted" style="margin-top:24px">
      <span class="tag-asp">A</span> = NITI Aayog Aspirational District ·
      <span class="tag-flood">F</span> = Kosi-Seemanchal Riparian Flood Belt ·
      Data: Ministry of Corporate Affairs (Rajya Sabha UQ 1010, Dec 2025).
    </p>
  </div>
</section>

{orvys_cta("Select a district. We'll design your programme.", "Orvys has vetted partner networks and ground data across all 38 Bihar districts.")}
"""
    return wrap_page(content,
        title="Bihar CSR by District: All 38 Districts Directory | Orvys Research",
        desc="CSR spend, population, and investment data for all 38 Bihar districts. Updated November 2026 from official parliamentary data.",
        path="research/districts/index.html")


# ── Main: generate all files ──────────────────────────────────────────────────

def generate_all(root_path=None):
    if root_path is None:
        root_path = ROOT
    root = pathlib.Path(root_path)

    hub = build_hub()
    diag = build_diagnostic()
    policy = build_policy()
    skilling = build_skilling()
    tracker = build_tracker()
    eco = build_ecosystem()
    register = build_register()
    dist_index = build_district_index()

    pages = {
        "research/index.html": hub,
        "research/diagnostic.html": diag,
        "research/bihar-csr-diagnostic.html": diag,
        "research/policy.html": policy,
        "research/bihar-csr-policy.html": policy,
        "research/skilling.html": skilling,
        "research/bihar-csr-skilling.html": skilling,
        "research/tracker.html": tracker,
        "research/initiatives-tracker.html": tracker,
        "research/ecosystem.html": eco,
        "research/register.html": register,
        "research/districts/index.html": dist_index,
    }
    for d in DISTRICT_ROWS:
        pages[f"research/districts/{d['slug']}.html"] = build_district(d)

    written = []
    for rel, content in pages.items():
        dest = root / "src" / "pages" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        written.append(rel)

    print(f"generate.py: wrote {len(written)} research pages to src/pages/research/")
    return written


if __name__ == "__main__":
    generate_all()
