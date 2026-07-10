"""Replace index.html #view-ai with the approved matrix layout in Option 2 (dark navy +
amber headers + cream bodies), plus the Cross-Functional Services block and mountain band."""
import re, sys
APPLY = '--apply' in sys.argv
p = 'index.html'
t = open(p, encoding='utf-8').read()

start = t.find('<div id="view-ai" hidden>')
assert start != -1, 'view-ai not found'
# balance divs
i = start; depth = 0
tag = re.compile(r'<(/?)div\b', re.I)
end = None
while True:
    m = tag.search(t, i)
    if not m: break
    depth += 1 if m.group(1) == '' else -1
    i = m.end()
    if depth == 0:
        end = t.find('>', m.end()) + 1
        break
assert end, 'no balanced close'
old = t[start:end]

new = '''<div id="view-ai" hidden>
                    <style>
                      .aim{background:#17222f;border-radius:16px;padding:20px 20px 26px;}
                      .aim-rule{height:1px;background:rgba(255,255,255,.12);margin-bottom:20px;}
                      .aim-row{display:grid;grid-template-columns:1fr;gap:12px;margin-bottom:18px;}
                      .aim-lbl{display:flex;align-items:center;justify-content:center;text-align:center;background:#26323f;color:#e9a765;border-radius:10px;padding:12px;font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase;}
                      .aim-cards{display:grid;gap:12px;grid-template-columns:repeat(2,minmax(0,1fr));}
                      .aim-card{display:flex;flex-direction:column;gap:10px;}
                      .aim-h{background:#e08a3c;color:#2a1a08;border-radius:10px;padding:14px 10px;min-height:60px;display:flex;align-items:center;justify-content:center;text-align:center;font-weight:700;font-size:15px;line-height:1.25;}
                      .aim-b{background:#FAF4EC;color:#44566a;border-radius:10px;padding:14px 12px;flex:1;display:flex;align-items:center;justify-content:center;text-align:center;font-size:13px;line-height:1.5;}
                      .aim-rail{display:none;border-radius:10px;text-decoration:none;}
                      .aim-rail span{writing-mode:vertical-rl;transform:rotate(180deg);font-weight:700;font-size:15px;letter-spacing:.05em;padding:14px 0;display:inline-flex;align-items:center;gap:6px;}
                      .aim-r1{background:#e08a3c;color:#2a1a08;}
                      .aim-r2{background:#8dccc0;color:#123a31;}
                      .aim-xfn{background:#FAF4EC;border-radius:12px;padding:22px 24px;}
                      .aim-xfn h4{color:#334b60;font-weight:700;font-size:1.35rem;margin:0 0 12px;}
                      .aim-xfn p{color:#44566a;line-height:1.6;font-size:0.95rem;margin:0 0 10px;}
                      .aim-xfn p:last-child{margin:0;font-weight:700;color:#334b60;}
                      @media(min-width:1024px){
                        .aim-row{grid-template-columns:120px 1fr 56px;gap:14px;align-items:stretch;}
                        .aim-row.wide{grid-template-columns:120px 1fr;}
                        .aim-cards.c5{grid-template-columns:repeat(5,minmax(0,1fr));}
                        .aim-cards.c4{grid-template-columns:repeat(4,minmax(0,1fr));}
                        .aim-rail{display:flex;align-items:center;justify-content:center;}
                      }
                      @media(max-width:520px){.aim-cards{grid-template-columns:1fr;}}
                      .ai-band{position:relative;width:100vw;margin-left:calc(50% - 50vw);overflow:hidden;margin-top:2.5rem;}
                      .ai-hl__pad{position:relative;max-width:1400px;margin:0 auto;padding:3rem 1.5rem;}
                      @media(min-width:768px){.ai-hl__pad{padding:4.5rem 3rem;}}
                      .ai-hl__grid{display:grid;grid-template-columns:1fr;gap:1.6rem;}
                      @media(min-width:640px){.ai-hl__grid{grid-template-columns:repeat(3,1fr);}}
                      .ai-hl__item{display:flex;gap:1rem;align-items:center;}
                      .ai-hl__item i{color:#f19a51;font-size:3rem;line-height:1;flex:0 0 auto;}
                      .ai-hl__item p{color:#FAFAF7;line-height:1.5;font-size:1.05rem;margin:0;}
                      .ai-hl__item strong{color:#fff;}
                    </style>

                    <div class="aim">
                        <div class="aim-rule"></div>

                        <div class="aim-row">
                            <div class="aim-lbl">AI Consulting Services</div>
                            <div class="aim-cards c5">
                                <div class="aim-card"><div class="aim-h">AI Awareness and Enablement</div><div class="aim-b">Creative workshops for AI use-case identification and qualification with IT and business.</div></div>
                                <div class="aim-card"><div class="aim-h">AI Empowerment</div><div class="aim-b">Workshops and trainings for AI usage in specific work situations, for example prompting techniques for internal auditors.</div></div>
                                <div class="aim-card"><div class="aim-h">AI Process Efficiency Elevation</div><div class="aim-b">Evaluation of complex processes to find efficiency gains through AI agents and automation, plus the definition of the related concepts.</div></div>
                                <div class="aim-card"><div class="aim-h">AI Team Efficiency Elevation</div><div class="aim-b">Structured evaluation of all core tasks across an organization to identify every AI potential.</div></div>
                                <div class="aim-card"><div class="aim-h">AI Proof of Concepts</div><div class="aim-b">Implementation of PoCs to evaluate impact and to enable qualified decision-making.</div></div>
                            </div>
                            <div class="aim-rail aim-r1"><span>Consulting</span></div>
                        </div>

                        <div class="aim-row">
                            <div class="aim-lbl">AI Products</div>
                            <div class="aim-cards c4">
                                <div class="aim-card"><div class="aim-h">AI Contract Analyzer</div><div class="aim-b">AI-based agent for mass contract analysis that identifies improvement potential in existing contracts. Relevant for M&amp;A, audits, vendor consolidations, and cost-saving initiatives.</div></div>
                                <div class="aim-card"><div class="aim-h">AI Tender Manager</div><div class="aim-b">AI-based review, evaluation, and rating of incoming supplier offers, with identification of the required improvements and next steps with suppliers.</div></div>
                                <div class="aim-card"><div class="aim-h">AI Contract2Invoice Inspector</div><div class="aim-b">AI-based agent that checks incoming invoices against the price units and contract terms held in the underlying contracts.</div></div>
                                <div class="aim-card"><div class="aim-h">Vendor and Contract Managed Services</div><div class="aim-b">Manage, improve, and renegotiate selected contract bundles, combining subject-matter experts with Aventario's AI products to run contracts efficiently.</div></div>
                            </div>
                            <a class="aim-rail aim-r2" href="https://managedsuppliers.com" target="_blank" rel="noopener"><span>managedsuppliers <i class="ph ph-arrow-up-right" style="font-size:13px;"></i></span></a>
                        </div>

                        <div class="aim-row wide">
                            <div class="aim-lbl">Cross-Functional Services</div>
                            <div class="aim-xfn">
                                <h4>A single, integrated service</h4>
                                <p>We perceive ourselves as a full-service provider and support your initiatives from the initial spark through to a finished, ready-to-operate result.</p>
                                <p>We drive sustainable results and successful initiative delivery, by engaging and equipping the whole affected organization and its stakeholders throughout all phases.</p>
                                <p>All our projects are staffed in line with our core principles to apply relevant methodologies and expertise in transformation implementation, program / project management and change and communication.</p>
                                <p>We provide our clients with a single, integrated service.</p>
                            </div>
                        </div>
                    </div>

                    <div class="ai-band">
                        <img src="images/photography/team-ridge-sunrise.jpg" alt="" role="presentation" class="absolute inset-0 w-full h-full object-cover" style="object-position:center 40%;" loading="lazy" decoding="async">
                        <div class="absolute inset-0" style="background:linear-gradient(90deg, rgba(13,19,30,0.94) 0%, rgba(13,19,30,0.78) 55%, rgba(13,19,30,0.50) 100%);"></div>
                        <div class="ai-hl__pad">
                            <h3 class="font-serif text-3xl md:text-4xl mb-10" style="color:#FAFAF7;">How we deliver</h3>
                            <div class="ai-hl__grid">
                                <div class="ai-hl__item"><i class="ph ph-users-three"></i><p><strong>Experienced consultants</strong> manage the engagement.</p></div>
                                <div class="ai-hl__item"><i class="ph ph-magnifying-glass"></i><p><strong>Subject matter experts</strong> perform the analysis and evaluation.</p></div>
                                <div class="ai-hl__item"><i class="ph ph-cpu"></i><p>Delivery is <strong>enabled by advanced AI technology</strong>.</p></div>
                            </div>
                        </div>
                    </div>

                </div>'''

t2 = t[:start] + new + t[end:]
print('old block chars:', len(old), '| new block chars:', len(new))
print('div balance in new:', new.count('<div') - new.count('</div'), '(want 0)')
if APPLY:
    open(p, 'w', encoding='utf-8', newline='').write(t2)
    print('APPLIED')
else:
    print('DRY-RUN')
