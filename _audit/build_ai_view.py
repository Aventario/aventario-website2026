"""Rebuild index.html #view-ai. Layout: labels per row (col 1), card grids per row
(col 2), and a SINGLE right rail column (col 3) that spans all three rows split 50/50
(Consulting top / managedsuppliers bottom) so managedsuppliers is not tied to AI Products.
Cross-Functional label matches the box height (grid row). How-we-deliver mountain band
re-added below, flush to the bright section edge."""
import re, sys
APPLY = '--apply' in sys.argv
p = 'index.html'
t = open(p, encoding='utf-8').read()

start = t.find('<div id="view-ai" hidden>')
assert start != -1
i = start; depth = 0; tag = re.compile(r'<(/?)div\b', re.I); end = None
while True:
    m = tag.search(t, i)
    if not m: break
    depth += 1 if m.group(1) == '' else -1
    i = m.end()
    if depth == 0:
        end = t.find('>', m.end()) + 1; break
assert end

CONSULT = [
    ("AI Awareness and Enablement", "Creative workshops for AI use-case identification and qualification with IT and business."),
    ("AI Empowerment", "Workshops and trainings for AI usage in specific work situations, for example prompting techniques for internal auditors."),
    ("AI Process Efficiency Elevation", "Evaluation of complex processes to find efficiency gains through AI agents and automation, plus the definition of the related concepts."),
    ("AI Team Efficiency Elevation", "Structured evaluation of all core tasks across an organization to identify every AI potential."),
    ("AI Proof of Concepts", "Implementation of PoCs to evaluate impact and to enable qualified decision-making."),
]
PRODUCTS = [
    ("AI Contract Analyzer", "AI-based agent for mass contract analysis that identifies improvement potential in existing contracts. Relevant for M&amp;A, audits, vendor consolidations, and cost-saving initiatives."),
    ("AI Tender Manager", "AI-based review, evaluation, and rating of incoming supplier offers, with identification of the required improvements and next steps with suppliers."),
    ("AI Contract2Invoice Inspector", "AI-based agent that checks incoming invoices against the price units and contract terms held in the underlying contracts."),
    ("Vendor and Contract Managed Services", "Manage, improve, and renegotiate selected contract bundles, combining subject-matter experts with Aventario's AI products to run contracts efficiently."),
]

def card(a, b):
    return (f'''                            <div class="aix-card">
                                <div class="aix-h">{a}</div>
                                <div class="aix-b">{b}</div>
                            </div>''')

consult_cards = "\n".join(card(a, b) for a, b in CONSULT)
prod_cards = "\n".join(card(a, b) for a, b in PRODUCTS)

