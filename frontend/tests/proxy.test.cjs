const test=require('node:test');
const assert=require('node:assert/strict');
const {allowed,authorize,backendUrl}=require('../api/proxy.cjs');
test('allow only named API paths',()=>{
 assert.equal(allowed('GET','dashboard'),true);
 assert.equal(allowed('POST','cases/abc/review'),true);
 assert.equal(allowed('GET','../../admin'),false);
 assert.equal(allowed('DELETE','objects'),false);
 assert.equal(allowed('POST','models/risk/train'),false);
});
test('require bearer token',()=>{
 assert.equal(authorize('Bearer correct-secret-123456789','correct-secret-123456789'),true);
 assert.equal(authorize('Bearer wrong','correct-secret-123456789'),false);
 assert.equal(authorize('Bearer anything',''),false);
});
test('backend must be HTTPS',()=>{
 assert.equal(backendUrl('https://api.example.org','dashboard'),'https://api.example.org/dashboard');
 assert.throws(()=>backendUrl('http://localhost:8765','dashboard'),/HTTPS/);
 assert.throws(()=>backendUrl('https://api.example.org','../secret'),/route not allowed/);
});
