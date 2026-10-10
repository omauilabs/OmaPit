"""Read-only troubleshooting report. See TROUBLESHOOTING.md.

  python3 backend/diagnose.py [--db PATH] [--json]
  python3 backend/omapit.py diagnose [--db PATH]

Opens the cook store in SQLite read-only mode: it never migrates, creates or
changes anything, and never scans for devices. The report contains counts,
ages and statuses only: no cook names, notes, temperatures, device addresses
or secret values. Review it before sharing; paths can include your username.
"""
import argparse, importlib.util, json, os, platform, sqlite3, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapters, compatibility, devices
from omapit import store_path

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED_DEVICE_SCHEMA = 1   # devices.migrate PRAGMA user_version
SUPPORTED_WORKBENCH = '1'     # settings.workbench_schema
MONITOR_FRESH_SECONDS = 5     # matches omapit.state service_health
INSTALL_FILES = ('manifest.json', 'Main.qml', 'Widget.qml', 'backend/omapit.py', 'assets/compatibility.json')

def _tilde(path):
    path = str(path); home = str(Path.home())
    return '~' + path[len(home):] if path == home or path.startswith(home + os.sep) else path

def _age(seconds):
    if seconds < 0: return 'in the future (check the system clock)'
    for size, unit in ((86400, 'd'), (3600, 'h'), (60, 'min')):
        if seconds >= size: return f'{seconds / size:.0f} {unit} ago'
    return f'{seconds:.0f} s ago'

class Report:
    def __init__(self): self.checks = []
    def add(self, area, status, message, hint=None):
        self.checks.append({'area': area, 'status': status, 'message': message, **({'hint': hint} if hint else {})})
    @property
    def failed(self): return any(c['status'] == 'fail' for c in self.checks)

def _environment(r):
    try: version = json.loads((ROOT / 'manifest.json').read_text())['version']
    except (OSError, ValueError, KeyError): version = 'unknown'
    r.add('app', 'info', f'OmaPit {version}; Python {platform.python_version()}; {platform.system() or "unknown OS"} {platform.machine()}')
    if sys.version_info < (3, 9):
        r.add('app', 'fail', 'Python 3.9 or newer is required.', 'Install a newer Python 3 and run OmaPit with it.')
    missing = [f for f in INSTALL_FILES if not (ROOT / f).is_file()]
    where = _tilde(ROOT)
    if missing: r.add('install', 'warn', f'Install at {where} is missing: {", ".join(missing)}', 'Copy the whole project, including backend/ and assets/, or reinstall.')
    else: r.add('install', 'ok', f'Install files present at {where}')
    if (ROOT / 'preview' / 'dist' / 'client' / 'index.html').is_file():
        r.add('browser', 'ok', 'Browser bundle is built (preview/dist/client).')
    else:
        r.add('browser', 'info', 'Browser bundle is not built. Only needed for the browser preview.', 'Run npm ci && npm run build in preview/.')

def _packages(r):
    for module, purpose in (('bleak', 'Bluetooth scanning'), ('paho', 'MQTT bridge')):
        if importlib.util.find_spec(module): r.add('packages', 'ok', f'{module} installed ({purpose}).')
        else: r.add('packages', 'info', f'{module} not installed. Only needed for {purpose}; manual entry works without it.',
                    'See README.md for the optional virtual environment.')

def _configuration(r):
    present = [name for name in ('OMAPIT_DB', 'OMAPIT_TOKEN', 'OMAPIT_HA_TOKEN', 'OMAPIT_MQTT_USER', 'OMAPIT_NTFY_URL', 'OMAPIT_DESKTOP_NOTIFY') if os.environ.get(name)]
    r.add('config', 'info', 'Environment settings present: ' + (', '.join(present) if present else 'none') + ' (values not shown).')
    token = os.environ.get('OMAPIT_TOKEN')
    if token and len(token) < 32:
        r.add('config', 'warn', 'OMAPIT_TOKEN is shorter than 32 characters, so LAN/phone serving will refuse to start.', 'Generate a longer random token.')
    if os.environ.get('OMAPIT_DESKTOP_NOTIFY') not in (None, '', '1'):
        r.add('config', 'warn', 'OMAPIT_DESKTOP_NOTIFY is set but not to 1, so desktop notifications are off.')

