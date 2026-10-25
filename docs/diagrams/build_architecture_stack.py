"""Portrait architecture animation inspired by the supplied layered stack reference.
Uses existing render/encode machinery without changing the earlier artwork.
"""
from pathlib import Path
from html import escape
import argparse,base64,json,subprocess,time,hashlib,struct
import xml.etree.ElementTree as ET
import build_architecture_animation as original
import assemble_architecture_gif as encoder
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
WORK=ROOT/'runtime/architecture-stack';WORK.mkdir(parents=True,exist_ok=True)
STEM='integration-hub-architecture-stack';W,H=1600,2100
TEAL='#60e2c3';PURPLE='#b59aff';BLUE='#78b7ff';GOLD='#edc66e';PINK='#e394d1';INK='#edf3f8';MUTED='#a0b2c2';parts=[]
def add(value):parts.append(value)
def text(x,y,value,size=25,color=INK,weight=500,anchor='start',spacing=0):
 add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}">{escape(value)}</text>')
def icon(kind,x,y,color,scale=1):
 start=len(original.parts);original.icon({'chip':'model','tools':'tool','database':'data'}.get(kind,kind),0,0,color);block=''.join(original.parts[start:]);del original.parts[start:]
 add(f'<g transform="translate({x},{y}) scale({scale})">{block}</g>')
