"""Rebuild index.html #view-ai to match the approved mockup (image 2): 5 AI Consulting
Service cards, 4 AI Product cards side-by-side, and a How We Deliver 3-box row, on the
dark navy Option-2 background. Uses EXPLICIT CSS grid (not Tailwind utilities that may
not be compiled -- e.g. base .grid-cols-4 does not exist in the compiled stylesheet)."""
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

def card(title, body):
    return (f'''                            <div class="aix-card">
                                <div class="aix-h">{title}</div>
                                <div class="aix-b">{body}</div>
                            </div>''')

consult_cards = "\n".join(card(a, b) for a, b in CONSULT)
prod_cards = "\n".join(card(a, b) for a, b in PRODUCTS)

new = f'''<div id="view-ai" hidden>
                    <style>
                      #services{{position:relative;}}
                      body.ai-mode #services::before{{content:"";position:absolute;left:calc(50% - 50vw);width:100vw;top:0;bottom:0;background:#17222f;z-index:0;}}
                      body.ai-mode #services > div{{position:relative;z-index:1;}}
                      body.ai-mode #svcHeading{{color:#f2f6fa;}}
                      body.ai-mode #svcIntro{{color:#9fb1c2;}}
                      .aix-row{{display:grid;grid-template-columns:128px minmax(0,1fr) 96px;gap:12px;align-items:stretch;margin-bottom:12px;}}
                      .aix-lbl{{display:flex;align-items:center;justify-content:center;text-align:center;background:rgba(255,255,255,0.05);border-radius:8px;padding:14px 8px;}}
                      .aix-lbl span{{font-family:'Lato',sans-serif;font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#e9a765;line-height:1.5;}}
                      .aix-cards{{display:grid;gap:12px;}}
                      .aix-c5{{grid-template-columns:repeat(5,minmax(0,1fr));}}
                      .aix-c4{{grid-template-columns:repeat(4,minmax(0,1fr));}}
                      .aix-c3{{grid-template-columns:repeat(3,minmax(0,1fr));}}
                      .aix-card{{display:flex;flex-direction:column;gap:10px;}}
                      .aix-h{{background:#e08a3c;color:#2a1a08;border-radius:8px;padding:10px;height:80px;display:flex;align-items:center;justify-content:center;text-align:center;font-family:'Lato',sans-serif;font-weight:700;font-size:18px;line-height:1.2;}}
                      .aix-b{{background:#FAF4EC;color:#44566a;border-radius:8px;padding:14px 12px;flex:1;min-height:158px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:14px;line-height:1.5;}}
                      .aix-rail{{border-radius:8px;display:flex;align-items:center;justify-content:center;text-decoration:none;}}
                      .aix-rail span{{writing-mode:vertical-rl;transform:rotate(180deg);font-family:'Lato',sans-serif;font-weight:700;font-size:18px;letter-spacing:.04em;padding:14px 0;display:inline-flex;align-items:center;gap:6px;}}
                      .aix-r1{{background:#e08a3c;color:#2a1a08;}}
                      .aix-r2{{background:#88C9BE;color:#1C2A36;}}
                      .aix-xfn{{display:flex;align-items:center;justify-content:center;text-align:center;background:#FAF4EC;border:2px solid #B45309;border-radius:8px;padding:12px 16px;height:72px;color:#334b60;font-family:'Lato',sans-serif;font-weight:700;font-size:16px;line-height:1.25;text-decoration:none;transition:transform .15s ease;}}
                      .aix-xfn:hover{{transform:translateY(-2px);}}
                      @media(max-width:1023px){{
                        .aix-row{{grid-template-columns:1fr;gap:10px;margin-bottom:20px;}}
                        .aix-cards{{grid-template-columns:1fr !important;}}
                        .aix-rail{{display:none;}}
                        .aix-lbl{{justify-content:flex-start;padding:10px 4px;}}
                      }}
                    </style>

                    <div class="aix-row">
                        <div class="aix-lbl"><span>AI Consulting<br>Services</span></div>
                        <div class="aix-cards aix-c5">
{consult_cards}
                        </div>
                        <div class="aix-rail aix-r1"><span>Consulting</span></div>
                    </div>

                    <div class="aix-row">
                        <div class="aix-lbl"><span>AI Products</span></div>
                        <div class="aix-cards aix-c4">
{prod_cards}
                        </div>
                        <a class="aix-rail aix-r2" href="https://managedsuppliers.com" target="_blank" rel="noopener"><span>managedsuppliers <i class="ph ph-arrow-up-right" style="font-size:13px;"></i></span></a>
                    </div>

                    <div class="aix-row">
                        <div class="aix-lbl"><span>Cross-Functional<br>Services</span></div>
                        <div class="aix-cards aix-c3">
                            <a class="aix-xfn" href="support-services.html#transformation-implementation">Transformation Implementation</a>
                            <a class="aix-xfn" href="support-services.html#program-project">Program and Project Management</a>
                            <a class="aix-xfn" href="support-services.html#change-communication">Change and Communication</a>
                        </div>
                        <div class="aix-rail" style="visibility:hidden;"></div>
                    </div>

                </div>'''

t2 = t[:start] + new + t[end:]
print('new div balance:', new.count('<div') - new.count('</div'), '(want 0)')
if APPLY:
    open(p, 'w', encoding='utf-8', newline='').write(t2)
    print('APPLIED')
else:
    print('DRY-RUN len', len(new))
