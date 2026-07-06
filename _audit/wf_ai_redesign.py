#!/usr/bin/env python3
"""Landing-page AI-view redesign (index.html, ai-toggle branch).
1) Split the consulting-matrix right column: top half Aventario AI, bottom half managedsuppliers.
2) Rebuild the AI view in the consulting-matrix card style (no numbers), products in orange,
   services in navy, plus a highlights band using the team image with bigger icons.
3) Remove the standalone editorial band (its picture moves up into the highlights)."""
import re, os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
html = open(P, encoding='utf-8').read()

# ---- 1) split the AI vertical column ------------------------------------
OLD_COL = '''                        <!-- Aventario AI vertical right column — switches the section to the AI portfolio -->
                        <button type="button" onclick="setSvcView('ai')" aria-label="View the Aventario AI portfolio" class="w-24 shrink-0 flex flex-col rounded-md p-4 cursor-pointer hover:opacity-95 transition-opacity" style="background-color: #f19a51; color: #3a2410;">
                            <div class="flex-1 flex items-center justify-center">
                                <h3 class="font-serif text-2xl leading-tight" style="writing-mode: vertical-rl; transform: rotate(180deg);">Aventario AI <i class="ph ph-sparkle text-base"></i></h3>
                            </div>
                            <p class="text-[10px] uppercase tracking-widest font-bold text-center mt-2">AI<br>portfolio</p>
                            <!-- spacer mirroring the cross-functional row so the side column ends above it -->
                            <div class="h-20"></div>
                        </button>'''
NEW_COL = '''                        <!-- Right column: top half Aventario AI (switch), bottom half managedsuppliers -->
                        <div class="w-24 shrink-0 flex flex-col gap-3">
                            <button type="button" onclick="setSvcView('ai')" aria-label="View the Aventario AI portfolio" class="flex-1 flex items-center justify-center rounded-md p-3 cursor-pointer hover:opacity-95 transition-opacity" style="background-color: #f19a51; color: #3a2410;">
                                <h3 class="font-serif text-xl leading-tight" style="writing-mode: vertical-rl; transform: rotate(180deg);">Aventario AI <i class="ph ph-sparkle text-sm"></i></h3>
                            </button>
                            <a href="https://managedsuppliers.com" target="_blank" rel="noopener" class="flex-1 flex items-center justify-center rounded-md p-3 hover:opacity-95 transition-opacity" style="background-color: #88C9BE; color: #1C2A36;">
                                <h3 class="font-serif text-xl leading-tight" style="writing-mode: vertical-rl; transform: rotate(180deg);">managedsuppliers <i class="ph ph-arrow-up-right text-sm"></i></h3>
                            </a>
                            <div class="h-20"></div>
                        </div>'''
assert OLD_COL in html, 'column block not found'
html = html.replace(OLD_COL, NEW_COL, 1)

# ---- 2) rebuild the AI view (from "<!-- AI Products -->" to the USP close) ----
def card(title, desc, hbg, hcol, tcls, dcls):
    return (f'                        <div class="ai-card">\n'
            f'                            <div class="ai-card__h" style="background:{hbg};color:{hcol};"><h4 class="font-serif {tcls} leading-tight">{title}</h4></div>\n'
            f'                            <p class="ai-card__b {dcls}">{desc}</p>\n'
            f'                        </div>\n')

products = [
    ('AI Contract Analyzer', "AI-based agent for mass contract analysis that identifies improvement potential in existing contracts. Relevant for M&amp;A, audits, vendor consolidations, and cost-saving initiatives."),
    ('AI Tender Manager', "AI-based review, evaluation, and rating of incoming supplier offers, with identification of the required improvements and next steps with suppliers."),
    ('AI Contract2Invoice Inspector', "AI-based agent that checks incoming invoices against the price units and contract terms held in the underlying contracts."),
    ('Vendor and Contract Managed Services', "Manage, improve, and renegotiate selected contract bundles, combining subject-matter experts with Aventario's AI products to run contracts efficiently."),
]
services = [
    ('AI Awareness and Enablement', "Creative workshops for AI use-case identification and qualification with IT and business."),
    ('AI Empowerment', "Workshops and trainings for AI usage in specific work situations, for example prompting techniques for internal auditors."),
    ('AI Process Efficiency Elevation', "Evaluation of complex processes to find efficiency gains through AI agents and automation, plus the definition of the related concepts."),
    ('AI Team Efficiency Elevation', "Structured evaluation of all core tasks across an organization to identify every AI potential."),
    ('AI Proof of Concepts', "Implementation of PoCs to evaluate impact and to enable qualified decision-making."),
]
prod_html = ''.join(card(t, d, '#f19a51', '#3a2410', 'text-lg', 'text-sm') for t, d in products)
svc_html = ''.join(card(t, d, '#334b60', '#FAFAF7', 'text-base', 'text-xs') for t, d in services)

