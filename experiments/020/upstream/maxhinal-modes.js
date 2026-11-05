(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.MaxhinalModes = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  function normalize(value) {
    return String(value || '').toLowerCase().normalize('NFKD').replace(/[^a-z0-9\s-]/g, ' ').replace(/\s+/g, ' ').trim();
  }

  function searchCorpus(corpus, query) {
    const terms = normalize(query).split(' ').filter(Boolean);
    if (!terms.length) return corpus.slice();
    return corpus.map((item) => {
      const title = normalize(item.title);
      const carry = normalize(item.carry);
      const summary = normalize(item.summary);
      const text = normalize(item.text);
      let score = 0;
      for (const term of terms) {
        if (title.includes(term)) score += 8;
        if (carry.includes(term)) score += 6;
        if (summary.includes(term)) score += 3;
        if (text.includes(term)) score += 1;
      }
      return { item, score };
    }).filter((row) => row.score > 0)
      .sort((a, b) => b.score - a.score || String(a.item.title).localeCompare(String(b.item.title)))
      .map((row) => row.item);
  }

  const STOP = new Set(['the','a','an','and','or','of','to','in','is','it','that','this','what','why','how','with','without','as','for','from','be','been','are','was','were','them','one','two','new']);

  function tokenSet(item) {
    const blob = normalize([item.title, item.summary, item.carry, item.text].join(' '));
    return new Set(blob.split(' ').filter((word) => word.length > 2 && !STOP.has(word)));
  }

  function suggestRelatives(corpus, selectedId, limit) {
    const selected = corpus.find((item) => item.id === selectedId);
    if (!selected) return [];
    const sourceTokens = tokenSet(selected);
    return corpus.filter((item) => item.id !== selectedId).map((item) => {
      const targetTokens = tokenSet(item);
      let overlap = 0;
      sourceTokens.forEach((token) => { if (targetTokens.has(token)) overlap += 1; });
      const titleBonus = normalize(selected.title).split(' ').some((token) => token.length > 3 && normalize(item.carry).includes(token)) ? 1 : 0;
      return { item, score: overlap + titleBonus };
    }).sort((a, b) => b.score - a.score || String(a.item.title).localeCompare(String(b.item.title)))
      .slice(0, Math.max(1, Number(limit) || 5))
      .map((row) => row.item);
  }

  const PRESSURE = {
    same_object: 'What persistent carrier makes these one identity rather than two similar occurrences?',
    relational_lineage: 'What attributable road actually connects A to B?',
    successor: 'What was inherited from A, and what was born fresh in B?',
    new_occurrence: 'What resemblance is most likely to tempt someone into overstating continuity?',
    unresolved: 'What single missing observation would most change your call?'
  };

  function pressureQuestion(verdict) {
    return PRESSURE[verdict] || PRESSURE.unresolved;
  }

  const HAIKU = {
    same_object: ['one body returns', 'the room changes around it', 'still wearing one name'],
    relational_lineage: ['old edges remain', 'two rooms inherit the road', 'new ghosts learn the name'],
    successor: ['seed leaves the old hand', 'another body grows it', 'kin without the throne'],
    new_occurrence: ['same costume new room', 'resemblance knocks at the door', 'no one lets it in'],
    unresolved: ['fog keeps both names still', 'the missing road stays missing', 'ask what crossed the dark']
  };

  const BANGERS = {
    same_object: [
      ['Same name on the door', 'Same scar in the light', 'If the carrier never broke', 'Make me prove it tonight'],
      ['You said the body stayed', 'I said show me the chain', 'Same face is cheap evidence', 'Tell me what remained']
    ],
    relational_lineage: [
      ['Not the body — keep the thread', 'Not the room — remember the road', 'Call it dead where it went dead', 'Do not bury what still holds'],
      ['Different fire, same wire', 'Different mouth, same vow', 'If the edge can bear the history', 'Show me the carrier now']
    ],
    successor: [
      ['Take the seed, not the throne', 'Take the road, not the name', 'Kin can carry something forward', 'Kin does not become the same'],
      ['What was given, what was born', 'What came through, what came alive', 'Do not crown the child with memory', 'Make the lineage survive']
    ],
    new_occurrence: [
      ['Same costume, different room', 'Same echo, different mouth', 'Resemblance wants a passport', 'Make it show the road out'],
      ['Looks familiar, prove the bridge', 'Feels familiar, name the chain', 'If there is no carrier crossing', 'Let the new thing keep its name']
    ],
    unresolved: [
      ['Fog is not a missing fact', 'Fog is where the witness ends', 'Name the thing you cannot see yet', 'Do not counterfeit the end'],
      ['Maybe yes and maybe no', 'Keep the question in the room', 'One more witness changes everything', 'Leave some dignity to gloom']
    ]
  };

  const LAWS = {
    same_object: [
      'Persistent appearance is not persistent identity; name the carrier.',
      'A claim of sameness inherits the burden of an attributable carrier.'
    ],
    relational_lineage: [
      'Continuity belongs to the smallest attributable relation that actually survives the crossing.',
      'A local instance may die while an attributable road remains alive.'
    ],
    successor: [
      'Inheritance may carry lineage without carrying identity or authority.',
      'A successor can receive a road without becoming the traveler who made it.'
    ],
    new_occurrence: [
      'Resemblance may recur without transporting identity.',
      'A familiar surface is evidence of recognition, not proof of continuity.'
    ],
    unresolved: [
      'Unresolved is not a hole; it is a witnessed limit.',
      'The edge of observation is not the edge of existence.'
    ]
  };

  function pick(list, rng) {
    const index = Math.min(list.length - 1, Math.floor(Math.max(0, Math.min(0.999999, rng())) * list.length));
    return list[index];
  }

  function spinOutput(input, rng) {
    const random = typeof rng === 'function' ? rng : Math.random;
    const verdict = PRESSURE[input && input.verdict] ? input.verdict : 'unresolved';
    const reason = normalize(input && input.reason);
    const avoidKind = input && input.avoidKind;
    const refusalThreshold = avoidKind === 'refusal' ? 0 : (!reason ? 0.28 : (verdict === 'unresolved' || verdict === 'new_occurrence' ? 0.16 : 0.07));
    if (random() < refusalThreshold) {
      const lines = ['NO SONG.', 'These two things may just be standing near each other.'];
      return { kind:'refusal', label:'REFUSAL', lines, text:lines.join('\n') };
    }

    const forms = ['haiku', 'banger', 'law'];
    let form = forms[Math.min(2, Math.floor(random() * 3))];
    if (form === avoidKind) form = forms[(forms.indexOf(form) + 1) % forms.length];

    let lines;
    if (form === 'haiku') lines = HAIKU[verdict].slice();
    if (form === 'banger') lines = pick(BANGERS[verdict], random).slice();
    if (form === 'law') lines = [pick(LAWS[verdict], random)];
    return { kind:form, label:form === 'banger' ? '4-LINE BANGER' : form.toUpperCase(), lines, text:lines.join('\n') };
  }

  function emptyResult(status, code, message) {
    return { status, projection:null, residuals:[{ code, message }], bad_spins:[] };
  }

  function sourceRef(entry) {
    return entry && entry.provenance && (entry.provenance.slice_id || entry.provenance.output_id)
      || entry && entry.ref && (entry.ref.slice_id || entry.ref.output_id)
      || null;
  }

  function runDiscontinuity(context) {
    const inputs = context.resolvedInputs || [];
    if (inputs.length < 2) return emptyResult('INSUFFICIENT_INPUT', 'INSUFFICIENT_INPUT', 'Discontinuity requires two inputs.');
    const parameters = context.parameters || {};
    const verdict = PRESSURE[parameters.verdict] ? parameters.verdict : 'unresolved';
    const reason = parameters.reason || '';
    const spin = spinOutput({ verdict, reason, avoidKind:parameters.avoid_kind }, context.rng);
    return {
      status:'OK',
      projection:{
        verdict,
        reason,
        source_refs:inputs.map(sourceRef),
        pressure_question:pressureQuestion(verdict),
        creative:spin
      },
      residuals:[],
      bad_spins:[]
    };
  }

  const MODES = { discontinuity:runDiscontinuity };

  return {
    MODES,
    normalize,
    searchCorpus,
    suggestRelatives,
    pressureQuestion,
    spinOutput,
    runDiscontinuity
  };
});