def _adapters(r):
    names = ', '.join(f"{a['id']} {a['version']}" for a in adapters.describe())
    r.add('adapters', 'ok', f'Device adapters: {names}')
    issues = compatibility.problems(compatibility.load(), compatibility.app_version())
    if issues: r.add('adapters', 'warn', f'Compatibility manifest has {len(issues)} problem(s): ' + issues[0], 'Run python3 backend/compatibility.py.')
    else: r.add('adapters', 'ok', 'Compatibility manifest is valid. See COMPATIBILITY.md.')

def _scalar(db, sql, args=()):
    try:
        row = db.execute(sql, args).fetchone()
        return row[0] if row else None
    except sqlite3.Error: return None

def _store(r, path, origin):
    shown = _tilde(path)
    if not path.exists():
        r.add('store', 'info', f'No cook store yet at {shown} ({origin}). It is created on first launch.')
        return
    try:
        db = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=2)
        db.row_factory = sqlite3.Row
        check = db.execute('PRAGMA quick_check').fetchone()[0]
    except sqlite3.Error as error:
        r.add('store', 'fail', f'Cannot read the cook store at {shown}: {error}', 'Check file permissions. If it is damaged, restore a backup; see TROUBLESHOOTING.md.')
        return
    try:
        size = path.stat().st_size / 1e6
        if check != 'ok': r.add('store', 'fail', f'Cook store at {shown} failed its integrity check.', 'Stop OmaPit and restore a backup; see TROUBLESHOOTING.md.')
        else: r.add('store', 'ok', f'Cook store at {shown} ({origin}, {size:.1f} MB) passed its integrity check.')
        _schema(r, db)
        _contents(r, db)
        backups = sorted(p.name for p in path.parent.glob(path.name + '.*.bak'))
        r.add('store', 'info', 'Migration backups: ' + (', '.join(backups) if backups else 'none'))
    finally:
        db.close()

def _schema(r, db):
    device_schema = _scalar(db, 'PRAGMA user_version') or 0
    workbench = _scalar(db, "SELECT value FROM settings WHERE key='workbench_schema'")
    if device_schema > SUPPORTED_DEVICE_SCHEMA or (workbench is not None and workbench != SUPPORTED_WORKBENCH):
        r.add('store', 'fail', 'The cook store was created by a newer OmaPit version.', 'Update OmaPit. Do not downgrade a newer store in place.')
    elif device_schema < SUPPORTED_DEVICE_SCHEMA or workbench is None:
        r.add('store', 'warn', 'The cook store predates this version and will be migrated on next launch. A backup is made first.')
    else:
        r.add('store', 'ok', f'Schema is current (devices {device_schema}, workbench {workbench}).')

