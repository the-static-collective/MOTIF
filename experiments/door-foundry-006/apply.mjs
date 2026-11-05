// MOTIF-006: a bounded, local-only batch bridge to the exact GRAFT-born raster
// operator. Every proposal stays synthetic. Never selects arbitrary source.
import {readFileSync} from 'node:fs';
import {execute} from './new_visual_rule.mjs';
try {
 const raw=readFileSync(0,'utf8');
 if(raw.length>90000)throw Error('HOLD_INPUT_BUDGET');
 const data=JSON.parse(raw);
 if(!data||!Array.isArray(data.queries)||data.queries.length>60)
   throw Error('HOLD_QUERY_BUDGET');
 const answers=data.queries.map(x=>execute(x));
 if(answers.some(x=>!x||!['PROPOSED_FRAME','HOLD_OUTSIDE_IMAGE',
   'HOLD_OBSTACLE','HOLD_BAD_FRAME_OR_ACTION',
   'HOLD_NOT_ONE_2X2_OBJECT'].includes(x.status)))
     throw Error('HOLD_UNKNOWN_OPERATOR_OUTPUT');
 process.stdout.write(JSON.stringify({status:'LOCAL_SYNTHETIC_ONLY',answers}));
} catch {
 process.stdout.write(JSON.stringify({status:'HOLD',answers:[]}));
 process.exitCode=1;
}