def route(path,color=TEAL,phase=0,arrow=False):
 add(f'<path d="{path}" fill="none" stroke="#677d8e" stroke-width="1.6" stroke-opacity=".6" stroke-dasharray="3 6"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 add(f'<circle r="5" fill="{color}" filter="url(#glow)"><animateMotion dur="8s" repeatCount="indefinite" begin="-{phase}s" path="{path}"/></circle>')
def group(x,y,w,title,color,kind):
 tw=min(w-30,len(title)*15+82);left=x+(w-tw)/2
 add(f'<rect x="{left}" y="{y}" width="{tw}" height="48" rx="13" fill="#111c25" stroke="{color}" stroke-opacity=".65"/>')
 add(f'<rect x="{left}" y="{y}" width="{tw}" height="48" rx="13" fill="none" stroke="{color}" filter="url(#glow)" opacity=".2"><animate attributeName="opacity" values=".12;.3;.12" dur="4s" repeatCount="indefinite"/></rect>')
 icon(kind,left+15,y+10,color,.85);text(left+52,y+32,title,22,color,650,spacing=.7)
 add(f'<path d="M{x+w/2} {y+48}v18" stroke="{color}" stroke-opacity=".5"/>')
def card(x,y,w,h,color,tag='LOCAL / ACTIVE'):
 add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#panel)" stroke="{color}" stroke-opacity=".42"/>')
 add(f'<path d="M{x+14} {y}h{w-28}q14 0 14 14v25H{x}v-25q0-14 14-14" fill="{color}" opacity=".08"/>')
 add(f'<path d="M{x} {y+39}h{w}" stroke="{color}" stroke-opacity=".25"/>')
 text(x+22,y+26,tag,14,color,650,spacing=1.8)
def generate():
 parts.clear();add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title description"><title id="title">Integration Hub architecture</title><desc id="description">Actual local architecture, from incident logs through verified findings and human-approved recovery. Optional extensions are separated. Animation illustrates flow, not live traffic.</desc>')
 add('''<defs><pattern id="dots" width="25" height="25" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".8" fill="#496171" opacity=".28"/></pattern><linearGradient id="panel" x2="0" y2="1"><stop stop-color="#121d27"/><stop offset="1" stop-color="#0d151d"/></linearGradient><radialGradient id="ambient"><stop stop-color="#143831" stop-opacity=".38"/><stop offset="1" stop-color="#090f15" stop-opacity="0"/></radialGradient><filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1l7 4-7 4" fill="none" stroke="#7b97a7" stroke-width="1.5"/></marker></defs>''')
 add('<rect width="1600" height="2100" fill="#090f15"/><rect width="1600" height="2100" fill="url(#dots)"/><ellipse cx="800" cy="300" rx="800" ry="580" fill="url(#ambient)"/>')
 add('<g font-family="Segoe UI, Arial, sans-serif">')
 text(800,90,'Integration Hub',68,INK,750,'middle',-1.8)
 text(800,140,'The architecture behind evidence-backed incident recovery',27,MUTED,500,'middle')
 text(800,179,'LOCAL-FIRST AI  /  VERIFIED EVIDENCE  /  HUMAN CONTROL',17,TEAL,650,'middle',2)
 add('<rect x="590" y="211" width="420" height="51" rx="25" fill="#121e28" stroke="#506574"/>');icon('screen',610,222,BLUE,.8);text(816,244,'Engineer submits incident logs',22,INK,550,'middle')
 # Top request and frontend -> API path.
 route('M800 262V280H425V300',TEAL,0,True)
 route('M750 455H850',TEAL,1,True)
 group(100,300,650,'FRONTEND & UI',TEAL,'screen');group(850,300,650,'API & GUARDRAILS',BLUE,'shield')
 card(100,366,650,220,TEAL);card(850,366,650,220,BLUE)
 icon('screen',124,425,TEAL,1.1);text(170,450,'React + TypeScript',33,INK,650)
 text(124,492,'Vite · 11 views · dark / light themes',26,MUTED)
 text(124,531,'Accessible review and approval dialogs',24,MUTED)
 text(124,565,'Visible-tab polling · connection recovery',23,TEAL)
 icon('shield',874,425,BLUE,1.1);text(920,450,'FastAPI + Python',33,INK,650)
 text(874,492,'Token access · Pydantic validation',26,MUTED)
 text(874,531,'Input screening · secret redaction',24,MUTED)
 text(874,565,'Step / token budgets · one active run',23,BLUE)
 route('M1175 586V617H800V642',PURPLE,2,True)
 group(100,642,1400,'AGENT ORCHESTRATION',PURPLE,'graph');card(100,708,1400,239,PURPLE,'LANGGRAPH / DURABLE STATE + BOUNDED REFLECTION')
 nodes=[('Triage','Parse signals'),('Planner','Select a tool'),('Tools','Retrieve sources'),('Analyst','Build hypothesis'),('Verify','Check quotations')]
 for i,(label,sub) in enumerate(nodes):
  x=125+i*277
  add(f'<rect x="{x}" y="774" width="241" height="79" rx="11" fill="#172130" stroke="{PURPLE}" stroke-opacity=".42"/>')
  text(x+120,806,label,26,INK,650,'middle');text(x+120,835,sub,19,MUTED,400,'middle')
  if i<4:route(f'M{x+241} 813h36',PURPLE,i,True)
 route('M1354 853V873H1077V855',PURPLE,3,True);text(1220,901,'Repair evidence · up to 2 retries',18,PURPLE,500,'middle')
 text(125,890,'Missing or unsafe evidence → human handoff',20,GOLD)
 text(125,924,'Valid finding → human approval → local ticket + reviewed memory',23,TEAL,600)
 # Service bus: supporting layers, not serial execution stages.
 route('M800 947V980H320V1003',TEAL,1);route('M800 980V1003',BLUE,2);route('M800 980H1280V1003',GOLD,3)
 for x,w,title,col,kind in [(100,440,'KNOWLEDGE / RAG',TEAL,'book'),(580,440,'MODELS / INFERENCE',BLUE,'chip'),(1060,440,'READ-ONLY TOOLS',GOLD,'tools')]:
  group(x,1003,w,title,col,kind);card(x,1069,w,255,col)
 text(124,1143,'Chroma',31,INK,650);text(124,1183,'Runbooks + source passages',23,MUTED);text(124,1218,'Sentence-aware chunks',23,MUTED);text(124,1253,'Nomic query / doc prefixes',23,MUTED);text(124,1300,'Top-3 retrieval · cited quotes',23,TEAL)
 text(604,1143,'Ollama',31,INK,650);text(604,1183,'Qwen2.5 · planner + analyst',23,MUTED);text(604,1218,'nomic-embed-text · vectors',23,MUTED);text(604,1261,'OPTIONAL / OFF BY DEFAULT',14,GOLD,650,spacing=1);text(604,1300,'OpenRouter / Nebius',24,GOLD)
 text(1084,1143,'Allowlisted actions',29,INK,650);text(1084,1183,'search_runbooks',25,MUTED);text(1084,1218,'search_memory',25,MUTED);text(1084,1253,'request_human',25,MUTED);text(1084,1300,'No shell execution',23,GOLD)
 route('M320 1324V1350H425V1374',PINK,4);route('M800 1324V1350H1175V1374',BLUE,5);route('M1280 1324V1350H1175',GOLD,6)
 group(100,1374,650,'DATA & REVIEWED MEMORY',PURPLE,'database');group(850,1374,650,'OBSERVABILITY & EVALS',PINK,'pulse')
 card(100,1440,650,207,PURPLE);card(850,1440,650,207,PINK)
 text(124,1514,'SQLite + WAL',31,INK,650);text(124,1555,'Documents · runs · tickets · graph checkpoints',24,MUTED);text(124,1592,'Reviewed hypotheses retained after approval',24,MUTED);text(124,1627,'Canonical records local · vectors rebuildable',23,PURPLE)
 text(874,1514,'Trace, measure, verify',31,INK,650);text(874,1555,'Tokens · latency · stages · analysis attempts',24,MUTED);text(874,1592,'Saved benchmarks → diagnostics dashboard',24,MUTED);text(874,1627,'API readiness + operational measurements',23,PINK)
 route('M425 1647V1673H425V1700',TEAL,1);route('M1175 1647V1673H425',PINK,3)
 group(100,1700,650,'DEPLOYMENT',TEAL,'deploy');group(850,1700,650,'OPTIONAL EXTENSIONS',GOLD,'cloud')
 card(100,1766,650,195,TEAL,'NATIVE LOCAL STACK');card(850,1766,650,195,GOLD,'DISABLED BY DEFAULT / EXPLICIT CONSENT')
 text(124,1836,'UI :5180 → API :8010',29,INK,650);text(124,1875,'Chroma :8082 · Ollama :11434',24,MUTED);text(124,1911,'Docker Compose / Nginx prepared',23,MUTED);text(124,1943,'Container runtime remains unverified',20,TEAL)
 text(874,1836,'Pinecone · Mem0 · Langfuse',28,INK,650);text(874,1875,'Keenable search · ElevenLabs voice',24,MUTED);text(874,1911,'Credentials + consent + budget gates',23,MUTED);text(874,1943,'Cloud operation not verified in local mode',20,GOLD)
 add('<rect x="100" y="1990" width="1400" height="58" rx="14" fill="#111c24" stroke="#334b53"/>');text(800,2027,'Cited hypothesis → human decision → local recovery ticket',27,INK,650,'middle')
 text(100,2082,'INTEGRATION HUB  /  SYSTEM ARCHITECTURE',15,MUTED,600,spacing=1.4)
 text(1500,2082,'Illustrative flow · no automatic production remediation',17,MUTED,400,'end')
 add('</g></svg>');svg='\n'.join(parts);ET.fromstring(svg)
 (OUT/(STEM+'.svg')).write_text(svg,encoding='utf-8')
 (OUT/(STEM+'.html')).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Integration Hub — Architecture Stack</title><style>body{margin:0;background:#090f15}svg{display:block;width:100%;height:auto}</style>'+svg+'</html>',encoding='utf-8')

def render(frames=100):
 # Reuse the tested CDP renderer with isolated output paths and portrait dimensions.
 source=(OUT/'build_architecture_animation.py').read_text(encoding='utf-8-sig')
 source=source[source.index('def render(frames=100):'):source.index("if __name__=='__main__':")]
 source=source.replace('9239','9241').replace('b.x<60||b.x+b.width>2340','b.x<70||b.x+b.width>1530').replace("'width':1800,'height':1200","'width':1600,'height':2100").replace('Rendered 2400 x 1600 PNG','Rendered 1600 x 2100 PNG')
 scope=globals().copy();exec(source,scope);scope['render'](frames)

def encode():
 # A separate copy keeps the earlier encoder and artwork byte-for-byte intact.
 ps=(OUT/'encode_architecture_frames.ps1').read_text(encoding='utf-8-sig').replace("$PSScriptRoot '../../runtime/architecture-animation'","$PSScriptRoot '.'")
 encoder_file=WORK/'encode_frames.ps1';encoder_file.write_text(ps,encoding='utf-8-sig')
 command=['powershell.exe','-NoProfile','-File',str(encoder_file)]
 subprocess.run(command+['-Mode','sample'],check=True)
 encoder.WORK=WORK;encoder.palette()
 subprocess.run(command+['-Mode','encode'],check=True)
 frames=[list(map(int,row.split(','))) for row in (WORK/'frames.csv').read_text().splitlines()]
 result=bytearray(b'GIF89a'+struct.pack('<HHBBB',W,H,0x70,0,0));result.extend(b'\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00')
 for i,x,y,w,h in frames:
  table,interlace,lzw=encoder.read_frame(WORK/f'encoded-{i:03}.gif');size=(len(table)//3).bit_length()-2
  result.extend(b'\x21\xf9\x04'+struct.pack('<BHB',5,8,0)+b'\x00');result.extend(b'\x2c'+struct.pack('<HHHHB',x,y,w,h,128|interlace|size)+table+lzw)
 result.append(0x3b);(OUT/(STEM+'.gif')).write_bytes(result);print(f'GIF exported: {len(frames)} frames / 8 seconds / {len(result)/1048576:.2f} MB',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--poster-only',action='store_true');args=p.parse_args()
 old={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in OUT.glob('integration-hub-architecture-animated.*')}
 generate();render(0 if args.poster_only else 100)
 if not args.poster_only:encode()
 assert all(hashlib.sha256((OUT/name).read_bytes()).hexdigest()==value for name,value in old.items())
 print('Original architecture assets unchanged.',flush=True)
