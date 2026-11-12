/* FIELD-013 — local browser visual-region proposals; NOT semantic recognition.
 * Source pixels stay on-device. Generic regions are offered for human review;
 * no classifier, external network, camera pose, dimensions, or safety claims.
 */
(function(root){'use strict';
  const clamp=x=>Math.max(0,Math.min(1,x));
  const iou=(a,b)=>{
    let x=Math.max(0,Math.min(a[2],b[2])-Math.max(a[0],b[0]));
    let y=Math.max(0,Math.min(a[3],b[3])-Math.max(a[1],b[1]));
    const inter=x*y, area=t=>(t[2]-t[0])*(t[3]-t[1]);
    return inter/Math.max(1e-9,area(a)+area(b)-inter);
  };
  function scanRGBA(rgba,width,height,options={}){
    if(!(rgba instanceof Uint8Array||rgba instanceof Uint8ClampedArray)||!Number.isInteger(width)||!Number.isInteger(height)||
      width<96||height<96||rgba.length!==width*height*4)throw Error('Bad source pixels');
    const maxCandidates=Math.max(0,Math.min(10,options.maxCandidates??5));
    if(!maxCandidates)return [];
    // Downsample *only* for region salience; bounds are still in original photo coordinates.
    const nx=32,ny=24, energy=new Float64Array(nx*ny), palette=new Float64Array(nx*ny),cells=nx*ny;
    const gray=new Float32Array(width*height),saturation=new Float32Array(width*height);
    for(let i=0;i<gray.length;i++){
      const r=rgba[i*4],g=rgba[i*4+1],b=rgba[i*4+2];
      gray[i]=.299*r+.587*g+.114*b;
      saturation[i]=Math.max(r,g,b)-Math.min(r,g,b);
    }
    for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
      const x0=Math.round(i*width/nx),y0=Math.round(j*height/ny);
      const x1=Math.min(width-2,Math.round((i+1)*width/nx)),y1=Math.min(height-2,Math.round((j+1)*height/ny));
      let acc=0,col=0,count=0;
      for(let y=y0+1;y<y1;y+=2)for(let x=x0+1;x<x1;x+=2){
        const k=y*width+x;
        const dx=Math.abs(gray[k+1]-gray[k-1]);
        const dy=Math.abs(gray[k+width]-gray[k-width]);
        acc+=Math.min(180,dx+dy);col+=saturation[k];count++;
      }
      energy[j*nx+i]=count?acc/count:0;
      palette[j*nx+i]=count?col/count:0;
    }
    const overall=energy.reduce((a,b)=>a+b,0)/cells;
    const proposals=[];
    // Multiple window scales identify visual areas of interest without semantic labels.
    for(const [ww,hh] of [[6,6],[9,8],[12,9],[17,12],[22,15]]){
      for(let y=0;y+hh<=ny;y+=Math.max(2,Math.floor(hh/3))){
        for(let x=0;x+ww<=nx;x+=Math.max(2,Math.floor(ww/3))){
          let e=0,c=0,v=0;const n=ww*hh;
          for(let yy=y;yy<y+hh;yy++)for(let xx=x;xx<x+ww;xx++){
            const k=yy*nx+xx;e+=energy[k];c+=palette[k];
          }
          e/=n;c/=n;
          const cx=(x+ww/2)/nx,cy=(y+hh/2)/ny;
          const borderPenalty=(cx<.09||cx>.91||cy<.08||cy>.92)?.7:1;
          const texture=e/(overall+1);
          // Extremely repetitive texture is not automatically a useful object.
          const score=(Math.min(texture,2.2)*.75 + Math.min(c/65,1.5)*.15 + Math.min(e/35,1.5)*.1)
                      *borderPenalty*Math.sqrt(Math.min(1,.2/(ww*hh/cells)));
          if(score<.22)continue;
          const box=[x/nx,y/ny,(x+ww)/nx,(y+hh)/ny].map(v=>+clamp(v).toFixed(5));
          proposals.push({bbox:box,score:+score.toFixed(5)});
        }
      }
    }
    proposals.sort((a,b)=>b.score-a.score);
    const chosen=[];
    for(const p of proposals){
      if(chosen.some(q=>iou(p.bbox,q.bbox)>.23))continue;
      // Do not treat arbitrarily large regions as segmented objects.
      if((p.bbox[2]-p.bbox[0])*(p.bbox[3]-p.bbox[1])>.6)continue;
      chosen.push({bbox:p.bbox,score:p.score,kind:'VISUAL_REGION_NOT_OBJECT_IDENTIFIED'});
      if(chosen.length>=maxCandidates)break;
    }
    return chosen;
  }
  function materialRegion(region,photo_id,digest,id){
    if(!region||!/^material-[A-Za-z0-9_-]{1,80}$/.test(id)||!/^[0-9a-f]{64}$/.test(digest))throw Error('Invalid provenance');
    const b=region.bbox;
    if(!Array.isArray(b)||b.length!==4||!b.every(x=>typeof x==='number'&&x>=0&&x<=1)||b[2]<=b[0]||b[3]<=b[1])throw Error('Invalid box');
    return {id,label:'Unidentified visual region — inspect',role:'unknown',status:'tentative',mobility:'unknown',
      source_frame:'photo_normalized',photo_id,photo_sha256:digest,bbox:b,
      provenance:'LOCAL_CV_TENTATIVE',registered_to_sketch:false,certified_safe:false,width:null};
  }
  const api={scanRGBA,materialRegion,iou};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.MOTIF013_SCAN=api;
})(typeof window!=='undefined'?window:globalThis);
