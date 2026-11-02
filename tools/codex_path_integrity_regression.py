#!/usr/bin/env python3
import argparse, hashlib, json
CASES = [
  r'Z:\AREA_01',
  r'C:\Build\SOURCE_MUTATION=NONE',
  r'D:\repo_name\artifact_01.json',
  r'E:\A_B\C_D\file_name.txt',
]
def sha(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def compare(expected, observed):
    return {"expected":expected,"observed":observed,"expected_sha256":sha(expected),"observed_sha256":sha(observed),"byte_exact":expected.encode()==observed.encode()}
def main():
    ap=argparse.ArgumentParser(description='Benign regression harness for Codex Windows path character integrity.')
    ap.add_argument('--observed-json', help='JSON array of model-observed strings; omitted prints corpus')
    a=ap.parse_args()
    if not a.observed_json:
      print(json.dumps({"cases":CASES}, indent=2)); return
    observed=json.load(open(a.observed_json,encoding='utf-8'))
    if len(observed)!=len(CASES): raise SystemExit('VYF_DENY_CASE_COUNT_MISMATCH')
    results=[compare(e,o) for e,o in zip(CASES,observed)]
    print(json.dumps(results,indent=2))
    raise SystemExit(0 if all(r['byte_exact'] for r in results) else 2)
if __name__=='__main__': main()
