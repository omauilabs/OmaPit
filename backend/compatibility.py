"""Validate the compatibility manifest (assets/compatibility.json).

The manifest is the single source for compatibility claims. Rows are scoped to
model + protocol + transport + adapter version, and the validator refuses
claims the evidence cannot support. Run directly to check the shipped file.
"""
import json, sys
from pathlib import Path
import adapters

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'assets' / 'compatibility.json'
ROLES = {'food', 'ambient', 'battery'}
IMPLEMENTATION = {'planned', 'experimental', 'implemented'}
DEVICE_TEXT = ('model', 'protocol', 'transport', 'adapter', 'adapter_version', 'implementation', 'evidence')
BRIDGE_TEXT = ('adapter', 'implementation', 'evidence', 'hardware_compatibility')

def _version(text):
    parts = str(text).split('.')
    return tuple(int(p) for p in parts) if len(parts) == 3 and all(p.isdigit() for p in parts) else None

def problems(manifest, app_version=None):
    """Return a list of human-readable problems; empty means the manifest is valid."""
    if not isinstance(manifest, dict): return ['manifest must be a JSON object']
    found = []
    if manifest.get('schema') != 1: found.append('schema must be 1')
    if app_version is not None and manifest.get('app_version') != app_version:
        found.append(f"app_version {manifest.get('app_version')!r} does not match manifest.json {app_version!r}")
    if manifest.get('control_commands') is not False:
        found.append('control_commands must be false: no adapter controls hardware')
    devices = manifest.get('devices')
    if not isinstance(devices, list) or not devices: found.append('devices must be a non-empty list'); devices = []
    for i, row in enumerate(devices):
        where = f'devices[{i}]'
        if not isinstance(row, dict): found.append(f'{where} must be an object'); continue
        where = f"{where} ({row.get('model', '?')} {row.get('protocol', '?')})"
        for key in DEVICE_TEXT:
            if not isinstance(row.get(key), str) or not row[key].strip(): found.append(f'{where}: {key} is required')
        if row.get('implementation') not in IMPLEMENTATION:
            found.append(f'{where}: implementation must be one of {sorted(IMPLEMENTATION)}')
        if not isinstance(row.get('omapit_live_test'), bool): found.append(f'{where}: omapit_live_test must be true or false')
        if row.get('implementation') == 'implemented' and row.get('omapit_live_test') is not True:
            found.append(f'{where}: implemented requires an OmaPit live test; use experimental')
        adapter = adapters.REGISTRY.get(row.get('adapter'))
        if adapter is None and isinstance(row.get('adapter'), str) and row['adapter'].strip(): found.append(f"{where}: unknown adapter {row.get('adapter')!r}")
        elif adapter is not None:
            claimed, current = _version(row.get('adapter_version')), _version(adapter.ADAPTER_VERSION)
            if claimed is None: found.append(f'{where}: adapter_version must look like 1.2.3')
            elif claimed > current: found.append(f'{where}: adapter_version {row["adapter_version"]} is newer than the shipped adapter {adapter.ADAPTER_VERSION}')
        roles, unverified = row.get('roles'), row.get('unverified_roles', [])
        if not isinstance(roles, list) or not roles or not set(roles) <= ROLES:
            found.append(f'{where}: roles must be a non-empty subset of {sorted(ROLES)}'); roles = []
        if not isinstance(unverified, list) or not set(unverified) <= ROLES:
            found.append(f'{where}: unverified_roles must be a subset of {sorted(ROLES)}'); unverified = []
        if set(roles) & set(unverified): found.append(f'{where}: a role cannot be both verified and unverified')
        if 'live_reception_observed' in row and not isinstance(row['live_reception_observed'], bool):
            found.append(f'{where}: live_reception_observed must be true or false')
        if row.get('acceptance') and not (ROOT / row['acceptance']).is_file():
            found.append(f"{where}: acceptance document {row['acceptance']} is missing")
    bridges = manifest.get('bridges', [])
    if not isinstance(bridges, list): found.append('bridges must be a list'); bridges = []
    for i, row in enumerate(bridges):
        if not isinstance(row, dict): found.append(f'bridges[{i}] must be an object'); continue
        for key in BRIDGE_TEXT:
            if not isinstance(row.get(key), str) or not row[key].strip(): found.append(f'bridges[{i}]: {key} is required')
    return found

def load(path=MANIFEST):
    return json.loads(Path(path).read_text())

def app_version():
    return json.loads((ROOT / 'manifest.json').read_text())['version']

def main():
    issues = problems(load(), app_version())
    for issue in issues: print(issue, file=sys.stderr)
    print('compatibility manifest: ' + ('invalid' if issues else 'ok'))
    return 1 if issues else 0

if __name__ == '__main__':
    sys.exit(main())
