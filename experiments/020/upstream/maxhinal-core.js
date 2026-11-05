(function(root, factory) {
  const modes = typeof module === 'object' && module.exports
    ? require('./maxhinal-modes.js')
    : root.MaxhinalModes;
  const api = factory(modes);
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.MaxhinalCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function(Modes) {
  if (!Modes) throw new Error('MaxhinalModes is required');

  const FORMAT = 'maxhinal/v0';
  const JOB_FORMAT = 'maxhinal-job/v0';

  function normalizeSeed(seed) {
    return String(seed == null ? '0' : seed);
  }

  function hashSeed(seed) {
    const text = normalizeSeed(seed);
    let h = 2166136261 >>> 0;
    for (let i = 0; i < text.length; i += 1) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h >>> 0;
  }

  function createRng(seed, offset=0) {
    let state = hashSeed(seed);
    let position = 0;
    function nextRaw() {
      state = (state + 0x6D2B79F5) >>> 0;
      let t = state;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      position += 1;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
    while (position < offset) nextRaw();
    return nextRaw;
  }

  function stableValue(value) {
    if (Array.isArray(value)) return value.map(stableValue);
    if (value && typeof value === 'object') {
      return Object.keys(value).sort().reduce((acc, key) => {
        acc[key] = stableValue(value[key]);
        return acc;
      }, {});
    }
    return value;
  }

  function stableStringify(value) {
    return JSON.stringify(stableValue(value), null, 2);
  }

  function clone(value) {
    return value == null ? value : JSON.parse(JSON.stringify(value));
  }

  function ordinal(prefix, index) {
    return `${prefix}-${String(index + 1).padStart(4, '0')}`;
  }

  function createRide(corpusMeta, seed='0') {
    const corpus = clone(corpusMeta || {});
    return {
      format:FORMAT,
      ride_id:`ride-${hashSeed(`${corpus.digest || ''}|${normalizeSeed(seed)}`).toString(16).padStart(8,'0')}`,
      created_at:null,
      corpus,
      replay:{ status:'EXACT', local_digest:corpus.digest || null },
      seed:normalizeSeed(seed),
      gas:[],
      operations:[],
      outputs:[],
      residuals:[],
      bad_spins:[],
      authority:'none',
      promotion:'NONE'
    };
  }

  function hydrateRide(inputRide, localCorpusMeta) {
    const ride = clone(inputRide);
    if (!ride || ride.format !== FORMAT) throw new Error(`Invalid ride format: ${ride && ride.format}`);
    const localDigest = localCorpusMeta && localCorpusMeta.digest || null;
    ride.replay = {
      status: ride.corpus && ride.corpus.digest === localDigest ? 'EXACT' : 'CORPUS_DRIFT',
      local_digest: localDigest
    };
    return ride;
  }

  function resolveInputRefs(ride, corpusPayload, refs) {
    const records = corpusPayload && Array.isArray(corpusPayload.records) ? corpusPayload.records : [];
    const resolved = [];
    const missing = [];
    for (const ref of Array.isArray(refs) ? refs : []) {
      if (ref && ref.kind === 'slice') {
        const value = records.find((row) => row.id === ref.slice_id);
        if (!value) {
          missing.push({ ref:clone(ref), code:'MISSING_INPUT', message:`Missing Slice input: ${ref.slice_id}` });
          continue;
        }
        resolved.push({
          ref:clone(ref),
          value:clone(value),
          provenance:{ kind:'slice', slice_id:value.id, path:value.path || null }
        });
        continue;
      }
      if (ref && ref.kind === 'derived') {
        const output = (ride.outputs || []).find((row) => row.output_id === ref.output_id);
        if (!output) {
          missing.push({ ref:clone(ref), code:'MISSING_INPUT', message:`Missing derived input: ${ref.output_id}` });
          continue;
        }
        resolved.push({
          ref:clone(ref),
          value:clone(output.value),
          provenance:{ kind:'derived', output_id:output.output_id, source_operation_id:output.source_operation_id }
        });
        continue;
      }
      missing.push({ ref:clone(ref), code:'MISSING_INPUT', message:'Unsupported or malformed input reference.' });
    }
    return { resolved, missing };
  }

  function appendBadSpin(inputRide, badSpin) {
    const ride = clone(inputRide);
    const record = {
      bad_id:ordinal('bad', ride.bad_spins.length),
      output_ref:badSpin && badSpin.output_ref || null,
      source_operation_id:badSpin && badSpin.source_operation_id || null,
      kind:badSpin && badSpin.kind || 'rejected',
      text:badSpin && badSpin.text || null,
      reason:badSpin && badSpin.reason || null
    };
    ride.bad_spins.push(record);
    return ride;
  }

  function appendResidual(ride, operationId, residual) {
    const record = {
      residual_id:ordinal('res', ride.residuals.length),
      source_operation_id:operationId,
      code:residual.code || 'UNRESOLVED',
      message:residual.message || '',
      details:residual.details == null ? null : clone(residual.details)
    };
    ride.residuals.push(record);
    return record.residual_id;
  }

  function runOperation(inputRide, corpusPayload, request) {
    const ride = clone(inputRide);
    const operationId = ordinal('op', ride.operations.length);
    const mode = request && request.mode;
    const inputs = clone(request && request.inputs || []);
    const parameters = clone(request && request.parameters || {});
    const coPhase = request && request.co_phase || 'unknown';
    const seedOffset = ride.operations.length;
    const operation = {
      operation_id:operationId,
      mode,
      inputs,
      parameters,
      co_phase:coPhase,
      seed_offset:seedOffset,
      output_refs:[],
      residual_refs:[],
      receipt:{ authority:'none', promotion:'NONE' }
    };

    const fn = Modes.MODES && Modes.MODES[mode];
    if (typeof fn !== 'function') {
      operation.residual_refs.push(appendResidual(ride, operationId, {
        code:'INVALID_MODEL', message:`Unknown Maxhinal mode: ${mode}`
      }));
      ride.operations.push(operation);
      return ride;
    }

    const resolution = resolveInputRefs(ride, corpusPayload, inputs);
    if (resolution.missing.length) {
      for (const issue of resolution.missing) operation.residual_refs.push(appendResidual(ride, operationId, issue));
      ride.operations.push(operation);
      return ride;
    }

    const modeResult = fn({
      corpus:corpusPayload && corpusPayload.records || [],
      resolvedInputs:resolution.resolved,
      parameters,
      rng:createRng(ride.seed, seedOffset),
      operation:clone(operation)
    }) || { status:'UNRESOLVED', projection:null, residuals:[], bad_spins:[] };

    if (modeResult.projection != null) {
      const output = {
        output_id:ordinal('out', ride.outputs.length),
        kind:'derived',
        mode,
        status:modeResult.status || 'OK',
        source_operation_id:operationId,
        source_refs:clone(inputs),
        value:clone(modeResult.projection)
      };
      ride.outputs.push(output);
      operation.output_refs.push(output.output_id);
    }

    for (const residual of modeResult.residuals || []) {
      operation.residual_refs.push(appendResidual(ride, operationId, residual));
    }

    for (const badSpin of modeResult.bad_spins || []) {
      const record = {
        bad_id:ordinal('bad', ride.bad_spins.length),
        output_ref:operation.output_refs.at(-1) || null,
        source_operation_id:operationId,
        kind:badSpin.kind || 'bad-spin',
        text:badSpin.text || null,
        reason:badSpin.reason || null
      };
      ride.bad_spins.push(record);
    }

    ride.operations.push(operation);
    return ride;
  }

  function registerGas(ride, corpusPayload, gasIds) {
    const records = corpusPayload && Array.isArray(corpusPayload.records) ? corpusPayload.records : [];
    for (const sliceId of Array.isArray(gasIds) ? gasIds : []) {
      if (ride.gas.some((entry) => entry.kind === 'slice' && entry.slice_id === sliceId)) continue;
      const record = records.find((row) => row.id === sliceId);
      ride.gas.push({
        kind:'slice',
        slice_id:sliceId,
        corpus_digest:ride.corpus.digest || null,
        title:record && record.title || null,
        path:record && record.path || null,
        status:record ? 'AVAILABLE' : 'MISSING'
      });
    }
  }

  function runJob(corpusPayload, job, existingRide) {
    if (job && job.format && job.format !== JOB_FORMAT) throw new Error(`Invalid job format: ${job.format}`);
    let ride = existingRide
      ? hydrateRide(existingRide, corpusPayload && corpusPayload.meta || {})
      : createRide(corpusPayload && corpusPayload.meta || {}, job && job.seed);
    if (!existingRide && job && job.seed != null) ride.seed = normalizeSeed(job.seed);
    registerGas(ride, corpusPayload, job && job.gas || []);
    for (const operation of job && job.operations || []) {
      ride = runOperation(ride, corpusPayload, operation);
    }
    return ride;
  }

  function semanticSnapshot(ride) {
    const copy = clone(ride);
    copy.created_at = null;
    return copy;
  }

  function serializeRide(ride) {
    return `${stableStringify(ride)}\n`;
  }

  function markdownReceipt(ride) {
    const lines = [
      '# MADD Hugh Jackman Maxhinal Ride Receipt',
      '',
      `Ride: ${ride.ride_id}`,
      `Corpus: ${ride.corpus && ride.corpus.digest || 'unknown'}`,
      `Replay: ${ride.replay && ride.replay.status || 'unknown'}`,
      `Seed: ${ride.seed}`,
      'Authority: none',
      'Promotion: NONE',
      '',
      '## Gas'
    ];
    if (!(ride.gas || []).length) lines.push('- none');
    for (const gas of ride.gas || []) lines.push(`- ${gas.slice_id} (${gas.status || 'AVAILABLE'})`);
    lines.push('', '## Operations');
    if (!(ride.operations || []).length) lines.push('- none');
    for (const op of ride.operations || []) {
      lines.push(`- ${op.operation_id}: ${op.mode} [${op.co_phase}] -> ${op.output_refs.join(', ') || 'no output'}`);
    }
    if ((ride.residuals || []).length) {
      lines.push('', '## Residuals');
      for (const item of ride.residuals) lines.push(`- ${item.residual_id} ${item.code}: ${item.message}`);
    }
    if ((ride.bad_spins || []).length) {
      lines.push('', '## Bad spins');
      for (const item of ride.bad_spins) lines.push(`- ${item.bad_id} -> ${item.output_ref || 'none'}: ${item.reason || item.kind}`);
    }
    return `${lines.join('\n')}\n`;
  }

  return {
    FORMAT,
    JOB_FORMAT,
    normalizeSeed,
    hashSeed,
    createRng,
    stableStringify,
    createRide,
    hydrateRide,
    resolveInputRefs,
    appendBadSpin,
    runOperation,
    runJob,
    semanticSnapshot,
    serializeRide,
    markdownReceipt
  };
});
