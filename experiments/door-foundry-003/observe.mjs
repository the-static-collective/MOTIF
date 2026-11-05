// Only local stdin -> source-owned GRAFT closed-template numeric sensor.
// No network, fs writes, dynamic URL, or arbitrary user-selected module path.
import {readFileSync} from 'node:fs';
import {execute} from './generated_sensor.mjs';
try {
  const input=readFileSync(0,'utf8');
  if(input.length>4096)throw Error('HOLD_OVERSIZED_INPUT');
  const data=JSON.parse(input);
  const result=execute(data);
  if(!result || !['OBSERVED_NUMERIC_FIELD','HOLD_INVALID_RESPONSE',
      'HOLD_MISSING_FIELD','HOLD_WRONG_FIELD_TYPE'].includes(result.status))
    throw Error('HOLD_GENERATED_MODULE_UNRECOGNIZED_RESULT');
  process.stdout.write(JSON.stringify(result));
} catch {
  process.stdout.write(JSON.stringify({status:'HOLD_INVALID_RESPONSE',value:null}));
  process.exitCode=1;
}
