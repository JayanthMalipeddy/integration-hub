import base64
import json
import time
from pathlib import Path
import httpx
from websockets.sync.client import connect

ROOT=Path(__file__).resolve().parents[1]
client=httpx.Client(timeout=10,trust_env=False)
pages=client.get('http://127.0.0.1:9225/json/list').json()
page=next(p for p in pages if p['type']=='page')
checks=[]
errors=[]
with connect(page['webSocketDebuggerUrl'],open_timeout=10) as ws:
    sequence=0
    def command(method,params=None):
        global sequence
        sequence+=1
        current=sequence
        ws.send(json.dumps({'id':current,'method':method,'params':params or {}}))
        while True:
            reply=json.loads(ws.recv(timeout=20))
            if reply.get('method')=='Runtime.exceptionThrown': errors.append(reply['params'])
            if reply.get('id')==current:
                if 'error' in reply: raise RuntimeError(reply['error'])
                return reply.get('result',{})
    def js(expression):
        value=command('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
        if value.get('exceptionDetails'): raise RuntimeError(value['exceptionDetails'])
        return value['result'].get('value')
    def until(expression):
        for _ in range(40):
            if js(expression): return
            time.sleep(.25)
        raise AssertionError('Browser condition timed out: '+expression)
    command('Runtime.enable')
    command('Page.enable')
    command('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1100,'deviceScaleFactor':1,'mobile':False})
    command('Page.navigate',{'url':'http://127.0.0.1:5180'})
    until("document.querySelector('nav') && document.body.innerText.includes('local_free')")
    names=['Overview','Agent workspace','Knowledge library','Incident analysis','RCA investigation','Execution timeline','Analytics & evaluations','Provider configuration','Memory','Reports & exports','Settings']
    for name in names:
        js('Array.from(document.querySelectorAll("nav button")).find(b=>b.innerText.startsWith('+json.dumps(name)+')).click()')
        heading='Investigations' if name=='Overview' else name
        until('document.querySelector("h1")?.innerText==='+json.dumps(heading))
        assert js('document.querySelector("main").innerText.length')>100
        checks.append({'view':name,'rendered':True})
    js('Array.from(document.querySelectorAll("nav button")).find(b=>b.innerText.startsWith("Agent workspace")).click()')
    until('!!document.querySelector(".sample-row")')
    js('document.querySelector(".sample-row").click()')
    assert js('document.querySelector("textarea").value.length')>20
    checks.append({'sample_form_populates':True})
    theme=js('document.documentElement.dataset.theme')
    js('document.querySelector("button.theme").click()')
    until('document.documentElement.dataset.theme!=='+json.dumps(theme))
    checks.append({'theme_switches':True})
    js('Array.from(document.querySelectorAll("nav button")).find(b=>b.innerText.startsWith("Provider configuration")).click()')
    until('document.querySelector("main").innerText.includes("8082")')
    js('Array.from(document.querySelectorAll("nav button")).find(b=>b.innerText.startsWith("Analytics & evaluations")).click()')
    until('!!document.querySelector("main select")')
    choices=js('document.querySelector("main select").options.length')
    assert choices>=2
    js('document.querySelector("main select").value=document.querySelector("main select").options[1].value;document.querySelector("main select").dispatchEvent(new Event("change",{bubbles:true}))')
    until('document.querySelector("main").innerText.includes("Case-level evidence")')
    # Only this browser receives the fixture; the backend and its stored runs are unchanged.
    js("""window.originalQualityFetch=window.fetch;
    window.fetch=async function(input,options){
      const url=String(input);
      const fixture={id:'ui-test-malformed',status:'needs_human',incident:{title:'Malformed response UI test',service:'test',logs:'status=401'},finding:{},error:'Structured response did not match the required schema',created_at:new Date().toISOString(),traces:[]};
      if(url==='/api/runs/ui-test-malformed')return new Response(JSON.stringify(fixture),{headers:{'Content-Type':'application/json'}});
      const response=await window.originalQualityFetch(input,options);
      if(url==='/api/dashboard'){const data=await response.json();data.runs.unshift(fixture);return new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}});}
      return response;
    };
    document.querySelector('[aria-label="Refresh data"]').click();""")
    js('Array.from(document.querySelectorAll("nav button")).find(b=>b.innerText.startsWith("Incident analysis")).click()')
    until('document.querySelector("main").innerText.includes("Malformed response UI test")')
    js('Array.from(document.querySelectorAll("tbody tr")).find(r=>r.innerText.includes("Malformed response UI test")).click()')
    until('document.querySelector("main").innerText.includes("Structured response did not match")')
    assert not js('!!document.querySelector(".finding")')
    js('window.fetch=window.originalQualityFetch;document.querySelector("button.icon-button").click()')
    command('Page.navigate',{'url':'http://127.0.0.1:5180'})
    until("document.querySelector('nav') && document.body.innerText.includes('local_free')")
    (ROOT/'runtime/browser-edge-case-verification.json').write_text(json.dumps({'benchmark_history_selection':True,'malformed_finding_handoff':True}),encoding='utf-8')
    js('Array.from(document.querySelectorAll("nav button")).find(b=>b.innerText.startsWith("Provider configuration")).click()')
    until('document.querySelector("main").innerText.includes("8082")')
    png=command('Page.captureScreenshot' ,{'format':'png','captureBeyondViewport':True})['data']
    (ROOT/'docs/screenshots/providers-quality.png').write_bytes(base64.b64decode(png))
    assert not errors,errors
report={'checks':checks,'javascript_exceptions':errors,'dashboard':'http://127.0.0.1:5180','note':'Read-only navigation, sample form and theme checks; no investigation or approval was submitted.'}
(ROOT/'runtime/browser-quality-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
