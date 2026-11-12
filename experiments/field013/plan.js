/* FIELD-013: non-committal material→goal candidate pairing and typed critique.
 * Image recognition, physical fit, and load certification NEVER follow from a candidate.
 */
(function(root){'use strict';
  const ROLES = new Set(['boundary_module','support_candidate','flexible_barrier','visual_cue','unknown']);
  function evaluate(state){
    if(!state||!Array.isArray(state.items)||!Array.isArray(state.materials))throw Error('Missing shared state');
    const routes=state.items.filter(x=>x.kind==='desired'&&x.status!=='user_rejected'&&x.points.length===2);
    const inventory=state.materials.filter(x=>x.status!=='user_rejected');
    const out=[],unknown=[];
    for(const m of inventory){
      if(!ROLES.has(m.role))throw Error('Invalid material role');
      if(m.role==='unknown'){
        unknown.push({material_id:m.id,question:'What is this visual region? Confirm whether it is a distinct usable object.',kind:'inspect-photo'});
        continue;
      }
      if(m.mobility==='fixed')continue;
      if(!routes.length){unknown.push({material_id:m.id,question:'Mark the desired boundary on the sketch before proposing photo-to-plan placement.',kind:'trace-route'});continue;}
      const used=routes.slice(0,3);
      for(const route of used){
        const hypothesizedRole={boundary_module:'boundary',support_candidate:'possible support',
          flexible_barrier:'conditional infill',visual_cue:'visual cue'}[m.role];
        const claim={id:`possibility-${m.id}-${route.id}`,material_id:m.id,route_id:route.id,
          title:`Explore ${m.label} as ${hypothesizedRole}`,status:'HYPOTHETICAL_NO_FIT_VERIFIED',
          basis:[m.id,route.id,m.photo_id],
          geometry_known:false,physical_scale_known:false,actual_mobility_known:m.mobility==='movable',
          safety_certified:false,
          hold:['Photo does not register to yard geometry','Width/fit are unverified',
            'Anchor and joint stability unverified','Check snagging, tipping, entrapment and escape routes']};
        out.push(claim);
      }
    }
    const supported=inventory.filter(m=>m.role==='support_candidate'&&m.status!=='user_rejected').length;
    const panels=inventory.filter(m=>m.role==='boundary_module'&&m.status!=='user_rejected').length;
    if(supported&&panels)out.push({id:'possible-support-network',title:'Explore panel–support combinations',
      status:'HYPOTHETICAL_SUPPORT_NETWORK',material_id:null,route_id:null,
      basis:inventory.filter(m=>['support_candidate','boundary_module'].includes(m.role)).map(m=>m.id),
      geometry_known:false,physical_scale_known:false,safety_certified:false,
      hold:['Mutual bracing is a hypothesis, not a structural calculation','Connector label strength does not establish joint performance',
        'Requires supervised cold-fit and independent suitability review']});
    if(routes.length)out.push({id:'reroute',title:'Explore shifting the desired boundary to existing supports',
      status:'ALTERNATIVE_GOAL_GEOMETRY_ONLY',material_id:null,route_id:null,basis:routes.map(r=>r.id),
      geometry_known:false,physical_scale_known:false,safety_certified:false,
      hold:['Sketched proportions may not reflect physical distances','Do not silently replace user intent']});
    return {status:'SOURCE_BOUND_HYPOTHESES',candidate_count:out.length,candidates:out.slice(0,16),questions:unknown.slice(0,10),
      real_fitted_layouts:0,automatic_safety_clearances:0,unconfirmed_photo_map_matches:0};
  }
  const api={evaluate};if(typeof module!=='undefined'&&module.exports)module.exports=api;root.MOTIF013_PLAN=api;
})(typeof window!=='undefined'?window:globalThis);
