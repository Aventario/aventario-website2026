"""Rebuild index.html #view-ai: matrix mirroring the Consulting view's structure and
typography (font-serif text-lg titles, text-sm bodies, w-32/w-24 rails, gap-3), in the
dark Option 2 theme. Cohesive dark section (no two-tone), no top divider, Cross-Functional
= the three real support-service boxes, and the How-we-deliver band flush to the bright edge."""
import re, sys
APPLY = '--apply' in sys.argv
p = 'index.html'
t = open(p, encoding='utf-8').read()

start = t.find('<div id="view-ai" hidden>')
assert start != -1, 'view-ai not found'
i = start; depth = 0; tag = re.compile(r'<(/?)div\b', re.I); end = None
while True:
    m = tag.search(t, i)
    if not m: break
    depth += 1 if m.group(1) == '' else -1
    i = m.end()
    if depth == 0:
        end = t.find('>', m.end()) + 1; break
assert end, 'no balanced close'

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
XFN = [
    ("Transformation Implementation", "support-services.html#transformation-implementation"),
    ("Program and Project Management", "support-services.html#program-project"),
    ("Change and Communication", "support-services.html#change-communication"),
]

def dcard(title, body):
    return (f'''                            <div class="flex flex-col gap-2">
                                <div class="rounded-md p-3 flex items-center justify-center text-center min-h-[76px]" style="background-color:#e08a3c;color:#2a1a08;"><h3 class="font-serif text-lg leading-tight">{title}</h3></div>
                                <div class="rounded-md p-4 flex-1 flex items-center justify-center text-center" style="background-color:#FAF4EC;color:#44566a;"><p class="text-sm leading-relaxed">{body}</p></div>
                            </div>''')

def mcard(title, body):
    return (f'''                        <div class="rounded-md overflow-hidden">
                            <div class="p-3 text-center" style="background-color:#e08a3c;color:#2a1a08;"><h3 class="font-serif text-lg leading-tight">{title}</h3></div>
                            <div class="p-4 text-center" style="background-color:#FAF4EC;color:#44566a;"><p class="text-sm leading-relaxed">{body}</p></div>
                        </div>''')

consult_d = "\n".join(dcard(t_, b) for t_, b in CONSULT)
prod_d = "\n".join(dcard(t_, b) for t_, b in PRODUCTS)
consult_m = "\n".join(mcard(t_, b) for t_, b in CONSULT)
prod_m = "\n".join(mcard(t_, b) for t_, b in PRODUCTS)
xfn_d = "\n".join(f'''                            <a href="{u}" class="rounded-md flex items-center justify-center text-center p-4 border-2 min-h-[72px] transition-transform hover:-translate-y-0.5" style="background-color:#FAF4EC;border-color:#B45309;"><span class="font-bold text-base" style="color:#334b60;">{n}</span></a>''' for n, u in XFN)
xfn_m = "\n".join(f'''                        <a href="{u}" class="block rounded-md p-3 text-center border-2 font-bold text-base" style="background-color:#FAF4EC;border-color:#B45309;color:#334b60;">{n}</a>''' for n, u in XFN)

