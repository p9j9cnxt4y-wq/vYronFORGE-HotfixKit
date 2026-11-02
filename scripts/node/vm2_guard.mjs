import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const MIN = [3,12,2];
const DENY_BUILTINS = new Set(['child_process','node:child_process','cluster','node:cluster','worker_threads','node:worker_threads','vm','node:vm','inspector','node:inspector','sqlite','node:sqlite']);

function parse(v){ return String(v).split(/[.+-]/).slice(0,3).map(x=>Number.parseInt(x,10)||0); }
function atLeast(v,min=MIN){ const a=parse(v); for(let i=0;i<3;i++){ if(a[i]>min[i]) return true; if(a[i]<min[i]) return false; } return true; }

export function assertVm2Version(){
  const pkg = require('vm2/package.json');
  if(!atLeast(pkg.version)) throw new Error(`VYF_DENY_VM2_VERSION:${pkg.version}:minimum=${MIN.join('.')}`);
  return pkg.version;
}

export function assertNodeVMConfig(config={}){
  if(config.nesting === true) throw new Error('VYF_DENY_VM2_NESTING');
  const r=config.require;
  if(r === true) throw new Error('VYF_DENY_VM2_REQUIRE_TRUE');
  if(r && typeof r === 'object'){
    if(r.external === true || (Array.isArray(r.external) && r.external.length)) throw new Error('VYF_DENY_VM2_EXTERNAL_REQUIRE');
    if(r.mock && Object.keys(r.mock).length) throw new Error('VYF_DENY_VM2_REQUIRE_MOCK');
    if(typeof r.resolve === 'function' || typeof r.customRequire === 'function') throw new Error('VYF_DENY_VM2_HOST_REQUIRE_CALLBACK');
    const builtins = Array.isArray(r.builtin) ? r.builtin : [];
    if(builtins.includes('*')) throw new Error('VYF_DENY_VM2_BUILTIN_WILDCARD');
    for(const b of builtins){ if(DENY_BUILTINS.has(b)) throw new Error(`VYF_DENY_VM2_BUILTIN:${b}`); }
  }
  if(process.env.VYRONFORGE_ISOLATED_WORKER !== '1') throw new Error('VYF_DENY_VM2_NO_OUTER_ISOLATION');
  return true;
}

export function hardenedVMOptions(extra={}){
  assertVm2Version();
  if(extra.sandbox && Object.values(extra.sandbox).some(v => typeof v === 'function'))
    throw new Error('VYF_DENY_HOST_FUNCTION_IN_SANDBOX');
  return Object.freeze({ ...extra, timeout: Math.min(Number(extra.timeout||1000), 5000), allowAsync:false, eval:false, wasm:false, bufferAllocLimit:Math.min(Number(extra.bufferAllocLimit||16777216), 33554432) });
}
