const test=require('node:test');
const assert=require('node:assert/strict');
const {add,markSynced,pending}=require('../src/queue.cjs');
const obs={local_id:'local-1',object_id:'A',observed_location:'Shelf B',observer:'registrar',evidence_ref:'field-note-1'};
test('queue observation and prevent duplicate local IDs',()=>{
  const q=add([],obs);
  assert.equal(q.length,1);
  assert.equal(add(q,obs).length,1);
  assert.equal(pending(q).length,1);
});
test('mark successful sync and retain audit response',()=>{
  const q=markSynced(add([],obs),'local-1',{observation_id:'server-1',discrepancy:true});
  assert.equal(pending(q).length,0);
  assert.equal(q[0].server_response.discrepancy,true);
});
test('reject missing evidence',()=>{
  assert.throws(()=>add([],{...obs,evidence_ref:''}),/required/);
});