def _contents(r, db):
    now = time.time()
    cooks = _scalar(db, 'SELECT COUNT(*) FROM cooks') or 0
    active = _scalar(db, 'SELECT COUNT(*) FROM cooks WHERE finished IS NULL') or 0
    r.add('cooks', 'info', f'{cooks} cook(s) stored, {active} active.')
    known = _scalar(db, 'SELECT COUNT(*) FROM devices WHERE source IN (?,?)', ('ble', 'bridge')) or 0
    unsupported = _scalar(db, 'SELECT COUNT(*) FROM devices WHERE error IS NOT NULL') or 0
    last = _scalar(db, "SELECT MAX(c.at) FROM channels c JOIN devices d ON d.id=c.device WHERE d.source IN ('ble','bridge') AND c.quality='valid'")
    if not known: r.add('devices', 'info', 'No live devices seen yet. Manual entry needs none.')
    else:
        fresh = last is not None and now - last <= devices.STALE_SECONDS
        detail = f'{known} live device(s) seen; last valid reading {_age(now - last) if last else "never"}.'
        r.add('devices', 'ok' if fresh or not active else 'warn', detail,
              None if fresh or not active else 'Readings stop after 30 s without packets. Move the receiver closer, wake the probe or rescan.')
    if unsupported: r.add('devices', 'warn', f'{unsupported} device(s) sent a format this version cannot decode.', 'See COMPATIBILITY.md and ADAPTERS.md.')
    selected = _scalar(db, 'SELECT d.device FROM cook_devices d JOIN cooks c ON c.id=d.cook WHERE c.finished IS NULL')
    if active: r.add('devices', 'info', 'Active cook is recording a live probe.' if selected else 'Active cook uses manual or demo readings.')
    try: scanner = devices.scanner_state(db)
    except (sqlite3.Error, ValueError): scanner = {'status': 'unknown'}
    if scanner.get('status') in ('error', 'stopped'):
        r.add('bluetooth', 'warn', 'Last Bluetooth scan: ' + str(scanner.get('error') or scanner['status']), 'See "Bluetooth scanning" in TROUBLESHOOTING.md.')
    else: r.add('bluetooth', 'info', f"Bluetooth scanner is {scanner.get('status', 'idle')}.")
    heartbeat = _scalar(db, "SELECT value FROM settings WHERE key='service_heartbeat'")
    try: beat = json.loads(heartbeat) if heartbeat else {}
    except ValueError: beat = {}
    at = beat.get('at') if isinstance(beat.get('at'), (int, float)) else None
    if at is not None and 0 <= now - at <= MONITOR_FRESH_SECONDS:
        r.add('alarms', 'ok', f"Alarm {beat.get('mode', 'service')} is running.")
    else:
        rules = _scalar(db, 'SELECT COUNT(*) FROM alarm_rules r JOIN cooks c ON c.id=r.cook WHERE r.enabled AND c.finished IS NULL') or 0
        seen = f'last seen {_age(now - at)}' if at is not None else 'never seen'
        r.add('alarms', 'warn' if rules else 'info', f'No alarm monitor running ({seen}); {rules} enabled alarm rule(s) on active cooks.',
              'Alarms are evaluated only while the companion server or --monitor runs. See packaging/omapit-monitor.service.' if rules else None)

def report(db_path=None):
    r = Report()
    origin = 'from --db' if db_path else 'from OMAPIT_DB' if os.environ.get('OMAPIT_DB') else 'default location'
    _environment(r); _packages(r); _configuration(r); _adapters(r); _store(r, store_path(db_path), origin)
    return r

def render(r):
    marks = {'ok': 'ok  ', 'info': 'info', 'warn': 'WARN', 'fail': 'FAIL'}
    lines = ['OmaPit diagnostics (read-only; review before sharing)', '']
    for c in r.checks:
        lines.append(f"[{marks[c['status']]}] {c['area']:<9} {c['message']}")
        if c.get('hint'): lines.append(f"{'':17}→ {c['hint']}")
    problems = sum(c['status'] in ('warn', 'fail') for c in r.checks)
    lines += ['', 'No problems found.' if not problems else f'{problems} item(s) need attention. See TROUBLESHOOTING.md.']
    return '\n'.join(lines)

def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only OmaPit troubleshooting report.')
    parser.add_argument('--db', help='Cook store to inspect (default: OMAPIT_DB or the standard location)')
    parser.add_argument('--json', action='store_true', help='Print machine-readable JSON')
    args = parser.parse_args(argv)
    r = report(args.db)
    print(json.dumps({'checks': r.checks, 'failed': r.failed}, indent=2) if args.json else render(r))
    return 1 if r.failed else 0

if __name__ == '__main__':
    sys.exit(main())
