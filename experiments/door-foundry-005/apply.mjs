// MOTIF-005: single approved local graph-rewrite candidate. No service calls,
// credentials, dynamic source paths, repository writes or physical execution.
import {readFileSync} from 'node:fs';
import {execute} from './new_guarded_operator.mjs';
try {
 const data=readFileSync(0,'utf8');
 if(data.length>6500)throw Error('HOLD_BUDGET');
 const request=JSON.parse(data);
 const result=execute(request);
 if(!result||!['PROPOSED_SYNTHETIC_ADD','HOLD_GUARD',
     'HOLD_BAD_INPUT','HOLD_UNTYPED','HOLD_ALREADY_PRESENT'].includes(result.status))
    throw Error('HOLD_UNKNOWN_GENERATED_RESULT');
 process.stdout.write(JSON.stringify(result));
} catch {
 process.stdout.write(JSON.stringify({status:'HOLD_BAD_INPUT',added:null}));
 process.exitCode=1;
}
