#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NODE_DIR=ROOT/'scripts'/'node'
FAKE_ROOT=NODE_DIR/'node_modules'
FAKE=FAKE_ROOT/'vm2'
if FAKE_ROOT.exists():
    raise SystemExit('VYF_TEST_DENY_PREEXISTING_NODE_MODULES')

def write_version(version: str) -> None:
    FAKE.mkdir(parents=True, exist_ok=True)
    (FAKE/'package.json').write_text(json.dumps({'name':'vm2','version':version}), encoding='utf-8')

def run(js: str, *, isolated: bool=True, expect: int=0) -> subprocess.CompletedProcess[str]:
    env=os.environ.copy()
    if isolated: env['VYRONFORGE_ISOLATED_WORKER']='1'
    else: env.pop('VYRONFORGE_ISOLATED_WORKER',None)
    p=subprocess.run(['node','--input-type=module','-e',js],cwd=ROOT,env=env,text=True,capture_output=True)
    if p.returncode != expect:
        print(p.stdout, end='')
        print(p.stderr, end='', file=sys.stderr)
        raise SystemExit(f'VYF_TEST_NODE_RC_{p.returncode}_EXPECTED_{expect}')
    return p

try:
    write_version('3.11.6')
    old=run("import {assertVm2Version} from './scripts/node/vm2_guard.mjs'; try{assertVm2Version(); process.exit(9)}catch(e){if(!String(e.message).includes('VYF_DENY_VM2_VERSION')) process.exit(8); console.log('OLD_VERSION_DENY=PASS')}")
    print(old.stdout.strip())

    write_version('3.12.2')
    js=r"""
import { assertVm2Version, assertNodeVMConfig, hardenedVMOptions } from './scripts/node/vm2_guard.mjs';
if(assertVm2Version() !== '3.12.2') process.exit(10);
const bad=[
  {nesting:true}, {require:true}, {require:{external:true}},
  {require:{builtin:['*']}}, {require:{builtin:['child_process']}},
  {require:{mock:{x:{}}}}, {require:{resolve:()=>{}}}
];
for(const cfg of bad){ let denied=false; try{assertNodeVMConfig(cfg)}catch(_){denied=true} if(!denied) process.exit(11); }
assertNodeVMConfig({require:{builtin:['path','url']}});
let hostDenied=false; try{hardenedVMOptions({sandbox:{fn:()=>1}})}catch(e){hostDenied=String(e.message).includes('HOST_FUNCTION')} if(!hostDenied) process.exit(12);
const opts=hardenedVMOptions({timeout:9000});
if(opts.timeout!==5000 || opts.eval!==false || opts.wasm!==false || opts.allowAsync!==false) process.exit(13);
console.log('VM2_GUARD_FIXED_VERSION_AND_CONFIG=PASS');
"""
    good=run(js)
    print(good.stdout.strip())

    noiso=run("import {assertNodeVMConfig} from './scripts/node/vm2_guard.mjs'; try{assertNodeVMConfig({}); process.exit(9)}catch(e){if(!String(e.message).includes('NO_OUTER_ISOLATION')) process.exit(8); console.log('OUTER_ISOLATION_DENY=PASS')}", isolated=False)
    print(noiso.stdout.strip())
finally:
    shutil.rmtree(FAKE_ROOT, ignore_errors=True)

print('NODE_GUARD_BEHAVIOR=PASS')
