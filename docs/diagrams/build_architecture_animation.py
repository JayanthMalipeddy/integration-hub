"""Editable animated architecture. Uses existing Edge and Windows graphics; no downloads."""
from pathlib import Path
from html import escape
import argparse, base64, json, subprocess, time
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
WORK=ROOT/'runtime/architecture-animation'
STEM='integration-hub-architecture-animated'
W,H=2400,1600
TEAL,BLUE,PURPLE,AMBER='#47e4c2','#78bcff','#b39aff','#ffc879'
INK,MUTED,DIM='#edf5ff','#a8bad1','#7186a3'
parts=[]
def add(s):parts.append(s)
def text(x,y,value,size=25,fill=INK,weight=400,anchor='start',spacing=0):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}">{escape(value)}</text>')
def icon(kind,x,y,color):
    symbols={
      'screen':'<rect x="1" y="2" width="26" height="18" rx="3"/><path d="M9 26h10M14 20v6M7 8h7M7 13h14"/>',
      'shield':'<path d="M14 1l11 4v9c0 7-11 13-11 13S3 21 3 14V5zM8 13l4 4 8-8"/>',
      'graph':'<circle cx="5" cy="5" r="4"/><circle cx="24" cy="14" r="4"/><circle cx="5" cy="25" r="4"/><path d="M9 5h5v9h6M5 9v12M9 25h5V14"/>',
      'book':'<path d="M14 5C9 1 4 2 1 4v22c4-3 8-3 13 0 5-3 9-3 13 0V4c-3-2-8-3-13 1v21"/>',
      'model':'<rect x="5" y="5" width="19" height="19" rx="5"/><path d="M10 1v4M19 1v4M10 24v4M19 24v4M1 10h4M1 19h4M24 10h4M24 19h4M11 19v-9l7 9v-9"/>',
      'tool':'<path d="M4 3l8 8-3 3-8-8M10 16L2 24l3 3 8-8M17 12l9-9c3 7-1 13-8 13L9 25"/>',
      'data':'<ellipse cx="14" cy="5" rx="12" ry="4"/><path d="M2 5v18c0 5 24 5 24 0V5M2 14c0 5 24 5 24 0"/>',
      'pulse':'<path d="M0 16h6l4-12 7 23 5-14h7"/>',
      'cloud':'<path d="M6 23a7 7 0 01-2-14 10 10 0 0119 1 7 7 0 013 13z"/>',
      'deploy':'<rect x="1" y="2" width="27" height="10" rx="3"/><rect x="1" y="17" width="27" height="10" rx="3"/><path d="M6 7h1M6 22h1M12 7h11M12 22h11"/>'}
    add(f'<g transform="translate({x} {y}) scale(1.15)" stroke="{color}" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{symbols[kind]}</g>')
def panel(x,y,w,h,color,eyebrow,title,kind,title_size=34,pulse=False):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="url(#card)" stroke="{color}" stroke-opacity=".32" stroke-width="1.5"/>')
    if pulse:add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="none" stroke="{color}" stroke-width="2" filter="url(#glow)"><animate attributeName="opacity" values=".08;.45;.08" dur="8s" begin="-2s" repeatCount="indefinite"/></rect>')
    icon(kind,x+25,y+27,color);text(x+73,y+51,eyebrow,18,color,600,spacing=2);text(x+26,y+99,title,title_size,INK,600)
def pill(x,y,w,label,color=TEAL,size=22):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="52" rx="13" fill="{color}" fill-opacity=".07" stroke="{color}" stroke-opacity=".23"/>');text(x+w/2,y+34,label,size,color,500,'middle')
def route(d,color=TEAL,packet=True,dashed=False,dur=4,phase=0,arrow=True):
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity=".42" stroke-width="2"'+(' stroke-dasharray="6 7"' if dashed else '')+(f' marker-end="url(#{"amber" if color==AMBER else "arrow"})"' if arrow else '')+'/>')
    if packet:add(f'<circle r="5" fill="{color}" filter="url(#glow)"><animateMotion path="{d}" dur="{dur}s" begin="{-phase}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.90;1" dur="{dur}s" begin="{-phase}s" repeatCount="indefinite"/></circle>')