new = f'''<div id="view-ai" hidden>
                    <style>
                      #services{{position:relative;}}
                      body.ai-mode #services::before{{content:"";position:absolute;left:calc(50% - 50vw);width:100vw;top:0;bottom:0;background:#17222f;z-index:0;}}
                      body.ai-mode #services > div{{position:relative;z-index:1;}}
                      body.ai-mode #services{{padding-bottom:0;}}
                      body.ai-mode #svcHeading{{color:#f2f6fa;}}
                      body.ai-mode #svcIntro{{color:#9fb1c2;}}
                      .aiv-lbl{{background:rgba(255,255,255,0.05);}}
                      .aiv-lbl p{{color:#e9a765;}}
                      .aiv-band{{position:relative;width:100vw;margin-left:calc(50% - 50vw);overflow:hidden;margin-top:2.5rem;margin-bottom:0;}}
                      .aiv-band__pad{{position:relative;max-width:1400px;margin:0 auto;padding:3rem 1.5rem;}}
                      @media(min-width:768px){{.aiv-band__pad{{padding:4.5rem 3rem;}}}}
                      .aiv-hl{{display:grid;grid-template-columns:1fr;gap:1.6rem;}}
                      @media(min-width:640px){{.aiv-hl{{grid-template-columns:repeat(3,1fr);}}}}
                      .aiv-hl__i{{display:flex;gap:1rem;align-items:center;}}
                      .aiv-hl__i i{{color:#f19a51;font-size:3rem;line-height:1;flex:0 0 auto;}}
                      .aiv-hl__i p{{color:#FAFAF7;line-height:1.5;font-size:1.05rem;margin:0;}}
                      .aiv-hl__i strong{{color:#fff;}}
                    </style>

                    <!-- Desktop matrix (mirrors the Consulting matrix: w-32 labels, gap-3, font-serif text-lg) -->
                    <div class="hidden lg:block">
                        <div class="flex flex-col gap-3">

                            <div class="flex gap-3">
                                <div class="aiv-lbl w-32 shrink-0 rounded-md flex items-center justify-center p-3"><p class="text-xs uppercase tracking-widest font-bold text-center">AI Consulting<br>Services</p></div>
                                <div class="flex-1 grid grid-cols-5 gap-3">
{consult_d}
                                </div>
                                <div class="w-24 shrink-0 rounded-md flex items-center justify-center" style="background-color:#e08a3c;color:#2a1a08;"><h3 class="font-serif text-lg leading-tight" style="writing-mode:vertical-rl;transform:rotate(180deg);">Consulting</h3></div>
                            </div>

                            <div class="flex gap-3">
                                <div class="aiv-lbl w-32 shrink-0 rounded-md flex items-center justify-center p-3"><p class="text-xs uppercase tracking-widest font-bold text-center">AI Products</p></div>
                                <div class="flex-1 grid grid-cols-4 gap-3">
{prod_d}
                                </div>
                                <a href="https://managedsuppliers.com" target="_blank" rel="noopener" class="w-24 shrink-0 rounded-md flex items-center justify-center hover:opacity-95 transition-opacity" style="background-color:#88C9BE;color:#1C2A36;"><h3 class="font-serif text-lg leading-tight" style="writing-mode:vertical-rl;transform:rotate(180deg);">managedsuppliers <i class="ph ph-arrow-up-right text-sm"></i></h3></a>
                            </div>

                            <div class="flex gap-3">
                                <div class="aiv-lbl w-32 shrink-0 rounded-md flex items-center justify-center p-3"><p class="text-xs uppercase tracking-widest font-bold text-center">Cross-Functional<br>Services</p></div>
                                <div class="flex-1 grid grid-cols-3 gap-3">
{xfn_d}
                                </div>
                                <div class="w-24 shrink-0"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Mobile stacked -->
                    <div class="lg:hidden space-y-8">
                        <div>
                            <p class="text-xs uppercase tracking-widest font-bold mb-3" style="color:#e9a765;">AI Consulting Services</p>
                            <div class="grid grid-cols-1 gap-3">
{consult_m}
                            </div>
                        </div>
                        <div>
                            <p class="text-xs uppercase tracking-widest font-bold mb-3" style="color:#e9a765;">AI Products</p>
                            <div class="grid grid-cols-1 gap-3">
{prod_m}
                            </div>
                            <a href="https://managedsuppliers.com" target="_blank" rel="noopener" class="mt-3 block rounded-md p-3 text-center font-serif text-lg" style="background-color:#88C9BE;color:#1C2A36;">managedsuppliers <i class="ph ph-arrow-up-right text-sm"></i></a>
                        </div>
                        <div>
                            <p class="text-xs uppercase tracking-widest font-bold mb-3" style="color:#e9a765;">Cross-Functional Services</p>
                            <div class="grid grid-cols-1 gap-2">
{xfn_m}
                            </div>
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
    print('DRY-RUN, new len', len(new))