new = f'''<div id="view-ai" hidden>
                    <style>
                      #services{{position:relative;}}
                      body.ai-mode #services::before{{content:"";position:absolute;left:calc(50% - 50vw);width:100vw;top:0;bottom:0;background:#17222f;z-index:0;}}
                      body.ai-mode #services > div{{position:relative;z-index:1;}}
                      body.ai-mode #services{{padding-bottom:0;}}
                      body.ai-mode #svcHeading{{color:#f2f6fa;}}
                      body.ai-mode #svcIntro{{color:#9fb1c2;}}
                      .aix-matrix{{display:grid;grid-template-columns:128px minmax(0,1fr) 96px;gap:12px;}}
                      .aix-lbl{{display:flex;align-items:center;justify-content:center;text-align:center;background:rgba(255,255,255,0.05);border-radius:8px;padding:10px 8px;}}
                      .aix-lbl span{{font-family:'Lato',sans-serif;font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#e9a765;line-height:1.5;}}
                      .aix-cards{{display:grid;gap:12px;grid-auto-rows:1fr;}}
                      .aix-c5{{grid-template-columns:repeat(5,minmax(0,1fr));}}
                      .aix-c4{{grid-template-columns:repeat(4,minmax(0,1fr));}}
                      .aix-c3{{grid-template-columns:repeat(3,minmax(0,1fr));}}
                      .aix-card{{display:flex;flex-direction:column;gap:10px;}}
                      .aix-h{{background:#e08a3c;color:#2a1a08;border-radius:8px;padding:10px;height:80px;display:flex;align-items:center;justify-content:center;text-align:center;font-family:'Lato',sans-serif;font-weight:700;font-size:18px;line-height:1.2;}}
                      .aix-b{{background:#FAF4EC;color:#44566a;border-radius:8px;padding:14px 12px;flex:1;min-height:158px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:14px;line-height:1.5;}}
                      .aix-xfn{{display:flex;align-items:center;justify-content:center;text-align:center;background:#FAF4EC;border:2px solid #B45309;border-radius:8px;padding:12px 16px;min-height:72px;color:#334b60;font-family:'Lato',sans-serif;font-weight:700;font-size:16px;line-height:1.25;text-decoration:none;transition:transform .15s ease;}}
                      .aix-xfn:hover{{transform:translateY(-2px);}}
                      .aix-railcol{{grid-column:3;grid-row:1 / span 3;display:flex;flex-direction:column;gap:12px;}}
                      .aix-rail{{flex:1;min-height:150px;border-radius:8px;display:flex;align-items:center;justify-content:center;text-decoration:none;}}
                      .aix-rail span{{writing-mode:vertical-rl;transform:rotate(180deg);font-family:'Lato',sans-serif;font-weight:700;font-size:18px;letter-spacing:.04em;padding:14px 0;display:inline-flex;align-items:center;gap:6px;}}
                      .aix-r1{{background:#e08a3c;color:#2a1a08;}}
                      .aix-r2{{background:#88C9BE;color:#1C2A36;}}
                      .aiv-band{{position:relative;width:100vw;margin-left:calc(50% - 50vw);overflow:hidden;margin-top:2.5rem;margin-bottom:0;}}
                      .aiv-band__pad{{position:relative;max-width:1400px;margin:0 auto;padding:3rem 1.5rem;}}
                      @media(min-width:768px){{.aiv-band__pad{{padding:4.5rem 3rem;}}}}
                      .aiv-hl{{display:grid;grid-template-columns:1fr;gap:1.6rem;}}
                      @media(min-width:640px){{.aiv-hl{{grid-template-columns:repeat(3,1fr);}}}}
                      .aiv-hl__i{{display:flex;gap:1rem;align-items:center;}}
                      .aiv-hl__i i{{color:#f19a51;font-size:3rem;line-height:1;flex:0 0 auto;}}
                      .aiv-hl__i p{{color:#FAFAF7;line-height:1.5;font-size:1.05rem;margin:0;}}
                      .aiv-hl__i strong{{color:#fff;}}
                      @media(max-width:1023px){{
                        .aix-matrix{{display:block;}}
                        .aix-lbl{{justify-content:flex-start;padding:8px 4px;margin-bottom:8px;}}
                        .aix-cards{{grid-template-columns:1fr !important;margin-bottom:20px;}}
                        .aix-railcol{{display:none;}}
                      }}
                    </style>

                    <div class="aix-matrix">
                        <div class="aix-lbl" style="grid-column:1;grid-row:1;"><span>AI Consulting<br>Services</span></div>
                        <div class="aix-cards aix-c5" style="grid-column:2;grid-row:1;">
{consult_cards}
                        </div>

                        <div class="aix-lbl" style="grid-column:1;grid-row:2;"><span>AI Products</span></div>
                        <div class="aix-cards aix-c4" style="grid-column:2;grid-row:2;">
{prod_cards}
                        </div>

                        <div class="aix-lbl" style="grid-column:1;grid-row:3;"><span>Cross-Functional<br>Services</span></div>
                        <div class="aix-cards aix-c3" style="grid-column:2;grid-row:3;">
                            <a class="aix-xfn" href="support-services.html#transformation-implementation">Transformation Implementation</a>
                            <a class="aix-xfn" href="support-services.html#program-project">Program and Project Management</a>
                            <a class="aix-xfn" href="support-services.html#change-communication">Change and Communication</a>
                        </div>

                        <div class="aix-railcol">
                            <div class="aix-rail aix-r1"><span>Consulting</span></div>
                            <a class="aix-rail aix-r2" href="https://managedsuppliers.com" target="_blank" rel="noopener"><span>managedsuppliers <i class="ph ph-arrow-up-right" style="font-size:13px;"></i></span></a>
                        </div>
                    </div>

                    <div class="aiv-band">
                        <img src="images/photography/team-ridge-sunrise.jpg" alt="" role="presentation" class="absolute inset-0 w-full h-full object-cover" style="object-position:center 40%;" loading="lazy" decoding="async">
                        <div class="absolute inset-0" style="background:linear-gradient(90deg, rgba(13,19,30,0.94) 0%, rgba(13,19,30,0.78) 55%, rgba(13,19,30,0.50) 100%);"></div>
                        <div class="aiv-band__pad">
                            <h3 class="font-serif text-3xl md:text-4xl mb-10" style="color:#FAFAF7;">How we deliver</h3>
                            <div class="aiv-hl">
                                <div class="aiv-hl__i"><i class="ph ph-users-three"></i><p><strong>Experienced consultants</strong> manage the engagement.</p></div>
                                <div class="aiv-hl__i"><i class="ph ph-magnifying-glass"></i><p><strong>Subject matter experts</strong> perform the analysis and evaluation.</p></div>
                                <div class="aiv-hl__i"><i class="ph ph-cpu"></i><p>Delivery is <strong>enabled by advanced AI technology</strong>.</p></div>
                            </div>
                        </div>
                    </div>

                </div>'''

t2 = t[:start] + new + t[end:]
print('new div balance:', new.count('<div') - new.count('</div'), '(want 0)')
if APPLY:
    open(p, 'w', encoding='utf-8', newline='').write(t2)
    print('APPLIED')
else:
    print('DRY len', len(new))
