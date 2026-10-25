"""Read-only browser checks using installed Edge. No approvals or API writes."""
from pathlib import Path
import json,time,subprocess,base64,sys
import httpx
from websockets.sync.client import connect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app.config import Settings
OUT=ROOT/'runtime'/'ui-verification';OUT.mkdir(parents=True,exist_ok=True)
subprocess.Popen([r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe','--headless=new','--disable-gpu','--no-first-run','--inprivate','--disable-sync','--disable-background-networking','--remote-debugging-port=9240','--remote-debugging-address=127.0.0.1','--user-data-dir='+str(OUT/'browser'),'about:blank'],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
client=httpx.Client(timeout=10,trust_env=False)
for _ in range(40):
 try:page=next(p for p in client.get('http://127.0.0.1:9240/json/list').json() if p['type']=='page');break
 except Exception:time.sleep(.25)
else:raise RuntimeError('Browser not available')
checks=[];errors=[]
with connect(page['webSocketDebuggerUrl'],max_size=16777216) as ws:
 seq=0
 def command(method,params=None):
  global seq
  seq+=1;current=seq;ws.send(json.dumps({'id':current,'method':method,'params':params or {}}))
  while True:
   r=json.loads(ws.recv(timeout=30))
   if r.get('method')=='Runtime.exceptionThrown':errors.append('Browser JavaScript exception')
   if r.get('id')==current:
    if 'error' in r:raise RuntimeError(r['error'])
    return r.get('result',{})
 def js(expr):
  r=command('Runtime.evaluate',{'expression':expr,'returnByValue':True,'awaitPromise':True})
  if r.get('exceptionDetails'):raise RuntimeError('Browser expression failed: '+expr[:120])
  return r.get('result',{}).get('value')
 def until(expr):
  for _ in range(75):
   if js(expr):return
   time.sleep(.2)
  raise AssertionError('Timed out: '+expr)
 def click(label,selector='button'):
  assert js('(()=>{const el=Array.from(document.querySelectorAll('+json.dumps(selector)+')).find(b=>b.textContent.trim().startsWith('+json.dumps(label)+'));if(!el)return false;el.focus();el.click();return true})()'),label
 def shot(name):
  (OUT/(name+'.png')).write_bytes(base64.b64decode(command('Page.captureScreenshot',{'format':'png'})['data']))
 def viewport(w,h):command('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
 def input_value(selector,value):
  js('(()=>{const el=document.querySelector('+json.dumps(selector)+');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set.call(el,'+json.dumps(value)+');el.dispatchEvent(new Event("input",{bubbles:true}));})()')
 def login(value):
  input_value('#access-token',value);js('document.querySelector("form").requestSubmit()')
 def nav(label):
  if js('window.innerWidth<=760 && !document.querySelector(".navigation-open")'):
   js('document.querySelector(".mobile-menu").click()')
  click(label,'nav button');time.sleep(.1)
 def check(name,expr):
  assert js(expr),name;checks.append(name)
 def key(name,shift=False):
  command('Input.dispatchKeyEvent',{'type':'keyDown','key':name,'code':name,'windowsVirtualKeyCode':{'Escape':27,'Tab':9,'Enter':13}[name],'modifiers':8 if shift else 0,'text':'\r' if name=='Enter' else ''})
  command('Input.dispatchKeyEvent',{'type':'keyUp','key':name,'code':name,'windowsVirtualKeyCode':{'Escape':27,'Tab':9,'Enter':13}[name]})
 try:
  command('Runtime.enable');command('Page.enable');command('Network.enable');viewport(1440,1000)
  command('Page.navigate',{'url':'http://127.0.0.1:5180'})
  until('!!document.querySelector("#access-token")');shot('access-desktop')
  login('incorrect-synthetic-credential');until('document.querySelector("[role=alert]")?.textContent.includes("Authentication")')
  check('Invalid token keeps protected navigation hidden','!document.querySelector("nav")')
  login(Settings.from_env().api_token);until('!!document.querySelector("nav")');time.sleep(.3)
  check('Valid token opens authenticated workspace','!!document.querySelector(".connection.connected")')
  check('No credential in browser storage','!Object.keys(localStorage).concat(Object.keys(sessionStorage)).some(k=>/token|auth/i.test(k))')
  labels=js('Array.from(document.querySelectorAll("nav button")).map(b=>b.querySelector("span").textContent)')
  for theme in ['dark','light']:
   nav('Settings');click('Switch to '+theme) if js('document.documentElement.dataset.theme')!=theme else None
   for w,h in [(1440,1000),(768,1024),(390,844)]:
    viewport(w,h)
    for label in labels:
     nav(label)
     assert js('document.documentElement.scrollWidth<=window.innerWidth'),f'Overflow: {theme} {w} {label}'
     assert js('!!document.querySelector("h1")'),label
     checks.append(f'{theme} {w}px: {label} renders without page overflow')
     if label in ['Overview','Analytics & evaluations','Agent workspace','Provider configuration'] and w in [1440,390]:shot(f'{theme}-{w}-{label.split()[0].lower()}')
   print(f'Checked all pages in {theme} theme.',flush=True)
  viewport(1440,1000);nav('Settings');click('Switch to dark') if js('document.documentElement.dataset.theme')!='dark' else None
  nav('Overview')
  input_value('.search-field input','no-such-investigation-qa-947');until('document.querySelector(".empty")?.textContent.includes("No investigations match")')
  check('Search shows explicit no-match state','document.querySelectorAll("tbody tr").length===0')
  input_value('.search-field input','');until('document.querySelectorAll("tbody tr").length>0')
  check('Clearing search restores records','document.querySelectorAll("tbody tr").length>0')
  js('document.querySelector(".status-filter select").value="awaiting_approval";document.querySelector(".status-filter select").dispatchEvent(new Event("change",{bubbles:true}))')
  until('document.querySelectorAll("tbody tr").length>0')
  check('Status filter only includes pending reviews','Array.from(document.querySelectorAll("tbody tr .badge")).every(e=>e.textContent==="awaiting approval")')
  js('document.querySelector(".run-link").focus()');key('Enter');until('Array.from(document.querySelectorAll("button")).some(e=>e.textContent.includes("Review and approve"))')
  checks.append('Keyboard opens investigation from table')
  click('Review and approve');until('!!document.querySelector("dialog[open]")')
  check('Confirmation defaults focus to Cancel','document.activeElement.textContent==="Cancel"')
  for _ in range(6):key('Tab');check('Dialog contains keyboard focus','!!document.activeElement.closest("dialog")')
  shot('approval-dialog');key('Escape');until('!document.querySelector("dialog[open]")')
  check('Escape cancels and restores focus','document.activeElement.textContent.includes("Review and approve")')
  nav('Analytics & evaluations');js('document.querySelector(".case-summary").click()')
  check('Case expansion exposes readable outcome','!!document.querySelector(".evaluation-case[open] .case-facts")')
  nav('Overview');before=js('document.querySelectorAll("tbody tr").length')
  command('Network.emulateNetworkConditions',{'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0})
  js('document.querySelector("header .icon-button").click()');until('!!document.querySelector(".connection.stale")')
  check('Offline keeps previously loaded records',f'document.querySelectorAll("tbody tr").length==={before}')
  shot('offline-state')
  command('Network.emulateNetworkConditions',{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1})
  js('document.querySelector("header .icon-button").click()');until('!!document.querySelector(".connection.connected")');checks.append('Reconnect returns to connected state')
  # Browser-local empty fixture; original API records are unchanged.
  js('window.originalFetch=window.fetch;window.fetch=async (...args)=>{const response=await window.originalFetch(...args);if(args[0]==="/api/dashboard"){const data=await response.json();data.runs=[];data.evaluations=[];data.documents=0;return new Response(JSON.stringify(data),{status:200,headers:{"Content-Type":"application/json"}})}return response}')
  js('document.querySelector("header .icon-button").click()');until('document.querySelector(".empty")?.textContent.includes("first investigation")')
  shot('empty-overview');checks.append('Empty dashboard has explicit guidance without fabricated metrics')
  nav('Analytics & evaluations');check('No benchmark shows explicit empty state','document.querySelector(".empty")?.textContent.includes("No benchmark")')
  js('window.fetch=window.originalFetch');js('document.querySelector("header .icon-button").click()');until('!!document.querySelector(".evaluation-case")')
  # Browser-only workflow fixture: exercise actions without sending a write to the server.
  js('''window.actionFetch=window.fetch;window.fixtureCounts={start:0,approve:0,evidence:0};window.workflowFixture={id:"ui-browser-fixture",status:"awaiting_approval",evidence_revision:1,review_digest:"revision-one",observations:[{source_id:"incident:logs",line_id:"L1",quote:"Synthetic evidence"}],questions:["Provide timestamped observations or state unavailable."],created_at:new Date().toISOString(),incident:{title:"Synthetic UI verification",service:"browser-only",logs:"Synthetic evidence"},finding:{hypothesis:"Synthetic browser fixture; no production incident.",confidence:"low",uncertainty:"Browser interaction test only.",checks:["Review fixture"],recovery:["Create fixture ticket"],citations:[]},validation:{citations:[],scope:"Browser-only fixture"},evidence:[],traces:[]};window.fetch=async(url,init={})=>{if(init.method&&init.method!=="GET"){if(url==="/api/runs"){window.fixtureCounts.start++;return Response.json(window.workflowFixture)}if(url==="/api/runs/ui-browser-fixture/evidence"){window.fixtureCounts.evidence++;window.lastEvidence=JSON.parse(init.body);await new Promise(r=>setTimeout(r,500));window.workflowFixture.evidence_revision=2;window.workflowFixture.review_digest="revision-two";return Response.json({evidence_revision:2,status:"running"})}if(url==="/api/runs/ui-browser-fixture/approval"){window.fixtureCounts.approve++;window.lastApproval=JSON.parse(init.body);await new Promise(r=>setTimeout(r,500));window.workflowFixture.status="completed";return Response.json({ok:true})}throw new Error("Blocked real mutation during UI verification")}if(url==="/api/runs/ui-browser-fixture")return Response.json(window.workflowFixture);const response=await window.actionFetch(url,init);if(url==="/api/dashboard"){const d=await response.json();d.runs=[window.workflowFixture,...d.runs];return Response.json(d)}return response}''')
  nav('Agent workspace');js('document.querySelector(".sample-row").click()');until('!document.querySelector("button[type=submit]").disabled')
  js('document.querySelector("form").requestSubmit()');until('document.querySelector("main")?.textContent.includes("Synthetic UI verification")')
  check('Form submit starts exactly one mocked investigation','window.fixtureCounts.start===1')
  check('Manual evidence form is available on a reviewable investigation','!!document.querySelector("#follow-up-evidence")')
  check('Unverified draft is prominently labelled','document.querySelector("main").textContent.includes("Unverified draft: do not treat")')
  check('Observed facts show source line identifiers','document.querySelector("main").textContent.includes("incident:logs / L1")')
  js('(()=>{const el=document.querySelector("#follow-up-evidence");Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value").set.call(el,"Upstream metrics unavailable; supplied timestamps are from node A.");el.dispatchEvent(new Event("input",{bubbles:true}));})()')
  js('document.querySelector("#follow-up-evidence").form.requestSubmit();document.querySelector("#follow-up-evidence").form.requestSubmit()')
  until('document.querySelector("main").textContent.includes("Revision 2.")')
  check('Repeated evidence submission sends one request','window.fixtureCounts.evidence===1')
  check('Evidence submission binds expected revision','window.lastEvidence.expected_revision===1')
  check('Unavailable evidence is submitted as operator text','window.lastEvidence.text.includes("unavailable")')
  check('Successful follow-up clears the form','document.querySelector("#follow-up-evidence").value===""')
  shot('manual-evidence-desktop')
  js('window.workflowFixture.incident.title="Long incident "+"x".repeat(400)')
  js('document.querySelector("header .icon-button").click()');time.sleep(.4);viewport(390,844)
  check('Long incident title fits mobile detail view','document.documentElement.scrollWidth<=390')
  viewport(1440,1000)
  click('Review and approve');until('!!document.querySelector("dialog[open]")')
  js('document.querySelector("dialog .primary").click();document.querySelector("dialog .primary").click()')
  until('!document.querySelector("dialog[open]") && document.querySelector("main")?.textContent.includes("completed")')
  check('Repeated confirm creates one mocked approval request','window.fixtureCounts.approve===1')
  check('Approval binds the displayed evidence revision','window.lastApproval.review_digest==="revision-two"')
  # A rejected write remains visible across healthy background refreshes.
  js('window.fetch=async(url,init={})=>{if(init.method&&init.method!=="GET")return Response.json({detail:"Synthetic write failure"},{status:503});if(url==="/api/runs/ui-browser-fixture")return Response.json(window.workflowFixture);return window.actionFetch(url,init)}')
  nav('Agent workspace');js('document.querySelector("form").requestSubmit()');until('document.querySelector("[role=alert]")?.textContent.includes("Synthetic write failure")')
  js('document.querySelector("header .icon-button").click()');time.sleep(.5)
  until('!!document.querySelector(".connection.connected")')
  check('Background refresh does not erase an action failure','document.querySelector("[role=alert]")?.textContent.includes("Synthetic write failure")')
  js('window.fetch=window.actionFetch');nav('Overview');js('document.querySelector("[aria-label=\'Dismiss error\']").click()')

  command('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
  check('Reduced motion respected','Array.from(document.querySelectorAll("*")).every(e=>getComputedStyle(e).animationName==="none")')
  viewport(390,844);js('document.querySelector(".mobile-menu").click()') if not js('!!document.querySelector(".navigation-open")') else None
  check('Mobile menu exposes theme control','getComputedStyle(document.querySelector(".theme")).display!=="none"')
  nav('Settings');click('Disconnect');until('!!document.querySelector("#access-token")')
  check('Disconnect hides protected workspace','!document.querySelector("nav")')
  check('Mobile access screen fits viewport','document.documentElement.scrollWidth<=390');shot('access-mobile')
  assert not errors,errors
  report={'passed':len(checks),'checks':checks,'javascript_errors':errors,'scope':'Real local services for navigation; empty states and action submissions use browser-only fixtures. No server writes submitted.'}
  (OUT/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
 except Exception:
  shot('failure');raise
 finally:
  try:command('Browser.close')
  except Exception:pass
