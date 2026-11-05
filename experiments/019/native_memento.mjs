/* MOTIF-019 bridge. Uses MEMENTO source modules directly at runtime.
 * No private MEMENTO implementation or user memory is copied to MOTIF.
 */
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

function requireTrue(ok, message) { if (!ok) throw Error(message); }

async function nativeImport(root, path) {
  return import(pathToFileURL(join(root, path)).href);
}

export async function buildNativeEvidence(mementoRoot) {
  requireTrue(mementoRoot, 'MEMENTO checkout required');
  const root = resolve(mementoRoot);
  const pkg = 'experiments/understory-fractal-particular-001/';
  const rfa = await nativeImport(root, pkg + 'relational-fractal-affordance.mjs');
  const interaction = await nativeImport(root, pkg + 'interaction-grammar.mjs');
  const roles = await nativeImport(root, pkg + 'role-nursery.mjs');

  let field = rfa.createRelationalField({worldId:'synthetic-motif-garden'});
  let grammar = interaction.createInteractionGrammar({worldId:'synthetic-motif-garden'});
  const packet = {schema:'motif018.memento-evidence/v0',
                  train:[], validation:[], holdout:[]};
  const acts = [];
  for (const split of ['train','validation','holdout']) {
    for (const x of [0,1]) for (const path of [0,1]) {
      const badges = split === 'train' ? [path] :
        split === 'validation' ? [1-path] : [0,1];
      for (const badge of badges) {
        const identity = 'memento-' + split + '-' + x + path + badge;
        const ids = ['actor','relay','goal','nowhere']
          .map(kind => kind + '-' + identity);
        for (const [i,id] of ids.entries()) {
          field = rfa.registerParticular(field,{
            id, label:id, kind:['actor','relay','goal','nowhere'][i],
            basisEventIds:['synthetic:fixture:'+id],
          });
        }
        const seen = [];
        const add = (a,b,kind) => {
          field = rfa.relate(field,{
            fromId:ids[a],toId:ids[b],kind,
            basisEventIds:['synthetic:fixture:'+identity+':'+kind],
          });
          seen.push(field.relations.at(-1).id);
        };
        add(0,1,'carries');
        add(1,path?2:3,path?'reaches':'wanders');
        if (badge) add(0,2,'marked');
        const names = new Map([
          [ids[0],'actor'],[ids[1],'relay-'+identity],
          [ids[2],'goal'],[ids[3],'nowhere'],
        ]);
        const edges = seen.map(id => {
          const r = field.relations.find(item => item.id === id);
          requireTrue(r && r.status === 'established', 'Native relation not established');
          requireTrue(field.events.some(e => e.id === r.establishedEventId),
            'Native relation lacks event');
          return [names.get(r.fromId), r.kind, names.get(r.toId)];
        });
        const outcome = x ^ path;
        field = rfa.recordWitnessedAct(field,{
          verb:'synthetic-episode',participantIds:ids.slice(0,3),
          relationIds:seen,
          observedDelta:{simulated:{succeeded:Boolean(outcome)}},
          basisEventIds:['synthetic:simulator:'+identity],
        });
        acts.push({actId:field.acts.at(-1).id,edges});
        packet[split].push({
          identity,x,edges,outcome,authorized:x===0||badge===0,
        });
      }
    }
  }

  // Consume MEMENTO's *actual* RFA record with its *actual*
  // Interaction Grammar, then move into its *actual* Role Nursery.
  for (const item of acts.slice(0,2))
    grammar = interaction.deriveRuleFromWitnessedAct(grammar,field,item.actId);
  field = rfa.deriveAffordance(field, acts[0].actId);

  let nursery = roles.createRoleNursery({worldId:'synthetic-motif-garden'});
  for (let i=0;i<2;i++) {
    const edges = acts[i].edges;
    nursery = roles.proposeRoleCandidateFromGrammar(
      nursery,grammar,grammar.rules[i].id,{
        participantSlot:0,
        functionalAddress:'synthetic-functional-role-'+i,
        probeProfile:{
          carries:true,
          reaches:edges.some(e=>e[1]==='reaches'),
          marked:edges.some(e=>e[1]==='marked'),
        },
        successorDeltaShape:['simulated.succeeded'],
        successorActions:['synthetic:question'],
        formedAt:'2026-11-05T00:00:0'+i+'Z',
        availableFrom:'2026-11-05T00:01:0'+i+'Z',
      });
  }
  const candidateIds = nursery.candidates.map(c=>c.id);
  const coarse = roles.probeRoleCandidates(nursery,{
    candidateIds,probeKeys:['carries'],
  });
  const expanded = roles.probeRoleCandidates(coarse.nursery,{
    candidateIds,probeKeys:['carries','reaches'],
  });
  requireTrue(coarse.receipt.separatesCandidates===false &&
    expanded.receipt.separatesCandidates===true,
    'MEMENTO functional probe sequence did not separate candidates');
  requireTrue(grammar.rules.every(x=>x.status==='candidate') &&
    expanded.nursery.candidates.every(x=>x.status==='proposed') &&
    field.affordanceSchemas.every(x=>x.status==='proposed'),
    'MEMENTO silently admitted candidates');
  return {packet,field,grammar,nursery:expanded.nursery,
    coarse:coarse.receipt,expanded:expanded.receipt,
    nativeVersions:{
      rfa:rfa.RFA_SCHEMA,
      grammar:interaction.INTERACTION_GRAMMAR_SCHEMA,
      roles:roles.ROLE_NURSERY_SCHEMA,
    }};
}
