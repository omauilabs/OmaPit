#!/usr/bin/env python3
"""Install or update the OmaPit Omarchy plugin from this source tree.

  python3 packaging/install.py              install, or update an earlier install
  python3 packaging/install.py --dry-run    show what would change
  python3 packaging/install.py --force      update even if installed files were edited
  python3 packaging/install.py --allow-downgrade

Installs to ${XDG_CONFIG_HOME:-~/.config}/omarchy/plugins/local.omapit.
It never touches your cook store. It refuses to replace a folder it did not
install. Before an update it moves the previous version to
${XDG_DATA_HOME:-~/.local/share}/omapit/plugin-backups/, outside the plugins
folder so Omarchy cannot load it as a second copy. See INSTALL.md.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent
PLUGIN_ID = 'local.omapit'
RECORD = '.omapit-install.json'
TREES = ('backend', 'assets')
FILES = ('manifest.json', 'LICENSE', 'ASSET-LICENSES.md', 'COMPATIBILITY.md', 'TROUBLESHOOTING.md')

def config_home(): return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
def data_home(): return Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share')
def default_target(): return config_home() / 'omarchy' / 'plugins' / PLUGIN_ID
def backup_root(): return data_home() / 'omapit' / 'plugin-backups'

def version_of(root):
    return json.loads((Path(root) / 'manifest.json').read_text())['version']

def _key(version):
    try: return tuple(int(p) for p in version.split('.'))
    except (AttributeError, ValueError): return None

def payload(source=SOURCE):
    """Relative paths of every file the plugin needs."""
    source = Path(source); files = {Path(f) for f in FILES if (source / f).is_file()}
    files |= {p.relative_to(source) for p in source.glob('*.qml')}
    for tree in TREES:
        for p in (source / tree).rglob('*'):
            parts = p.relative_to(source).parts
            if p.is_file() and '__pycache__' not in parts and p.suffix != '.pyc' and not any(x.startswith('.') for x in parts):
                files.add(p.relative_to(source))
    try:  # acceptance documents the compatibility manifest links to
        for row in json.loads((source / 'assets' / 'compatibility.json').read_text()).get('devices', []):
            if row.get('acceptance') and (source / row['acceptance']).is_file(): files.add(Path(row['acceptance']))
    except (OSError, ValueError): pass
    missing = [f for f in ('manifest.json', 'Main.qml', 'Widget.qml', 'backend/omapit.py') if Path(f) not in files]
    if missing: raise SystemExit('Source tree is incomplete; missing ' + ', '.join(missing))
    return sorted(files)

def _sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _commit(source):
    try:
        out = subprocess.run(['git', '-C', str(source), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, timeout=5)
        dirty = subprocess.run(['git', '-C', str(source), 'status', '--porcelain'], capture_output=True, text=True, timeout=5).stdout.strip()
        return out.stdout.strip() + ('-modified' if dirty else '') if out.returncode == 0 else 'unknown'
    except (OSError, subprocess.SubprocessError): return 'unknown'

def edited_files(target):
    """Installed files changed since install, according to the install record."""
    record = json.loads((target / RECORD).read_text())
    return sorted(f for f, digest in record['files'].items() if not (target / f).is_file() or _sha(target / f) != digest)

def stage(source, files, into):
    into.mkdir(parents=True)
    for rel in files:
        (into / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, into / rel)
    record = {'plugin': PLUGIN_ID, 'version': version_of(source), 'source_commit': _commit(source),
              'installed_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'files': {str(f): _sha(into / f) for f in files}}
    (into / RECORD).write_text(json.dumps(record, indent=2) + '\n')

def install(source=SOURCE, target=None, *, dry_run=False, force=False, allow_downgrade=False, log=print):
    source, target = Path(source), Path(target or default_target())
    files, new = payload(source), version_of(source)
    updating = target.exists()
    if updating:
        if not (target / RECORD).is_file():
            raise SystemExit(f'{target} exists but was not installed by this script. Move it aside, then run the installer again. Nothing was changed.')
        old = json.loads((target / RECORD).read_text()).get('version', 'unknown')
        if _key(new) and _key(old) and _key(new) < _key(old) and not allow_downgrade:
            raise SystemExit(f'Installed {old} is newer than {new}. Your cook store may already use the newer format. Re-run with --allow-downgrade only if you have restored a matching store backup. Nothing was changed.')
        edited = edited_files(target)
        if edited and not force:
            raise SystemExit('Installed files were edited since install:\n  ' + '\n  '.join(edited) + '\nRe-run with --force to replace them; the edited copy is kept in the backup. Nothing was changed.')
        log(f'Updating {target}: {old} → {new} ({len(files)} files).')
    else:
        log(f'Installing OmaPit {new} to {target} ({len(files)} files).')
    if dry_run: log('Dry run: nothing was changed.'); return None
    staging_root = backup_root(); staging_root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    staged = staging_root / f'.staging-{stamp}-{os.getpid()}'
    try: stage(source, files, staged)
    except BaseException: shutil.rmtree(staged, ignore_errors=True); raise
    backup = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if updating:
            backup = staging_root / f'{stamp}-{old}'
            shutil.move(str(target), str(backup))
        shutil.move(str(staged), str(target))
    except BaseException:
        if backup and backup.exists() and not target.exists(): shutil.move(str(backup), str(target))
        shutil.rmtree(staged, ignore_errors=True)
        raise
    if backup: log(f'Previous version saved to {backup}')
    log('Next: omarchy-shell shell rescanPlugins && omarchy plugin enable local.omapit')
    return backup

def main(argv=None):
    p = argparse.ArgumentParser(description='Install or update the OmaPit Omarchy plugin.')
    p.add_argument('--target', help=f'Plugin folder (default: {default_target()})')
    p.add_argument('--dry-run', action='store_true', help='Show what would change without changing anything')
    p.add_argument('--force', action='store_true', help='Replace installed files that were edited since install')
    p.add_argument('--allow-downgrade', action='store_true', help='Install an older version over a newer one')
    a = p.parse_args(argv)
    install(target=a.target, dry_run=a.dry_run, force=a.force, allow_downgrade=a.allow_downgrade)
    return 0

if __name__ == '__main__':
    sys.exit(main())
