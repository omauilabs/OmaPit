"""Validate the compatibility manifest (assets/compatibility.json).

The manifest is the single source for compatibility claims. Rows are scoped to
model + protocol + transport + adapter version, and the validator refuses
claims the evidence cannot support. COMPATIBILITY.md is rendered from it.

  python3 backend/compatibility.py          check the manifest and the page
  python3 backend/compatibility.py --write  regenerate COMPATIBILITY.md
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

PAGE = ROOT / 'COMPATIBILITY.md'

def _cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')

def _roles(names):
    return ', '.join(r for r in ('food', 'ambient', 'battery') if r in names) or '—'

def render(manifest):
    """Render the human-readable compatibility page from the manifest."""
    lines = [
        '# Compatibility',
        '',
        '<!-- Generated from assets/compatibility.json by `python3 backend/compatibility.py --write`. Edit the JSON, not this page. -->',
        '',
        f"OmaPit {manifest['app_version']}. Every row is scoped to one model, protocol, transport and adapter version. "
        'Nothing here is a claim about other firmware, other units of the same model or the whole brand.',
        '',
        '**Experimental** means OmaPit decodes the format but it has not passed full owner acceptance on real hardware. '
        '**Seen live** lists channels observed from real hardware; it does not cover accuracy, range, reconnection or alarms. '
        'OmaPit only reads temperatures: no adapter controls a grill, fan or probe.',
        '',
        '## Direct Bluetooth',
        '',
        '| Model | Protocol | Adapter | Status | Seen live | Decoded, not yet seen live | Evidence |',
        '|---|---|---|---|---|---|---|',
    ]
    for row in manifest['devices']:
        live = row.get('omapit_live_test') or row.get('live_reception_observed')
        decoded = set(row['roles']) | set(row.get('unverified_roles', []))
        seen = set(row['roles']) if live else set()
        evidence = row['evidence']
        if row.get('acceptance'): evidence += f" ([details]({row['acceptance']}))"
        lines.append('| ' + ' | '.join(_cell(v) for v in [
            row['model'], row['protocol'], f"{row['adapter']} {row['adapter_version']}",
            row['implementation'].capitalize(), _roles(seen), _roles(decoded - seen), evidence]) + ' |')
    lines += ['', '## Bridges and imports', '',
              'A bridge carries readings from another system. Its status says nothing about which thermometers that system supports.', '',
              '| Path | Status | Evidence | Hardware compatibility |', '|---|---|---|---|']
    for row in manifest.get('bridges', []):
        lines.append('| ' + ' | '.join(_cell(row[k]) for k in BRIDGE_TEXT) + ' |')
    lines += ['', '## Not supported yet', '',
              'MEATER, ThermoPro, Inkbird, FireBoard, Combustion and other brands are candidates under review, not supported devices. '
              'Owners can help by sharing an aggregate report; see [community/README.md](community/README.md). '
              'Developers can add a device by following [ADAPTERS.md](ADAPTERS.md).', '']
    return '\n'.join(lines)

def main(argv=None):
    write = '--write' in (sys.argv[1:] if argv is None else argv)
    manifest = load(); issues = problems(manifest, app_version())
    if not issues:
        page = render(manifest)
        if write: PAGE.write_text(page)
        elif not PAGE.is_file() or PAGE.read_text() != page:
            issues.append('COMPATIBILITY.md is out of date; run python3 backend/compatibility.py --write')
    for issue in issues: print(issue, file=sys.stderr)
    print('compatibility manifest: ' + ('invalid' if issues else 'ok'))
    return 1 if issues else 0

if __name__ == '__main__':
    sys.exit(main())