NEW_AI = f'''<!-- Aventario AI view — consulting-matrix card style, no numbers -->
                    <style>
                      .ai-grid{{display:grid;grid-template-columns:1fr;gap:0.75rem;}}
                      @media(min-width:640px){{.ai-grid{{grid-template-columns:repeat(2,1fr);}}}}
                      @media(min-width:1024px){{.ai-prod{{grid-template-columns:repeat(4,1fr);}}.ai-svc{{grid-template-columns:repeat(5,1fr);}}}}
                      .ai-card{{display:flex;flex-direction:column;border:1px solid rgba(51,75,96,0.12);border-radius:8px;overflow:hidden;background:#fff;}}
                      .ai-card__h{{padding:0.9rem 0.7rem;text-align:center;display:flex;align-items:center;justify-content:center;min-height:72px;}}
                      .ai-card__b{{padding:0.9rem;flex:1;color:#5f768b;line-height:1.55;}}
                      .ai-hl{{position:relative;border-radius:12px;overflow:hidden;}}
                      .ai-hl__pad{{position:relative;padding:1.5rem;}}
                      @media(min-width:768px){{.ai-hl__pad{{padding:2.1rem 2.4rem;}}}}
                      .ai-hl__grid{{display:grid;grid-template-columns:1fr;gap:1.3rem;}}
                      @media(min-width:640px){{.ai-hl__grid{{grid-template-columns:repeat(3,1fr);}}}}
                      .ai-hl__item{{display:flex;gap:0.95rem;align-items:center;}}
                      .ai-hl__item i{{color:#f19a51;font-size:2.7rem;line-height:1;flex:0 0 auto;}}
                      .ai-hl__item p{{color:#FAFAF7;line-height:1.5;font-size:0.95rem;margin:0;}}
                      .ai-hl__item strong{{color:#fff;}}
                    </style>

                    <h3 class="font-serif text-2xl text-text mb-4">Aventario AI Products</h3>
                    <div class="ai-grid ai-prod mb-8">
{prod_html}                    </div>

                    <h3 class="font-serif text-2xl text-text mb-4">AI Consulting Service</h3>
                    <div class="ai-grid ai-svc mb-8">
{svc_html}                    </div>

                    <!-- Highlights: team picture moved up here + how we deliver (bigger icons) -->
                    <div class="ai-hl">
                        <img src="images/photography/team-ridge-sunrise.jpg" alt="" role="presentation" class="absolute inset-0 w-full h-full object-cover" style="object-position:center 40%;" loading="lazy" decoding="async">
                        <div class="absolute inset-0" style="background:linear-gradient(90deg, rgba(13,19,30,0.94) 0%, rgba(13,19,30,0.80) 55%, rgba(13,19,30,0.55) 100%);"></div>
                        <div class="ai-hl__pad">
                            <div class="ai-hl__grid">
                                <div class="ai-hl__item"><i class="ph ph-users-three"></i><p><strong>Experienced consultants</strong> manage the engagement.</p></div>
                                <div class="ai-hl__item"><i class="ph ph-magnifying-glass"></i><p><strong>Subject matter experts</strong> perform the analysis and evaluation.</p></div>
                                <div class="ai-hl__item"><i class="ph ph-cpu"></i><p>Delivery is <strong>enabled by advanced AI technology</strong>.</p></div>
                            </div>
                        </div>
                    </div>'''

start = html.index('<!-- AI Products -->')
anchor = 'enabled by advanced AI technology</strong>.</p>'
ai = html.index(anchor, start) + len(anchor)
m = re.match(r'\s*</div>\s*</div>\s*</div>', html[ai:])
assert m, 'USP close not matched'
end = ai + m.end()
html = html[:start] + NEW_AI + html[end:]

# ---- 3) remove the standalone editorial band (picture moved up) ----------
band_start = html.index('<!-- ====== 3b. Editorial band')
band_end = html.index('</section>', band_start) + len('</section>')
html = html[:band_start] + '<!-- editorial band removed: picture moved into the AI highlights -->' + html[band_end:]

open(P, 'w', encoding='utf-8').write(html)
print('AI redesign applied. products:', len(products), 'services:', len(services))
