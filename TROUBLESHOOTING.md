# Troubleshooting

Start with the diagnostics report. It is read-only: it never migrates or changes your cook store and never scans for devices.

```sh
python3 backend/omapit.py diagnose
python3 backend/diagnose.py --db PATH/TO/cooks.sqlite3   # a specific store
python3 backend/diagnose.py --json                       # machine-readable
```

Each line is marked `ok`, `info`, `WARN` or `FAIL`, with a hint where there is something to do. It exits with status 1 when something failed. The report shows counts, ages and statuses only: no cook names, notes, temperatures, device addresses or secret values. File paths can include your username, so read it before you share it.

Before you change anything below, stop OmaPit: close the panel, and stop `omapit-monitor` or `omapit-companion` if you run them as services. Copy your cook store somewhere safe first. It lives at `~/.local/share/omapit/cooks.sqlite3` unless `OMAPIT_DB` or `--db` says otherwise.

## Cook store

**"The cook store was created by a newer OmaPit version."** Your store has been opened by a newer build. Update OmaPit. Never downgrade a newer store in place.

**"The cook store predates this version and will be migrated."** This is expected after an update. On next launch OmaPit makes a backup beside the store, such as `cooks.sqlite3.before-devices-v1.bak` or `cooks.sqlite3.before-workbench-v1.bak`, and then migrates.

**The store fails its integrity check or cannot be read.** Check that your user owns the file and can read and write it. If it is damaged:

1. Stop every OmaPit process and move the damaged file aside. Don't delete it.
2. Restore your newest journal backup into an empty store. See "Portable backup and restore" in [INTEGRATIONS.md](INTEGRATIONS.md).
3. If you have no journal backup, copy the newest `*.bak` file to the store's filename. These backups were taken before a migration, so they don't contain anything recorded after that, and they need the OmaPit build that matches them.

## Bluetooth probes

**"bleak not installed".** Bluetooth is optional; manual entry never needs it. To scan, install it in a virtual environment as described in [README.md](README.md), and start OmaPit with that environment's Python.

**"Bluetooth scan failed" or "Scanner stopped responding".** Check that Bluetooth is on and the service is running (`systemctl status bluetooth`, `bluetoothctl show`), then scan again from Devices. Scans stop after 60 seconds unless a cook is recording a probe.

**A probe shows as stale.** OmaPit marks readings stale after 30 seconds without a packet. Wake the probe or take it out of its dock, and move the computer's Bluetooth receiver closer. A direct Bluetooth connection does not get the range of the vendor's Wi-Fi hub. Whether OmaPit and the vendor app can read the probe at the same time hasn't been tested; if readings stop while the app is open, say so in your report.

**A device shows as unsupported.** It sent a format this version can't decode. OmaPit won't guess at unknown formats. Check [COMPATIBILITY.md](COMPATIBILITY.md). If you own the device, a short capture and report help add support; see [community/README.md](community/README.md) and [ADAPTERS.md](ADAPTERS.md).

**I can't select a probe for my cook.** Start a manual cook first; the demo cook can't record a probe. The probe must have been seen in the last 30 seconds, so scan again if needed. Replayed captures can never be selected.

## Alarms and notifications

**Alarms don't go off.** Alarms are checked only while the companion server (`--serve`) or the monitor (`--monitor`) is running. Diagnostics warns when you have enabled alarm rules and no monitor is running. To keep one running, edit and install `packaging/omapit-monitor.service`, or `packaging/omapit-companion.service` if you also use the browser or phone view.

**No desktop or phone notification.** Desktop notifications need `OMAPIT_DESKTOP_NOTIFY=1`, and ntfy needs `OMAPIT_NTFY_URL`, set in the service's environment. Delivery is best effort: check Alerts → delivery health. A notification being sent doesn't prove someone saw it.

## Browser and phone view

**Blank page or "File not found".** Build the browser bundle: `cd preview && npm ci && npm run build`. Diagnostics reports whether it is built.

**"Host rejected" (403).** Open the address the server was started for: `http://127.0.0.1:PORT` or `http://localhost:PORT`. For another device on your network, start the server with `--listen`, `--public-host` and an `OMAPIT_TOKEN` of at least 32 characters. See [INTEGRATIONS.md](INTEGRATIONS.md).

**"Enter your companion access token" (401).** The server has `OMAPIT_TOKEN` set. Enter the same token in the access form.

**The server won't start.** Another program may be using the port. Choose a different one with `--serve`.

## Omarchy panel

**The widget doesn't appear.** The native plugin hasn't yet been accepted on a real Omarchy install, so please report what you see. Check that the plugin folder contains `manifest.json`, the QML files, `backend/` and `assets/`. Running `python3 backend/diagnose.py` from inside that folder checks this. Then run `omarchy-shell shell rescanPlugins` and `omarchy plugin enable local.omapit`.

## Reporting a problem

Include the diagnostics report after reading it, what you did, what you expected and what happened. Never attach your cook store or a journal backup: they contain your notes, photos and device identities.
