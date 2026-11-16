/* Pure queue operations, shared by mobile app and Node unit tests. */
function add(queue, observation) {
  if (!observation || !observation.object_id?.trim() || !observation.observed_location?.trim() ||
      !observation.observer?.trim() || !observation.evidence_ref?.trim()) {
    throw new Error('Object ID, location, observer and evidence reference are required');
  }
  if (!observation.local_id) throw new Error('local_id required');
  if (queue.some(x=>x.local_id===observation.local_id)) return queue;
  return [...queue, {...observation, sync_status:'pending'}];
}
function markSynced(queue, id, response) {
  return queue.map(x=>x.local_id===id ? {...x,sync_status:'synced',server_response:response} : x);
}
function pending(queue) {return queue.filter(x=>x.sync_status!=='synced')}
module.exports={add,markSynced,pending};
