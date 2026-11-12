/* Deterministic pinhole camera & world-ground unprojection. No WebGL/CDN.
 * Real 3-dimensional scene vertices, depth sorting and perspective. */
(function(root){'use strict';
 const norm = v=>{const n=Math.hypot(v.x,v.y,v.z)||1;return {x:v.x/n,y:v.y/n,z:v.z/n};};
 const sub=(a,b)=>({x:a.x-b.x,y:a.y-b.y,z:a.z-b.z});
 const dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z;
 const cross=(a,b)=>({x:a.y*b.z-a.z*b.y,y:a.z*b.x-a.x*b.z,z:a.x*b.y-a.y*b.x});
 const add=(a,b,k=1)=>({x:a.x+b.x*k,y:a.y+b.y*k,z:a.z+b.z*k});
 const camera=(yaw=.80,pitch=.64,distance=17,target={x:5,y:.45,z:2.25})=>({yaw,pitch,distance,target});
 function basis(c){
  const eye={x:c.target.x+c.distance*Math.cos(c.pitch)*Math.sin(c.yaw),
    y:c.target.y+c.distance*Math.sin(c.pitch),
    z:c.target.z+c.distance*Math.cos(c.pitch)*Math.cos(c.yaw)};
  const forward=norm(sub(c.target,eye)),right=norm(cross(forward,{x:0,y:1,z:0})),up=cross(right,forward);
  return {eye,forward,right,up};
 }
 function project(p,c,w,h){
   const b=basis(c),q=sub(p,b.eye),z=dot(q,b.forward),f=Math.min(w,h)*1.25;
   if(z<=.08)return null;
   return {x:w/2+(dot(q,b.right)*f)/z,y:h/2-(dot(q,b.up)*f)/z,depth:z};
 }
 function rayGround(px,py,c,w,h,groundY=0){
   const b=basis(c),f=Math.min(w,h)*1.25,
     dir=norm(add(add(b.forward,b.right,(px-w/2)/f),b.up,-(py-h/2)/f));
   if(Math.abs(dir.y)<1e-6)return null;
   const t=(groundY-b.eye.y)/dir.y;
   if(t<=0)return null;
   const p=add(b.eye,dir,t);return {x:p.x,z:p.z,y:groundY};
 }
 function panelFaces(o, S){
   const a=S.world(o.points[0]),b=S.world(o.points[1]);
   const dx=b.x-a.x,dz=b.z-a.z,L=Math.hypot(dx,dz)||.01;
   const t=Math.max(.015,o.thickness)/2,nx=-dz/L*t,nz=dx/L*t,low=o.clearance,hi=low+o.height;
   const pts=[
      {x:a.x+nx,y:low,z:a.z+nz},{x:b.x+nx,y:low,z:b.z+nz},
      {x:b.x+nx,y:hi,z:b.z+nz},{x:a.x+nx,y:hi,z:a.z+nz},
      {x:a.x-nx,y:low,z:a.z-nz},{x:b.x-nx,y:low,z:b.z-nz},
      {x:b.x-nx,y:hi,z:b.z-nz},{x:a.x-nx,y:hi,z:a.z-nz}];
   return [[0,1,2,3],[5,4,7,6],[3,2,6,7],[4,5,1,0],[0,3,7,4],[1,5,6,2]].map((f,i)=>({verts:f.map(id=>pts[id]),tone:i}));
 }
 function supportFaces(o,S){
   const p=S.world(o.points[0]),r=Math.max(.05,o.thickness*.6),verts=[],n=8;
   for(let j=0;j<n;j++){
     const angle=j*2*Math.PI/n;
     verts.push({x:p.x+Math.cos(angle)*r,z:p.z+Math.sin(angle)*r,y:0});
   }
   const faces=[];for(let j=0;j<n;j++){
     const k=(j+1)%n,a=verts[j],b=verts[k];
     faces.push({verts:[a,b,{...b,y:o.height},{...a,y:o.height}],tone:j%2});
   }
   faces.push({verts:verts.map(v=>({...v,y:o.height})),tone:1});return faces;
 }
 function polygons(objects,S,cam,w,h){
   const out=[];
   for(const o of objects){
     if(o.kind==='access')continue;
     const faces=o.points.length===2?panelFaces(o,S):supportFaces(o,S);
     for(const f of faces){const points=f.verts.map(v=>project(v,cam,w,h));if(points.some(p=>p===null))continue;
       out.push({id:o.id,kind:o.kind,status:o.status,depth:points.reduce((sum,p)=>sum+p.depth,0)/points.length,
           points,tone:f.tone,style:o.kind==='desired'?'hypothetical':o.status==='tentative'?'tentative':'human'});
     }
   }
   return out.sort((a,b)=>b.depth-a.depth);
 }
 const api={camera,basis,project,rayGround,polygons};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.MOTIF014_CAMERA=api;
})(typeof window!=='undefined'?window:globalThis);
