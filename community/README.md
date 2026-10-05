# Agent-assisted hardware benchmarks

Goal: gather reproducible model-specific compatibility evidence without requiring maintainers to buy every thermometer. No scanning, submission, scheduler or repository is enabled by this tool automatically.

## Report contract

Schema version 1 (benchmark.schema.json, plus the stricter CLI validator) contains only:

- OmaPit version, model/manufacturer, firmware/protocol, adapter version and transport (short plain labels).
- OS family, architecture and Python version; no hostname, username, filesystem path or exact OS build.
- Total stored channel samples, valid food/ambient/battery sample counts, total duration and largest observed reception gap.
- Evidence type and explicit pass/fail/not-run outcomes for physical checks.

No temperature values, exact timestamps, device addresses, serials, raw packets, credentials, cook names/notes or photos are accepted as fields. Strict validation rejects unknown fields, address/UUID/email/path/URL patterns, malformed counts, and physical pass claims from replay reports. Inspect free-text model/version fields: pattern checks cannot identify every possible secret or serial.

`live-observation` means stored live samples exist. It does not mean accuracy or reliability passed. Counts include individual channel samples; gaps use distinct reception timestamps across channels, not radio-packet counts. Duration and largest gap do not measure usable range, packet-loss rate, clock accuracy or radio latency. A report includes all stored samples for the selected device; use a separate benchmark database for clean session measurements. Multiple scans separated by downtime can produce a large gap.

Physical checks are owner attestations; they need an actual observed test. Leave checks not-run until completed. Real-capture replay needs provenance reviewed separately; do not attach raw files to the issue. A collector-generated replay is conservatively labeled synthetic.

## Local preparation

From the OmaPit directory:

```sh
python3 community/benchmark.py template --model CQ60 --out work/benchmark.json
python3 community/benchmark.py collect --db /path/to/isolated.sqlite3 --device SELECTED_LOCAL_ID --out work/benchmark.json
python3 community/benchmark.py validate work/benchmark.json
python3 community/benchmark.py review work/benchmark.json --out work/benchmark-preview.md
```

`collect` reads an existing database in read-only mode. It does not run Bluetooth, copy the selected ID into the report or modify a cook. Choose the device locally; never publish the ID. Edit manufacturer/model/version labels and completed check outcomes before validation. Do not use the cooking database to conduct destructive tests.

## Owner opt-in, then automatic submission

The human owner must authorize the specific destination and public report fields above. Once the public project repository exists, substitute its actual owner/repository. Never use a guessed repository.

```sh
python3 community/benchmark.py configure --repo OWNER/REPOSITORY --config work/benchmark-sharing.json --allow-auto-submit
python3 community/benchmark.py submit work/benchmark.json --config work/benchmark-sharing.json
python3 community/benchmark.py disable --config work/benchmark-sharing.json
```

Configure records consent locally and sends nothing. Submission uses an already installed/authenticated GitHub CLI (`gh`), creates a reviewable public issue, and checks for the report fingerprint among open and closed issues first. Never paste GitHub tokens into reports. Destination configuration is separate from the report, so submitted content cannot redirect future uploads. Revocation stops later submissions; it does not remove an already public issue. A project maintainer should configure issue routing/moderation before enabling community use.

After opt-in, an owner's agent may run collect → validate → submit after an authorized hardware session without asking again for every report within that scope. There is no daemon or recurring task installed. Scheduling is a separate explicit owner choice. Reports with different observations get different fingerprints. Concurrent submissions and GitHub search indexing can still produce duplicates; maintainers should deduplicate before reviewing.

## Review before compatibility promotion

Review exact model/protocol/adapter/transport and separate live reception from accuracy, ambient, battery, wake/dock, reconnect, restart, recording, alarms, multi-probe and long-cook checks. A user report is evidence, not an automatic compatibility certification. Require reproduction for surprising results. Never promote an entire brand or firmware family from one unit. Keep capture redistribution permission and any independently reviewed fixtures separate from this aggregate report.

Automated coverage: `python3 -m unittest discover -s community -p 'test_*.py'`. Network submission is tested with mocked GitHub responses, not actual public issues.
