// ALEX-MOTIF-021: bounded local exact-phrase research over pinned public source copies.
// The broader ALEX reading floor is not replaced by this search adapter.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const DIR=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../research/packets/MOTIF-021');
const TERMS=['common ancestor','reference','original','custody','independent'];
const MAX_HITS=3;
const sha=x=>createHash('sha1').update(Buffer.from('blob '+x.length+'\0')).update(x).digest('hex');
const readJson=p=>JSON.parse(readFileSync(path.join(DIR,p),'utf8'));

export function researchPacket(){
 const manifest=readJson('source-manifest.json');
 if(manifest.schema!=='alex.motif021.source-manifest/v0'||manifest.sources.length!==5)
   throw Error('HOLD_UNKNOWN_OR_INCOMPLETE_MANIFEST');
 const hits=[],coverage=[];
 for(const source of manifest.sources){
   if(!/^sources\/[a-z0-9.-]+\.md$/.test(source.archive)||
      !/^[0-9a-f]{40}$/.test(source.git_blob)||
      !/^[0-9a-f]{40}$/.test(source.source_commit))
      throw Error('HOLD_UNSAFE_SOURCE_PATH_OR_PIN');
   const bytes=readFileSync(path.join(DIR,source.archive));
   if(sha(bytes)!==source.git_blob)throw Error('HOLD_SOURCE_BYTES_DRIFT');
   const lines=bytes.toString('utf8').split('\n');
   let candidates=0,captured=0;
   for(let i=0;i<lines.length;i++){
     const matched=TERMS.filter(t=>lines[i].toLowerCase().includes(t));
     if(!matched.length)continue;
     candidates++;
     if(captured>=MAX_HITS)continue;
     hits.push({
       hit_id:source.id+'-L'+(i+1),source_id:source.id,
       repository:source.repository,
       source_commit:source.source_commit,source_path:source.source_path,
       git_blob:source.git_blob,archive:source.archive,
       line_start:i+1,line_end:i+1,
       exact_line_excerpt:lines[i].slice(0,240),
       matched_phrases:matched,classification:'DISCOVERY_NOT_ADMITTED_EVIDENCE'
     });
     captured++;
   }
   coverage.push({source_id:source.id,lines_scanned:lines.length,
     matching_lines:candidates,hits_retained:captured,
     inspected_entire_materialized_source:true,
     hits_truncated:candidates>MAX_HITS});
 }
 const search={
   id:'ALEX-MOTIF-021-SEARCH',corpus_id:'ALEX-MOTIF-021-PINNED-FIVE',
   query:TERMS.join(' OR '),query_type:'exact_phrase_bounded_OR',
   index_id:'LOCAL_PINNED_PUBLIC_MARKDOWN',index_version:'v0',
   fields_searched:['original_text_lines'],
   record_types_searched:['public_markdown_snapshot'],
   page_or_reading_scope:manifest.sources.map(x=>x.archive),
   pagination_complete:true,unreadable_or_missing_ranges:[],
   exclusions:['all unmaterialized sources','live branches since pinned cuts','private project material','unlicensed redistribution decisions'],
   truncation:{hits_per_source:MAX_HITS,matching_line_overflow:coverage.some(x=>x.hits_truncated)},
   filters:[{origin:'public',content_verified_by_git_blob:true}],
   result_ids:hits.map(x=>x.hit_id),result_count:hits.length,
   observed_at:'2026-11-05',producer:'alex.motif021-local-search/v0',
   coverage_status:'PARTIAL'
 };
 return {
   schema:'alex.motif-source-research-packet/v1',
   packet_id:manifest.packet_id,
   question:'What evidence distinguishes shared upstream source ancestry from shared difficulty or corrupt reference families, and what source-owned machinery can support review?',
   research_mode:'FIND+TRACE+PRESSURE',
   search_observation:search,
   source_inventory:manifest.sources,
   coverage,
   hits,
   claim_status:'SOURCE_DISCOVERY_ONLY_NO_REAL_CUSTODY_AUTHENTICATED',
   research_findings:[
    {claim:'MOTIF-019 computes conditional source-error associations, not verified literal common ancestry.',
      status:'INFERRED_FROM_PINNED_PUBLIC_DESIGN',source_ids:['SRC-02']},
    {claim:'MOTIF-020 runs original Maxhinal hypothesis transformations without promoting their creative output into evidence.',
      status:'INFERRED_FROM_PINNED_PUBLIC_DESIGN',source_ids:['SRC-01']},
    {claim:'ALEX distinguishes discovery trace from evidence path and requires source-locus provenance.',
      status:'SOURCE_POLICY',source_ids:['SRC-03']},
    {claim:'planZ is an index/review boundary, not a plan-execution authority.',
      status:'SOURCE_POLICY',source_ids:['SRC-04']},
    {claim:'GRAFT provides reviewable source cuts; composition does not grant deployment permissions.',
      status:'SOURCE_POLICY',source_ids:['SRC-05']}
   ],
   next_questions:[
    'Can independently recovered source custody distinguish copied material from shared environment?',
    'Which independent third reference breaks a possible two-reference common-mode error?',
    'Which bounded executable analysis can GRAFT compose without promoting inferred ancestry into verified lineage?'
   ],
   restrictions:{
     only_public_document_snapshots:true,
     actual_external_repository_search_run:false,
     actual_local_pinned_search_run:true,
     human_or_private_evidence_collected:false,
     exact_materialized_source_files:5,
     target_runtime_production:false,
     independently_authenticated_custody:false,
     permission_to_publish_private_data:false,
     evidence_admission:'NONE',
     automatic_execution_authority:'NONE'
   }
 };
}
if(process.argv[1]===fileURLToPath(import.meta.url))
 process.stdout.write(JSON.stringify(researchPacket(),null,2)+'\n');
