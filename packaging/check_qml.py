#!/usr/bin/env python3
"""Fail on QML syntax errors in the native plugin.

  python3 packaging/check_qml.py

Runs Qt's qmllint (from qt6-declarative-dev-tools; set QMLLINT to override the
path) on every top-level .qml file. Only 'critical' findings, which are parse
errors, fail the check. Warnings are counted but expected: Quickshell and
Omarchy's qs.Commons modules exist only on Omarchy, so qmllint cannot resolve
their types here. Passing this check is not native acceptance.
"""
import json, os, shutil, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def qmllint():
    for candidate in (os.environ.get('QMLLINT'), shutil.which('qmllint6'), '/usr/lib/qt6/bin/qmllint', shutil.which('qmllint')):
        if candidate and Path(candidate).is_file(): return candidate
    sys.exit('qmllint not found; install qt6-declarative-dev-tools or set QMLLINT.')

def main():
    files = sorted(ROOT.glob('*.qml'))
    run = subprocess.run([qmllint(), '--json', '-', *map(str, files)], capture_output=True, text=True, cwd=ROOT)
    try: report = json.loads(run.stdout)
    except ValueError: sys.exit('qmllint produced no JSON report:\n' + run.stderr[-2000:])
    failed = False
    for entry in report['files']:
        name = Path(entry['filename']).name
        critical = [w for w in entry['warnings'] if w['type'] == 'critical']
        counts = Counter(w['type'] for w in entry['warnings'])
        print(f"{name}: {len(critical)} error(s), {counts.get('warning', 0)} warning(s)")
        for w in critical:
            failed = True
            print(f"  {name}:{w.get('line', '?')}:{w.get('column', '?')}: {w['message']}")
    if len(report['files']) != len(files): sys.exit(f'qmllint checked {len(report["files"])} of {len(files)} files')
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())
