# OmaPit integrations — 0.3.0

Everything is opt-in. No hardware scans, Home Assistant connections, MQTT subscriptions or external messages were run automatically while developing this release; the MQTT tests use a throwaway broker on the test machine only. Contract tests and mock notification delivery do not establish hardware compatibility.

## Bridge schema v1

Send to `POST /api/bridge_ingest` with the same-origin header and access token if configured, or ingest locally through `backend/bridges.py --db JOURNAL json packet.json`.

```json
{
  "schema": 1,
  "source": "json",
  "device": "kettle-probe-1",
  "name": "Kettle probe",
  "sample_at": 1791097200,
  "retained": false,
  "channels": {
    "food": {"value": 72.5, "unit": "C"},
    "ambient": {"value": 250, "unit": "F"},
    "battery": {"value": 80, "unit": "%"}
  }
}
```

Replace the example timestamp with the actual sample's Unix timestamp. Sources: `json`, `mqtt`, `home-assistant`. Roles: `food`, `ambient`, `battery`. Omit missing channels; use null with a known unit to mark an invalid reading. Names/IDs must remain stable. Received temperatures are normalized to Celsius channels; food journal readings use Fahrenheit. Arrival/poll time never replaces the source sample timestamp. Each channel rejects duplicates and out-of-order updates independently.

Samples older than 30 seconds, more than five seconds in the future or marked retained are rejected as live data. The sample publisher must provide a trustworthy timestamp; this contract cannot detect a publisher falsely relabeling an old value. Map bridge devices to individual foods in Meal. Bridge devices cannot use the legacy single-CHEF-iQ selection button.

## Home Assistant

Set `OMAPIT_HA_TOKEN` in the worker's environment, not in the journal or command line. Poll one entity with:

```sh
python3 backend/bridges.py --db JOURNAL ha --url http://YOUR_HA_HOST:8123 --entity sensor.food_temperature --role food
```

Each entity becomes its own bridge device. Map it to the appropriate food. Polling defaults to 15 seconds; failures never synthesize readings. The worker preserves `last_reported` when available, otherwise `last_updated`. Integrations that only update timestamps when a value changes may appear stale at a stable temperature; a timestamp-aware publisher is preferable to pretending every HTTP poll is a new measurement. Unavailable states invalidate a channel only when they include a recognized unit and fresh timestamp; otherwise the old channel ages out. Cloud-backed HA integrations remain cloud-dependent.

Reference: [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest/).

## MQTT

Install optional `backend/requirements-bridge.txt` in the app environment. Publish schema-v1 JSON on a dedicated exact topic. The subscriber refuses wildcard topics and ignores retained payloads even if the JSON claims otherwise.

```sh
python3 backend/bridges.py --db JOURNAL mqtt --host YOUR_BROKER --topic omapit/temperatures --tls --port 8883
```

Optional credentials: `OMAPIT_MQTT_USER`, `OMAPIT_MQTT_PASSWORD`. TLS verifies certificates using the system trust store; for a broker with its own certificate authority, set `SSL_CERT_FILE` to that CA file. `tests/test_mqtt_broker.py` exercises the bridge against a real local Mosquitto broker, including retained and stale samples, reconnection, password auth and TLS. It runs when `mosquitto` and paho-mqtt are installed. No real thermometer publisher has been tested. Reference: [Paho Python client](https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html).

## Phone companion

The same responsive UI can run on a phone. Default serving remains loopback-only. LAN serving requires `OMAPIT_TOKEN` of at least 32 characters and `--public-host` matching the exact host used by the phone:

```sh
python3 backend/omapit.py --db JOURNAL --static preview/dist/client --serve 4176 --listen 0.0.0.0 --public-host YOUR_LAN_IP
```

Configure the token securely in the service environment first; then enter it in the companion's access form. The token is scoped to the entire journal, including edits and exports, and stays in that tab's session storage. Static app assets are public; all API access requires the token when configured. Host and Origin checks reject unexpected origins. There is no public deployment, account service or automatic port forwarding.

Built-in HTTP is not encrypted. Use it only on a trusted private network; for secure access use a TLS-capable private tunnel/reverse proxy with `--public-origin https://YOUR_PRIVATE_HOST` and a configured token. The proxy must preserve that Host and Origin; the app then permits only that explicit HTTPS origin. Credential-bearing outbound clients refuse redirects. HTTPS browser notification support depends on the browser/platform. Mobile LAN access and background notification delivery have not been tested on a real phone. A phone webpage is not a push service.

## Alerts and notifications

The HTTP service evaluates alarms every second independently of an open browser. CLI/native snapshots also evaluate alarms. For native monitoring independent of snapshot frequency:

```sh
python3 backend/omapit.py --monitor
```

A systemd user-service template is in `packaging/omapit-monitor.service`; edit its absolute paths and environment before installation. It has not been enabled here. The HTTP server already runs a monitor, so avoid running both unless necessary.

- Browser: explicit notification permission; test button. Requires an open connected app and platform support.
- Linux desktop: set `OMAPIT_DESKTOP_NOTIFY=1` for the monitor/server. Uses `notify-send`; native delivery needs Linux acceptance.
- Phone push: set `OMAPIT_NTFY_URL` to your HTTPS topic and optionally `OMAPIT_NTFY_TOKEN`. Subscribe your phone to that topic using ntfy. Self-hosting is supported through the configured endpoint. Nothing is sent until configured and an alarm actually fires.

Delivery health records sent/failed attempts. Up to three attempts per notice, with ten-second spacing; notices older than a minute are not newly delivered. A crash during an in-flight attempt may leave it `sending`; later alarm repeats provide another notice. Delivery is best-effort, not exactly-once or a safety guarantee. An acknowledged/snoozed/resolved episode is not newly sent. ntfy/provider delivery and phone sound behavior remain unverified. Keep topics/access credentials private. Reference: [ntfy publishing](https://docs.ntfy.sh/publish/).

High/low alarms use a two-degree Fahrenheit recovery margin by default to resist jitter; `hysteresis` is configurable in the command payload. Condition buffers and repeat intervals are configurable. Food alarms follow that food's current probe mapping; finishing a food resolves its alarms. Replay/demo samples never trigger live temperature alarms.

## Portable backup and restore

Use Recipes → Back up journal, then restore into an empty journal. Backups contain photos, device identities and personal notes; inspect before sharing. Existing records are never overwritten. Restoring preserves history but pauses rules, clears live mappings, marks channels historical and resets scanner state. Re-enable desired rules and map devices intentionally.

For backups larger than the 16 MiB browser request limit:

```sh
python3 backend/omapit.py --db JOURNAL backup > journal-backup.json
python3 backend/omapit.py --db EMPTY_JOURNAL --payload-file journal-backup.json restore
```

Native/browser extension migration creates `JOURNAL.before-workbench-v1.bak` when first upgrading. For rollback, stop workers, preserve the current database and restore that backup while using the previous app build. The backup predates new features. Do not downgrade an extended database in place.
