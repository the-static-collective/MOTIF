/* FIELD-011 on-device pixel aperture + strictly typed proposal-to-board bridge.
 * No OCR, network, shape completion, image transfer or world registration.
 */
(function(root){'use strict';
  const SCHEMA='motif.field011.draft.v1';
  const good=(x)=>typeof x==='number'&&Number.isFinite(x)&&x>=0&&x<=1;
  const point=(v)=>Array.isArray(v)&&v.length===2&&v.every(good);
  const fitPoint=(p,w,h,bw=1000,bh=450)=>{
    if(!point(p)||![w,h,bw,bh].every(x=>Number.isFinite(x)&&x>0))throw Error('Bad coordinates');
    const s=Math.min(bw/w,bh/h),sw=w*s,sh=h*s;
    return [Number(((bw-sw)/2+p[0]*sw).toFixed(6))/bw,Number(((bh-sh)/2+p[1]*sh).toFixed(6))/bh];
  };
  const isHex=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
  function validate(packet,sourceDigest=null){
    if(!packet||packet.schema!==SCHEMA||packet.coordinate_frame!=='sketch_normalized'||
       packet.source_kind!=='USER_SKETCH'||!isHex(packet.source_sha256)||
       (sourceDigest&&packet.source_sha256!==sourceDigest)||
       !Array.isArray(packet.source_size)||packet.source_size.length!==2||
       !packet.source_size.every(x=>Number.isFinite(x)&&x>=90&&x<=10000)||
       !Array.isArray(packet.items)||packet.items.length>24||
       packet.asserts_complete_desired_boundary!==false||packet.asserts_physical_scale!==false||
       packet.asserts_safety!==false||packet.photo_to_sketch_registration!=='NOT_PERFORMED')
       throw Error('Untrusted or incompatible auto-draft packet');
    const seen=new Set();
    for(const i of packet.items){
      if(!i||typeof i.id!=='string'||!/^cv-[a-f0-9]{12}-\d{2}$/.test(i.id)||seen.has(i.id)||
         i.kind!=='desired'||i.status!=='tentative'||i.movable!==false||
         typeof i.label!=='string'||i.label.length>120||
         !Array.isArray(i.points)||i.points.length!==2||!i.points.every(point)||
         !i.evidence||i.evidence.source_sha256!==packet.source_sha256||
         i.evidence.semantic_status!=='POSSIBLE_MARK__NOT_CONFIRMED_BOUNDARY'||
         i.evidence.safety_certified!==false)throw Error('Unsafe draft object');
      seen.add(i.id);
    }
    return packet;
  }
  function toEvents(project, packet, stampId=()=>Date.now().toString(36)){
    validate(packet);
    if(!project||project.schema!=='motif.field010.v1'||project.base.source!=='user_sketch'||
       !Array.isArray(project.events)||!Array.isArray(project.base.items))throw Error('Import requires user sketch board');
    const ids=new Set(project.base.items.map(i=>i.id));
    for(const e of project.events){if(e.item?.id)ids.add(e.item.id);}
    const result=[];
    for(const i of packet.items){
      if(ids.has(i.id))continue;
      result.push({id:'auto-'+stampId(),type:'add',time:new Date().toISOString(),
        source:'LOCAL_VISION_DRAFT_NOT_OBSERVED_PHYSICAL_EVIDENCE',
        item:JSON.parse(JSON.stringify(i))});
      ids.add(i.id);
    }
    return result;
  }
  function _pixelCandidates(gray,w,h){
    if(gray.length!==w*h||Math.min(w,h)<90||w*h>2e6)throw Error('Bad pixel array');
    // Strictly exploratory short-stroke detector, designed to HOLD rather than infer a route.
    const stride=Math.max(1,Math.floor(Math.max(w,h)/900));
    const dw=Math.ceil(w/stride),dh=Math.ceil(h/stride);
    const src=new Uint8Array(dw*dh),intens=[];
    for(let y=0;y<dh;y++)for(let x=0;x<dw;x++){
      const v=gray[Math.min(h-1,y*stride)*w+Math.min(w-1,x*stride)];
      src[y*dw+x]=v;
      if(x%7===0&&y%7===0)intens.push(v);
    }
    intens.sort((a,b)=>a-b);const median=intens[Math.floor(intens.length/2)]||170;
    const threshold=Math.min(130,Math.max(68,median-43));
    const dark=new Uint8Array(dw*dh);
    for(let y=0;y<dh;y++)for(let x=0;x<dw;x++) dark[y*dw+x]=Number(src[y*dw+x]<threshold);
    // Remove long horizontal solid strokes and printed notebook ruling.
    for(let y=0;y<dh;y++){
      let x=0;while(x<dw){if(!dark[y*dw+x]){x++;continue;}const s=x;while(x<dw&&dark[y*dw+x])x++;
        if(x-s>Math.max(53,Math.floor(dw*.07)))for(let k=s;k<x;k++)dark[y*dw+k]=0;
      }
    }
    const visited=new Uint8Array(dw*dh),blocks=[];
    // Avoid expensive all-pixel flood fill on large dark backgrounds.
    for(let y=3;y<dh-3;y++)for(let x=3;x<dw-3;x++){
      const id=y*dw+x;if(!dark[id]||visited[id])continue;
      const stack=[id];visited[id]=1;let minx=x,maxx=x,miny=y,maxy=y,area=0;
      while(stack.length){const q=stack.pop(),xx=q%dw,yy=Math.floor(q/dw);area++;
        if(xx<minx)minx=xx;if(xx>maxx)maxx=xx;if(yy<miny)miny=yy;if(yy>maxy)maxy=yy;
        if(area>4500){stack.length=0;break;}
        for(const p of [q-1,q+1,q-dw,q+dw]){
          const px=p%dw,py=Math.floor(p/dw);
          if(p>=0&&p<visited.length&&Math.abs(px-xx)+Math.abs(py-yy)===1&&dark[p]&&!visited[p]){visited[p]=1;stack.push(p);}
        }
      }
      const ww=maxx-minx+1,hh=maxy-miny+1;
      if(area<7||area>350||Math.min(ww,hh)>12)continue;
      let axis=null;
      if(ww>=7&&ww<=Math.min(60,dw*.085)&&ww/hh>=1.7&&hh<=9)axis='H';
      else if(hh>=7&&hh<=Math.min(58,dh*.105)&&hh/ww>=1.7&&ww<=9)axis='V';
      if(axis)blocks.push({cx:(minx+maxx)/2,cy:(miny+maxy)/2,w:ww,h:hh,axis});
    }
    const groups=[];
    for(const axis of ['H','V']){
      const along=axis==='H'?'cx':'cy',cross=axis==='H'?'cy':'cx', size=axis==='H'?dw:dh;
      const c=blocks.filter(b=>b.axis===axis).sort((a,b)=>a[along]-b[along]);
      const used=new Set();const choices=[];
      for(let k=0;k<c.length;k++){
        const a=c[k];
        let line=c.filter(b=>Math.abs(b[cross]-a[cross])<=(axis==='H'?5:6))
          .sort((x,y)=>x[along]-y[along]);
        let cur=[];
        for(const z of line){
          if(cur.length && z[along]-cur[cur.length-1][along]>(axis==='H'?70:85)){
            if(cur.length>=3)choices.push(cur);cur=[];
          }
          cur.push(z);
        }
        if(cur.length>=3)choices.push(cur);
      }
      choices.sort((a,b)=>b.length-a.length);
      for(const arr of choices){
        const span=arr.at(-1)[along]-arr[0][along];
        if(span<Math.max(axis==='H'?45:35,size*(axis==='H'?.07:.09)))continue;
        if(arr.some(x=>used.has(x)))continue;
        const gaps=arr.slice(1).map((z,k)=>z[along]-arr[k][along]-(z[axis==='H'?'w':'h']+arr[k][axis==='H'?'w':'h'])/2);
        if(gaps.filter(x=>x>=4).length<Math.max(2,.6*gaps.length))continue;
        arr.forEach(x=>used.add(x));
        groups.push({axis,points:arr.map(z=>[Number(((z.cx+.5)/dw).toFixed(6)),Number(((z.cy+.5)/dh).toFixed(6))])});
        if(groups.length>=12)break;
      }
    }
    return groups;
  }
  function fromGray(gray,width,height,sourceDigest,{desiredDottedRule=false,sourceId='sketch-1'}={}){
    if(!isHex(sourceDigest))throw Error('Missing source SHA-256');
    const groups=_pixelCandidates(gray,width,height);
    const items=groups.map((g,k)=>({
      id:`cv-${sourceDigest.slice(0,12)}-${String(k+1).padStart(2,'0')}`,
      kind:'desired',label:`Possible dotted fragment ${k+1} · review`,status:'tentative',movable:false,
      points:[fitPoint(g.points[0],width,height),fitPoint(g.points.at(-1),width,height)],
      evidence:{source_id:sourceId,source_sha256:sourceDigest,method:'FIELD-011_BROWSER_PIXEL_HEURISTIC',
        source_normalized_points:g.points,axis:g.axis,semantic_status:'POSSIBLE_MARK__NOT_CONFIRMED_BOUNDARY',
        drawn_join_hypothesized:true,user_rule_dotted_is_desired:Boolean(desiredDottedRule),safety_certified:false}
    }));
    return validate({schema:SCHEMA,source_id:sourceId,source_sha256:sourceDigest,source_size:[width,height],board_size:[1000,450],
      coordinate_frame:'sketch_normalized',source_kind:'USER_SKETCH',method:'FIELD-011_BROWSER_HEURISTIC_NOT_VLM',
      items,source_line_count:groups.length,candidate_count:items.length,
      asserts_complete_desired_boundary:false,asserts_physical_scale:false,asserts_safety:false,
      photo_to_sketch_registration:'NOT_PERFORMED',note:'Tentative dark-stroke grouping only. False positives and missed lines expected.',
      next_inputs:['Review candidate markings','Draw missing routes','Enter one measured reference']});
  }
  function fromRGBA(data,w,h,digest,opts){
    if(!data||data.length!==w*h*4)throw Error('Wrong image byte count');
    const gray=new Uint8Array(w*h);
    for(let i=0;i<gray.length;i++)gray[i]=Math.round(.299*data[i*4]+.587*data[i*4+1]+.114*data[i*4+2]);
    return fromGray(gray,w,h,digest,opts);
  }
  function sha256Bytes(bytes){
    // Hash only; not an authentication signature. Pure-JS fallback for offline/file browsers.
    if(!(bytes instanceof Uint8Array))bytes=new Uint8Array(bytes);
    const K=[
      0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const len=bytes.length, padded=Math.ceil((len+9)/64)*64, data=new Uint8Array(padded);
    data.set(bytes);data[len]=128;
    const bits=len*8,hi=Math.floor(bits/4294967296),lo=bits>>>0;
    for(let i=0;i<4;i++){data[padded-8+i]=(hi>>>(24-8*i))&255;data[padded-4+i]=(lo>>>(24-8*i))&255;}
    const rotr=(n,b)=>(n>>>b)|(n<<(32-b)),w=new Uint32Array(64);
    for(let start=0;start<padded;start+=64){
      for(let i=0;i<16;i++){const off=start+i*4;w[i]=((data[off]<<24)|(data[off+1]<<16)|(data[off+2]<<8)|data[off+3])>>>0;}
      for(let i=16;i<64;i++){
        const a=w[i-15],b=w[i-2];
        w[i]=(w[i-16]+(rotr(a,7)^rotr(a,18)^(a>>>3))+w[i-7]+(rotr(b,17)^rotr(b,19)^(b>>>10)))>>>0;
      }
      let [a,b,c,d,e,f,g,h]=H;
      for(let i=0;i<64;i++){
        const s1=rotr(e,6)^rotr(e,11)^rotr(e,25),ch=(e&f)^(~e&g);
        const t1=(h+s1+ch+K[i]+w[i])>>>0;
        const s0=rotr(a,2)^rotr(a,13)^rotr(a,22),maj=(a&b)^(a&c)^(b&c);
        const t2=(s0+maj)>>>0;
        h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
      }
      const add=[a,b,c,d,e,f,g,h];for(let i=0;i<8;i++)H[i]=(H[i]+add[i])>>>0;
    }
    return H.map(x=>x.toString(16).padStart(8,'0')).join('');
  }
  const API={SCHEMA,validate,fitPoint,fromGray,fromRGBA,toEvents,sha256Bytes};
  if(typeof module==='object'&&module.exports)module.exports=API;
  root.MOTIF011=API;
})(typeof window!=='undefined'?window:globalThis);
