/* Build the real native UNDERSTORY six-family validation envelope.
 * These are *synthetic* records constructed in memory. No private memory read.
 */
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const at = t => '2026-11-05T00:0' + t + ':00Z';

export function syntheticUnderstory(result) {
  const b = {
    schema:'memento.understory-record/v0',
    observer:'synthetic-motif-observer',
    world_instance_id:'synthetic-motif-garden',
    evidence_refs:['synthetic:motif:source-witness'],
  };
  const contact = {...b,id:'contact-motif-001',family:'contact',
    occurrence_ref:'synthetic:rfa:act-0001',
    sensed_at:at(0),recorded_at:at(0)};
  const attention = {...b,id:'attention-motif-001',family:'attention',
    contact_ref:contact.id, action:'attended',
    occurred_at:at(1),recorded_at:at(1)};
  const decoder = {...b,id:'decoder-motif-001',family:'decoder',
    contact_ref:contact.id,decoder_ref:'motif:018:concept-proposal',
    projection_ref:'synthetic:motif:representation-projection',
    applied_at:at(2),recorded_at:at(2)};
  const stance = {...b,id:'stance-motif-001',family:'stance',
    projection_ref:decoder.projection_ref,stance:'held',
    formed_at:at(3),recorded_at:at(3)};
  const association = {...b,id:'association-motif-001',family:'association',
    member_refs:[contact.id,decoder.id],
    relation_hint:'hypothesized-structural-explanation',
    status:'unresolved',recorded_at:at(4)};
  const activation = {...b,id:'activation-motif-001',family:'activation',
    trace_refs:[contact.id,association.id,stance.id],
    trigger_ref:result.status==='HOLD_FOR_HUMAN_REVIEW' ?
      'synthetic:later-review-of-proposal' : 'synthetic:later-review-of-hold',
    descendant_projection_ref:'synthetic:future-question-not-answer',
    activated_at:at(5),recorded_at:at(5)};
  return [contact,attention,decoder,stance,association,activation];
}

export async function checkUnderstory(mementoRoot,result) {
  if (!mementoRoot) throw Error('MEMENTO checkout required');
  const path = join(resolve(mementoRoot),'scripts/lib/understory.mjs');
  const native = await import(pathToFileURL(path).href);
  const rows = syntheticUnderstory(result);
  const witness = native.validateUnderstoryRecords(rows);
  if (witness.recordCount!==6)
    throw Error('UNDERSTORY did not validate six record families');
  return {
    familyCounts:witness.familyCounts,
    recordCount:witness.recordCount,
    stance:rows[3].stance,
    association:rows[4].status,
    activation:rows[5].id,
    sourceStatus:'SYNTHETIC_IN_MEMORY_ONLY',
    ledgerWrites:0,
    canonAdmissions:0,
    actualHumanContactClaim:false,
  };
}
