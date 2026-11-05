import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const DEFAULT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../research/packets/MOTIF-021');
const STOP=new Set('what which whose would could should where when why how does that this there with about from were have been then them each source sources these those into only under over before after can make is are an and for the in on of to by a as it do be'.split(' '));
const hash=x=>createHash('sha256').update(x).digest('hex');
const blob=x=>createHash('sha1').update(Buffer.from('blob '+x.length+'\0')).update(x).digest('hex');
function terms(s){return [...new Set(s.toLowerCase().split(/[^a-z0-9]+/).filter(t=>t.length>2&&!STOP.has(t)))];}
export function ask(question,corpus=DEFAULT){
 if(typeof question!=='string'||question.length<16||question.length>300)
  throw Error('HOLD_INVALID_QUESTION_LENGTH');
 const query=question.trim(),words=terms(query);
 if(words.length<2||words.length>20)throw Error('HOLD_UNBOUNDED_QUESTION');
 const manifest=JSON.parse(readFileSync(path.join(corpus,'source-manifest.json'),'utf8'));
 if(manifest.schema!=='alex.motif021.source-manifest/v0'||manifest.sources.length!==5)
  throw Error('HOLD_MISSING_SOURCE_MANIFEST');
 const scored=[],coverage=[];
 for(const s of manifest.sources){
  if(!/^sources\/[a-z0-9.-]+\.md$/.test(s.archive)||!/^[a-f0-9]{40}$/.test(s.git_blob))
   throw Error('HOLD_INVALID_SOURCE_PATH');
  const bytes=readFileSync(path.join(corpus,s.archive));
  if(blob(bytes)!==s.git_blob)throw Error('HOLD_TAMPERED_ORIGINAL_SOURCE');
  const lines=bytes.toString('utf8').split('\n');
  let matched=0;
  for(let i=0;i<lines.length;i++){
   const t=terms(lines[i]),overlap=words.filter(w=>t.includes(w));
   if(!overlap.length)continue;
   matched++;
   scored.push({source_id:s.id,repository:s.repository,source_commit:s.source_commit,
    source_path:s.source_path,source_blob:s.git_blob,line:i+1,
    score:overlap.length,matched_terms:overlap,excerpt:lines[i].slice(0,180),
    support:'DISCOVERY_ONLY'});
  }
  coverage.push({id:s.id,lines:lines.length,matches:matched,verified_git_blob:s.git_blob});
 }
 scored.sort((a,b)=>b.score-a.score||a.source_id.localeCompare(b.source_id)||a.line-b.line);
 const hits=[],perSource=new Map();
 for(const h of scored){
  if(hits.length>=18)break;
  if((perSource.get(h.source_id)||0)>=5)continue;
  hits.push(h);perSource.set(h.source_id,(perSource.get(h.source_id)||0)+1);
 }
 const result={schema:'alex.motif022.question-packet/v0',
  question:query,query_hash:hash(query),terms:words,
  status:hits.length?'RESEARCH_PACKET_HELD':'HOLD_NO_MATCHES',
  hits,coverage,source_count:manifest.sources.length,
  partial_coverage:true,total_matched_lines:scored.length,
  truncated:scored.length>hits.length,
  inquiry_not_source_authentication:true,
  real_independence_proved:false,authority:'none',external_actions:0};
 return {...result,checksum:hash(JSON.stringify(result))};
}
export function validate(packet){
 if(!packet||packet.schema!=='alex.motif022.question-packet/v0'||
   !['RESEARCH_PACKET_HELD','HOLD_NO_MATCHES'].includes(packet.status)||
   packet.authority!=='none'||packet.real_independence_proved!==false||
   packet.external_actions!==0||packet.partial_coverage!==true||
   !Array.isArray(packet.hits)||packet.hits.length>18)
  throw Error('HOLD_INVALID_ALEX_RESEARCH_PACKET');
 const {checksum,...body}=packet;
 if(checksum!==hash(JSON.stringify(body)))throw Error('HOLD_CHANGED_ALEX_RESEARCH_PACKET');
 return true;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 try{process.stdout.write(JSON.stringify(ask(process.argv.slice(2).join(' ')),null,2)+'\n')}
 catch(e){process.stderr.write(String(e.message)+'\n');process.exitCode=2}
}
