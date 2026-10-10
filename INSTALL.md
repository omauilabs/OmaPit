# Install, update and roll back

The Omarchy plugin itself has not yet been accepted on a real Omarchy install. The installer below has been tested against a temporary home folder only. Please report what happens on your machine; see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Install

You need a recent Omarchy shell with plugin support and Python 3.9 or newer. From a checkout of this repository:

```sh
python3 packaging/install.py --dry-run   # see what it will do
python3 packaging/install.py
omarchy-shell shell rescanPlugins
omarchy plugin enable local.omapit
```

The installer copies the plugin, which is `manifest.json`, the QML files, `backend/`, `assets/` and the licence and help documents, to `~/.config/omarchy/plugins/local.omapit` (it follows `XDG_CONFIG_HOME`). Use `--target` to choose another folder. It writes `.omapit-install.json` there, listing the version and a checksum of every installed file.

It refuses to touch a folder it didn't install, including one you copied by hand or a symlink to your checkout. Move that folder aside first.

Your cook store is separate from the plugin: `~/.local/share/omapit/cooks.sqlite3`, or `OMAPIT_DB` if set. Installing, updating and uninstalling never touch it.

Check the result with `python3 ~/.config/omarchy/plugins/local.omapit/backend/diagnose.py`.

## Bluetooth (optional)

Manual entry works without any extra packages. To read a Bluetooth probe, create a virtual environment with Bleak and point the plugin at its Python:

```sh
python3 -m venv ~/.local/share/omapit/venv
~/.local/share/omapit/venv/bin/pip install -r ~/.config/omarchy/plugins/local.omapit/backend/requirements-ble.txt
```

Then set `OMAPIT_PYTHON=$HOME/.local/share/omapit/venv/bin/python` in the environment Omarchy's shell starts with, and restart the shell. The virtual environment lives outside the plugin folder, so updates don't remove it.

## Background alarms (optional)

Alarms are checked only while the companion server or monitor is running. To run one in the background, copy `packaging/omapit-monitor.service` to `~/.config/systemd/user/`, replace the `/ABSOLUTE/...` placeholders with the plugin folder and your Python, then run `systemctl --user enable --now omapit-monitor`. Use `omapit-companion.service` instead if you also want the browser or phone view.

## Update

Pull or download the new version, then run the same command:

```sh
python3 packaging/install.py --dry-run
python3 packaging/install.py
```

Before replacing anything it moves the installed version to `~/.local/share/omapit/plugin-backups/<date>-<version>/`. That folder is outside Omarchy's plugin folder, so Omarchy can't load a backup as a second copy. Files that a new version no longer ships are removed with the old copy.

The installer stops, changing nothing, when:

- **You edited installed files.** It lists them. Keep your changes in a checkout instead (see [CUSTOMIZATION.md](CUSTOMIZATION.md)), or re-run with `--force`; the edited copy stays in the backup.
- **The source is older than the installed version.** See below.

Restart Omarchy's shell after an update. The first launch of a new version may migrate your cook store; it saves a copy beside the store first, such as `cooks.sqlite3.before-workbench-v1.bak`.

Backups accumulate; delete old folders in `plugin-backups` when you no longer need them.

## Roll back

A newer version may have migrated your cook store, and an older version can't open a migrated store. Roll back the store together with the plugin:

1. Stop OmaPit: disable the plugin, and stop `omapit-monitor` or `omapit-companion` if you run them.
2. Copy your current `cooks.sqlite3` somewhere safe. It holds everything you recorded since the update.
3. If `diagnose` reports that the store was created by a newer version, replace `cooks.sqlite3` with the `*.bak` file the update created. Cooks recorded after that update are not in it; keep the copy from step 2.
4. Install the older version from its checkout with `python3 packaging/install.py --allow-downgrade`, or move its folder back from `plugin-backups` into place.
5. Run `python3 backend/diagnose.py` and confirm the store reports a current schema, then re-enable the plugin.

Never open a newer store with an older version in place.

## Uninstall

Disable the plugin in Omarchy, then remove its folder:

```sh
rm -r ~/.config/omarchy/plugins/local.omapit
omarchy-shell shell rescanPlugins
```

Your cook store, Bluetooth environment and plugin backups stay in `~/.local/share/omapit/`. Delete that folder only if you also want to remove your cook journal.
