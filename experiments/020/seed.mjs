import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {designInstrument} from './instrument_garden.mjs';
const root=fileURLToPath(new URL('seeded_minecraft.json',import.meta.url));
const packet=JSON.parse(readFileSync(root,'utf8'));
console.log(JSON.stringify(designInstrument(packet),null,2));
