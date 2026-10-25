import test, { afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import ts from 'typescript';
const source = readFileSync(new URL('../src/lib/api.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;
let sequence = 0;
const load = () => import('data:text/javascript;base64,' + Buffer.from(compiled + `\n// ${sequence++}`).toString('base64'));
const originalFetch = globalThis.fetch;
const originalTimeout = AbortSignal.timeout;
afterEach(() => { globalThis.fetch = originalFetch; AbortSignal.timeout = originalTimeout; });
test('token is attached to requests and disconnect removes it', async () => {
  const client = await load(); const calls = [];
  globalThis.fetch = async (url, init) => { calls.push(init); return Response.json({ ok: true }); };
  client.setAccessToken('synthetic-test-token'); await client.api('/dashboard');
  assert.equal(calls[0].headers.get('Authorization'), 'Bearer synthetic-test-token');
  client.setAccessToken(''); await client.api('/dashboard');
  assert.equal(calls[1].headers.get('Authorization'), null);
  assert.deepEqual(client.authorizationHeaders(), {});
});
test('Headers objects are preserved and JSON defaults applied', async () => {
  const client = await load();
  globalThis.fetch = async (_, init) => { assert.equal(init.headers.get('X-Request-ID'), 'fixture'); assert.equal(init.headers.get('Content-Type'), 'application/json'); return Response.json({}); };
  await client.api('/dashboard', { headers: new Headers({ 'X-Request-ID': 'fixture' }) });
});
test('file upload lets the browser set multipart boundaries', async () => {
  const client = await load(); const body = new FormData(); body.append('file', new Blob(['fixture']), 'fixture.txt');
  globalThis.fetch = async (_, init) => { assert.equal(init.headers.has('Content-Type'), false); assert.equal(init.body, body); return Response.json({}); };
  await client.api('/documents/upload', { method: 'POST', body });
});
test('401 retains typed status for the access gate', async () => {
  const client = await load(); globalThis.fetch = async () => Response.json({ detail: 'Authentication required' }, { status: 401 });
  await assert.rejects(client.api('/dashboard'), error => error instanceof client.ApiError && error.status === 401 && error.message === 'Authentication required');
});
test('non-JSON error response has a safe status fallback', async () => {
  const client = await load(); globalThis.fetch = async () => new Response('<html>Unavailable</html>', { status: 503 });
  await assert.rejects(client.api('/dashboard'), { message: 'Request failed (503)', status: 503 });
});
test('caller abort reaches the transport without being masked', async () => {
  const client = await load(); const controller = new AbortController();
  globalThis.fetch = (_, init) => new Promise((resolve, reject) => init.signal.addEventListener('abort', () => reject(init.signal.reason), { once: true }));
  const pending = client.api('/dashboard', { signal: controller.signal }); controller.abort();
  await assert.rejects(pending, { name: 'AbortError' });
});
test('read timeout explains how to recover', async () => {
  const client = await load(); const controller = new AbortController(); AbortSignal.timeout = () => controller.signal;
  globalThis.fetch = async () => { controller.abort(new DOMException('Timeout', 'TimeoutError')); throw controller.signal.reason; };
  await assert.rejects(client.api('/dashboard'), error => error.status === 0 && error.message.includes('refreshing'));
});
test('write timeout is not retried and warns about uncertain outcome', async () => {
  const client = await load(); const controller = new AbortController(); AbortSignal.timeout = () => controller.signal; let calls = 0;
  globalThis.fetch = async () => { calls++; controller.abort(new DOMException('Timeout', 'TimeoutError')); throw controller.signal.reason; };
  await assert.rejects(client.api('/runs', { method: 'POST' }), error => error.message.includes('may still be processing'));
  assert.equal(calls, 1);
});
test('network errors produce an actionable message', async () => {
  const client = await load(); globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(client.api('/dashboard'), { message: 'Unable to reach the server. Check your connection and try again.', status: 0 });
});