def generate_svg():
    parts.clear()
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
    add('<title id="title">Integration Hub — animated system architecture</title><desc id="desc">React and FastAPI lead to LangGraph investigation, retrieval, verification, bounded reflection, human approval and local ticket creation. Services: Chroma, Ollama Qwen2.5, nomic embeddings, SQLite, reviewed memory and traces. Cloud integrations are optional and disabled. Native deployment is local; Docker runtime remains unverified.</desc>')
    add('''<defs>
    <radialGradient id="ambient"><stop stop-color="#123c49" stop-opacity=".6"/><stop offset="1" stop-color="#080e1b" stop-opacity="0"/></radialGradient>
    <radialGradient id="ambient2"><stop stop-color="#2a2259" stop-opacity=".45"/><stop offset="1" stop-color="#080e1b" stop-opacity="0"/></radialGradient>
    <linearGradient id="card" x2=".6" y2="1"><stop stop-color="#121e31"/><stop offset="1" stop-color="#0d1728"/></linearGradient>
    <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#6c8caa" opacity=".12"/></pattern>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L8 5L1 9" fill="none" stroke="#47e4c2" stroke-width="1.3"/></marker>
    <marker id="amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L8 5L1 9" fill="none" stroke="#ffc879" stroke-width="1.3"/></marker>
    <style>text{font-family:'Segoe UI',Arial,sans-serif}.mono{font-family:Consolas,monospace}</style></defs>''')
    add('<rect width="2400" height="1600" fill="#080e1b"/><ellipse cx="2070" cy="100" rx="1000" ry="750" fill="url(#ambient)"/><ellipse cx="760" cy="1030" rx="1100" ry="850" fill="url(#ambient2)"/><rect width="2400" height="1600" fill="url(#grid)"/>')
    text(82,83,'SYSTEM ARCHITECTURE  /  LOCAL-FIRST AI',19,TEAL,600,spacing=3)
    text(78,172,'Integration Hub',86,INK,650,spacing=-2)
    text(82,222,'From incident logs to an evidence-backed recovery plan.',31,MUTED)
    pill(1805,103,515,'ACTIVE PROFILE  /  LOCAL_FREE',TEAL,23)
    text(2320,196,'Read-only investigation. Human-approved action.',23,MUTED,anchor='end')
    add('<path d="M80 254H2320" stroke="#24354d"/>')
    for i,label in enumerate(['Submit logs','Authenticate','Retrieve evidence','Analyze + verify','Review + approve','Ticket + memory']):
        x=80+i*379;add(f'<rect x="{x}" y="285" width="345" height="74" rx="17" fill="#101b2c" stroke="#294055"/>')
        text(x+23,331,f'{i+1:02}',23,TEAL if i<4 else AMBER,600);text(x+68,332,label,25,INK,500)
        if i<5:route(f'M{x+349} 322H{x+370}',packet=False)
    panel(80,410,470,425,BLUE,'USER WORKSPACE','React + TypeScript','screen',pulse=True)
    text(106,554,'Vite frontend · port 5180',25,BLUE)
    for y,t in [(610,'11 connected workspace views'),(652,'Access token in tab memory'),(694,'Run-state polling every 5 s')]:text(106,y,t,25,MUTED)
    pill(106,749,418,'Engineer → incident + logs',BLUE,23)
    panel(600,410,500,425,TEAL,'API & SECURITY BOUNDARY','FastAPI / Python','shield',pulse=True)
    text(626,554,'Pydantic validation · port 8010',25,TEAL)
    for y,t in [(610,'Authentication + input limits'),(652,'Redaction + injection checks'),(694,'Token budget + one active run')]:text(626,y,t,25,MUTED)
    pill(626,749,448,'Background task → run ID',TEAL,23)
    route('M550 620H600',BLUE);route('M1100 620H1150',phase=1)
    panel(1150,410,1170,425,PURPLE,'AGENT ORCHESTRATION','LangGraph','graph',pulse=True)
    text(1436,509,'Durable state · bounded reflection · approval gate',25,MUTED)
    for i,(label,detail,color) in enumerate([('Triage','Parse signals',TEAL),('Planner','Select a tool',PURPLE),('Tools','Retrieve evidence',BLUE),('Analyst','Qwen hypothesis',PURPLE),('Verify','Quotes + sources',TEAL)]):
        x=1182+i*224
        add(f'<rect x="{x}" y="550" width="205" height="86" rx="15" fill="#142239" stroke="{color}" stroke-opacity=".45"/>')
        add(f'<rect x="{x}" y="550" width="205" height="86" rx="15" fill="none" stroke="{color}" stroke-width="2" filter="url(#glow)"><animate attributeName="opacity" values=".08;.6;.08" dur="4s" begin="{-i*.5}s" repeatCount="indefinite"/></rect>')
        text(x+102.5,584,label,25,INK,600,'middle');text(x+102.5,615,detail,19,MUTED,anchor='middle')
        if i<4:route(f'M{x+207} 592H{x+221}',color,phase=i*.5)
    route('M2180 636V662H1956V637',PURPLE,phase=2)
    text(2030,691,'Repair evidence · max 2 retries',19,PURPLE,500,'middle')
    route('M1285 636V704H1352V738',AMBER,dashed=True,dur=8)
    route('M1508 636V704H1352',AMBER,packet=False,dashed=True,arrow=False)
    route('M2284 593H2303V716H1719V738',phase=2)
    text(1520,733,'Valid evidence',17,TEAL,500)
    for x,w,c,title,detail in [(1182,340,AMBER,'Human handoff','Unsafe / missing / unsupported'),(1554,330,AMBER,'Human approval','Durable pause · approve / decline'),(1916,372,TEAL,'Local ticket + memory','Plan + reviewed hypothesis')]:
        add(f'<rect x="{x}" y="747" width="{w}" height="67" rx="14" fill="{c}" fill-opacity=".07" stroke="{c}" stroke-opacity=".5"/>')
        text(x+w/2,775,title,24,c,600,'middle');text(x+w/2,801,detail,18,MUTED,anchor='middle')
    route('M1884 780H1916',phase=2.5)
    route('M1735 836V868',PURPLE,phase=2,arrow=False)
    add('<path d="M80 880H2320" fill="none" stroke="#2b435b" stroke-width="1.5"/>');text(80,918,'WORKFLOW SERVICES',18,DIM,600,spacing=2.5)
    for center,c in [(330,BLUE),(810,PURPLE),(1260,TEAL),(1720,BLUE),(2140,PURPLE)]:
        route(f'M{center} 880V940',c,phase=center/1000,arrow=False);add(f'<circle cx="{center}" cy="880" r="4" fill="{c}"/>')
    panel(80,940,500,340,BLUE,'RAG / KNOWLEDGE','Chroma + runbooks','book',32)
    for y,t in [(1080,'TXT / MD / JSON imports'),(1120,'Sentence-aware chunks'),(1160,'Nomic document/query prefixes'),(1200,'Top-3 vector evidence'),(1240,'Canonical source validation')]:text(106,y,t,24,MUTED)
    panel(610,940,400,340,PURPLE,'LOCAL MODEL LAYER','Ollama','model',34)
    text(636,1082,'Qwen2.5',27,INK,500);text(636,1118,'Planner + analyst',23,MUTED);text(636,1173,'nomic-embed-text',26,INK,500);text(636,1209,'Local embeddings',23,MUTED);text(636,1251,'No API charge in local mode',21,PURPLE)
    panel(1040,940,440,340,TEAL,'TOOLS / PERMISSIONS','Allowlisted tools','tool',32)
    for y,t in [(1083,'search_runbooks'),(1124,'search_memory'),(1165,'request_human')]:add(f'<text class="mono" x="1066" y="{y}" font-size="25" fill="{MUTED}">{t}</text>')
    add('<path d="M1066 1193H1454" stroke="#294052"/>');text(1066,1232,'Read-only · no shell execution',23,TEAL)
    panel(1510,940,420,340,BLUE,'DATA + MEMORY','SQLite + WAL','data',32)
    for y,t in [(1080,'Documents · runs · tickets'),(1120,'Durable graph checkpoints'),(1160,'Reviewed hypothesis memory'),(1200,'Canonical data stays local')]:text(1536,y,t,23,MUTED)
    text(1536,1245,'Vector indexes are rebuildable',21,BLUE)
    panel(1960,940,360,340,PURPLE,'OBSERVABILITY','Trace + measure','pulse',29)
    for y,t in [(1080,'Tokens · latency · attempts'),(1120,'/api/ready'),(1160,'/api/operations'),(1200,'Saved evals → dashboard'),(1240,'Local trace records')]:text(1986,y,t,22,MUTED)
    add('<rect x="80" y="1340" width="1370" height="180" rx="22" fill="#0d1526" stroke="#665482" stroke-opacity=".65" stroke-dasharray="7 7"/>');icon('cloud',106,1365,PURPLE)
    text(154,1390,'OPTIONAL CLOUD ADAPTERS  /  DISABLED BY DEFAULT',19,PURPLE,600,spacing=1.7)
    text(106,1435,'OpenRouter · Nebius · Pinecone · Mem0 · Langfuse',27,INK,500)
    text(106,1471,'Keenable search · ElevenLabs voice · explicit memory / trace exports',23,MUTED)
    text(106,1504,'Consent + credentials + budget required; live cloud operation unverified.',21,DIM)
    add('<rect x="1480" y="1340" width="840" height="180" rx="22" fill="#0e1927" stroke="#294455"/>');icon('deploy',1506,1365,TEAL)
    text(1554,1390,'LOCAL DEPLOYMENT',19,TEAL,600,spacing=2)
    text(1506,1435,'UI :5180 → API :8010 · Chroma :8082',27,INK,500)
    text(1506,1471,'Single process · one active investigation',23,MUTED)
    text(1506,1504,'Docker Compose / Nginx prepared; runtime unverified.',20,DIM)
    text(80,1571,'Cited hypothesis → human decision → local recovery plan',24,INK,500)
    text(2320,1571,'Illustrative motion · no automatic production remediation',20,DIM,anchor='end')
    add('</svg>');result='\n'.join(parts);ET.fromstring(result)
    (OUT/(STEM+'.svg')).write_text(result,encoding='utf-8')
    (OUT/(STEM+'.html')).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Integration Hub — Architecture</title><style>html,body{margin:0;background:#080e1b}svg{display:block;width:100%;height:auto}</style>'+result+'</html>',encoding='utf-8')
    print('Created editable SVG and offline animated HTML.',flush=True)
def render(frames=100):
    import httpx
    from websockets.sync.client import connect
    WORK.mkdir(parents=True,exist_ok=True)
    subprocess.Popen([r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe','--headless=new','--disable-gpu','--no-first-run','--inprivate','--disable-sync','--disable-features=msImplicitSignin','--disable-background-networking','--remote-debugging-port=9239','--remote-debugging-address=127.0.0.1','--user-data-dir='+str(WORK/'browser'),'about:blank'],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    client=httpx.Client(timeout=10,trust_env=False)
    for _ in range(40):
        try:page=next(p for p in client.get('http://127.0.0.1:9239/json/list').json() if p['type']=='page');break
        except Exception:time.sleep(.3)
    else:raise RuntimeError('Browser did not start')
    with connect(page['webSocketDebuggerUrl'],open_timeout=10,max_size=16777216) as ws:
        sequence=0
        def command(method,params=None):
            nonlocal sequence
            sequence+=1;seq=sequence;ws.send(json.dumps({'id':seq,'method':method,'params':params or {}}))
            while True:
                r=json.loads(ws.recv(timeout=30))
                if r.get('id')==seq:
                    if 'error' in r:raise RuntimeError(r['error'])
                    return r.get('result',{})
        def js(expression):
            r=command('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
            if r.get('exceptionDetails'):raise RuntimeError(r['exceptionDetails'])
            return r['result'].get('value')
        try:
            command('Page.enable');command('Runtime.enable');command('Emulation.setDeviceMetricsOverride',{'width':W,'height':H,'deviceScaleFactor':1,'mobile':False})
            command('Page.navigate',{'url':(OUT/(STEM+'.html')).as_uri()})
            for _ in range(40):
                if js("!!document.querySelector('svg')"):break
                time.sleep(.2)
            js("document.fonts.ready.then(()=>{document.querySelector('svg').pauseAnimations();document.querySelector('svg').setCurrentTime(3.36)})")
            overflow=js("Array.from(document.querySelectorAll('text')).filter(e=>{const b=e.getBBox();return b.x<60||b.x+b.width>2340}).map(e=>e.textContent)")
            if overflow:raise AssertionError(overflow)
            (OUT/(STEM+'.png')).write_bytes(base64.b64decode(command('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
            print('Rendered 2400 x 1600 PNG; text fits the canvas.',flush=True)
            if not frames:return
            command('Emulation.setDeviceMetricsOverride',{'width':1800,'height':1200,'deviceScaleFactor':1,'mobile':False})
            for i in range(frames):
                js(f"document.querySelector('svg').setCurrentTime({8*i/frames})")
                (WORK/f'frame-{i:03}.png').write_bytes(base64.b64decode(command('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
                if i%20==0:print(f'Rendered animation frame {i+1}/{frames}',flush=True)
        finally:
            try:command('Browser.close')
            except Exception:pass
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--poster-only',action='store_true');parser.add_argument('--svg-only',action='store_true');args=parser.parse_args();generate_svg()
    if not args.svg_only:render(0 if args.poster_only else 100)

