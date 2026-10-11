"""Load the native QML plugin offscreen and fail on any runtime warning.

Quickshell and Omarchy's qs.Commons exist only on Omarchy, so tests/qml/stubs
stands in for the few types OmaPit uses. The stubbed Process sends each command
to a small local helper, which runs the real backend against a temporary store.
This catches binding, reference and type errors in OmaPit's own QML; it cannot
show that the stand-ins match Omarchy, so it is not native acceptance.

Needs qmltestrunner with the QtQuick, Controls, Layouts and QtTest QML modules
(Debian/Ubuntu: qml6-module-qttest and friends). Set QMLTESTRUNNER to override
the path. The test is skipped when the runner is missing, unless
OMAPIT_REQUIRE_QML is set, as in CI.
"""
import json, os, shutil, subprocess, sys, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / 'backend' / 'omapit.py'
# Actions the panel may send that must never run here: scanning starts Bluetooth.
REFUSED = {'scan', 'select_device'}

def runner():
    for candidate in (os.environ.get('QMLTESTRUNNER'), '/usr/lib/qt6/bin/qmltestrunner', shutil.which('qmltestrunner6'), shutil.which('qmltestrunner')):
        if candidate and Path(candidate).is_file(): return candidate
    return None

class Helper(BaseHTTPRequestHandler):
    db = None
    commands = []

    def log_message(self, *args): pass

    def reply(self, status, body):
        data = body.encode()
        self.send_response(status); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path != '/env': return self.reply(404, 'unknown path')
        name = parse_qs(url.query).get('name', [''])[0]
        self.reply(200, sys.executable if name == 'OMAPIT_PYTHON' else '')

    def do_POST(self):
        if self.path != '/run': return self.reply(404, 'unknown path')
        command = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if len(command) != 4 or Path(command[1]).resolve() != BACKEND or command[2] in REFUSED:
            return self.reply(403, 'only backend actions are run: ' + json.dumps(command[1:3]))
        Helper.commands.append(command[2])
        done = subprocess.run([sys.executable, str(BACKEND), '--db', self.db, command[2], command[3]], capture_output=True, text=True, timeout=30)
        self.reply(200, json.dumps({'code': done.returncode, 'stdout': done.stdout, 'stderr': done.stderr}))

@unittest.skipUnless(runner() or os.environ.get('OMAPIT_REQUIRE_QML'), 'qmltestrunner not installed')
class QmlRuntimeTest(unittest.TestCase):
    def test_plugin_loads_and_runs_without_qml_warnings(self):
        self.assertTrue(runner(), 'qmltestrunner not found; set QMLTESTRUNNER')
        with tempfile.TemporaryDirectory() as tmp:
            Helper.db = str(Path(tmp) / 'cooks.sqlite3'); Helper.commands = []
            server = ThreadingHTTPServer(('127.0.0.1', 0), Helper)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                stubs = Path(tmp) / 'stubs'
                shutil.copytree(ROOT / 'tests' / 'qml' / 'stubs', stubs)
                (stubs / 'Quickshell' / 'Io' / 'endpoint.js').write_text(f'var url = "http://127.0.0.1:{server.server_port}"\n')
                env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software', no_proxy='127.0.0.1,localhost', NO_PROXY='127.0.0.1,localhost')
                run = subprocess.run([runner(), '-import', str(stubs), '-input', str(ROOT / 'tests' / 'qml' / 'tst_plugin.qml')],
                                     capture_output=True, text=True, env=env, cwd=ROOT, timeout=300)
            finally:
                server.shutdown(); server.server_close()
        output = run.stdout + run.stderr
        self.assertEqual(run.returncode, 0, output)
        self.assertIn('0 failed', output)
        # The backend really ran the panel's actions, not just snapshots.
        for action in ('create', 'reading', 'note', 'unit', 'finish', 'demo', 'history'):
            self.assertIn(action, Helper.commands)

if __name__ == '__main__':
    unittest.main()
