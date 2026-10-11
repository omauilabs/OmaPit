# Omarchy acceptance checklist

The first run of the native plugin on a real Omarchy machine. Nothing here has been tested on Omarchy yet, so expect to find problems; each one you record is useful. Plan about 30 minutes, plus 15 if you include the optional Bluetooth part.

Mark every check **pass**, **fail** or **not run**. Leave a check as not run rather than guessing. Copy the results block at the end into an issue, or paste it to whoever is helping you.

## Before you start

- Back up `~/.local/share/omapit/` if it exists. It holds your cook journal.
- Use a checkout of the version you are testing: `git log -1 --oneline` gives its commit for the report.
- You need Python 3.9 or newer (`python3 --version`).
- Nothing in this checklist scans for Bluetooth devices until the optional section, and only if you choose to run it.

## 1. Install

| # | Step | Expected |
|---|---|---|
| 1.1 | `python3 packaging/install.py --dry-run` | Says it will install to `~/.config/omarchy/plugins/local.omapit`; changes nothing. |
| 1.2 | `python3 packaging/install.py` | Installs and prints the two Omarchy commands to run next. |
| 1.3 | `python3 ~/.config/omarchy/plugins/local.omapit/backend/diagnose.py` | No `FAIL` lines. `install` and `adapters` are `ok`. |
| 1.4 | `omarchy-shell shell rescanPlugins` then `omarchy plugin enable local.omapit` | Both commands succeed. |

## 2. Bar widget and panel

| # | Check | Expected |
|---|---|---|
| 2.1 | Widget appears | An OmaPit item shows in the right section of the bar. |
| 2.2 | Widget theme | It uses your Omarchy foreground colour, not a fixed colour. |
| 2.3 | Open the panel | Clicking the widget opens the cook journal panel. |
| 2.4 | Close the panel | Clicking the widget again, or closing the window, dismisses it. |
| 2.5 | Window size | The panel fits on screen; nothing is cut off. Try a smaller window if you can resize it. |
| 2.6 | Empty state | With no cooks, the panel offers to start one or explore a demo, without errors. |

## 3. Using the panel

Use a test cook you are happy to delete afterwards.

| # | Check | Expected |
|---|---|---|
| 3.1 | Start a cook | A dialog opens, accepts a name and target time, and the cook appears. |
| 3.2 | Log a manual reading | The reading appears in the panel and its chart. |
| 3.3 | Change units | °F/°C switches, and existing readings convert. |
| 3.4 | Add a note | The note appears in the cook's events. |
| 3.5 | Meal workbench | Foods, alarms, timeline and recipes sections open without errors. |
| 3.6 | Finish the cook | It moves to history and is no longer active. |

## 4. Keyboard and theme

| # | Check | Expected |
|---|---|---|
| 4.1 | Keyboard only | Tab reaches every button and field in the panel, and the focused item is visible. |
| 4.2 | Dialogs by keyboard | Dialogs can be filled in and submitted or cancelled without the mouse. |
| 4.3 | Theme switch | Change Omarchy's theme while the panel is open: colours follow, text stays readable, amber and blue keep their temperature meanings. |

## 5. Persistence and restart

| # | Check | Expected |
|---|---|---|
| 5.1 | Restart the shell or log out and in | The plugin loads again, and the test cook's readings and notes are still there. |
| 5.2 | Store location | `python3 ~/.config/omarchy/plugins/local.omapit/backend/diagnose.py` reports the store, schema current, and the cook count you expect. |
| 5.3 | Browser and panel agree (optional) | Run the browser preview against the same store, as in README.md; it shows the same cooks. |

## 6. Update and roll back

| # | Step | Expected |
|---|---|---|
| 6.1 | Run `python3 packaging/install.py` again | It updates and saves the previous version under `~/.local/share/omapit/plugin-backups/`. |
| 6.2 | After rescanning, check Omarchy's plugin list | Only one OmaPit appears; the backup is not loaded. |
| 6.3 | Edit any installed QML file, then run the installer again | It refuses and lists the edited file. Undo the edit or re-run with `--force`. |

## 7. Optional: Bluetooth on Linux

Only if you want to test your CHEF iQ probe now. This is the first Linux/BlueZ test of the adapter.

| # | Check | Expected |
|---|---|---|
| 7.1 | Set up Bleak as in INSTALL.md, set `OMAPIT_PYTHON`, restart the shell | `diagnose.py` run with that Python shows `bleak installed`. |
| 7.2 | Devices → scan, with the probe out of its charger | The probe appears with a model and protocol, or as unsupported. |
| 7.3 | Food reading | Matches the CHEF iQ app within the probe's stated accuracy. |
| 7.4 | Stale warning | Put the probe back in its charger; within about 30 seconds the reading shows as stale. |

## If something fails

- Note what you did and what you saw. Screenshots help.
- Copy any QML or Python errors from the shell's log output.
- Run `python3 ~/.config/omarchy/plugins/local.omapit/backend/diagnose.py` and include its output after reading it.
- To remove the plugin, follow "Uninstall" in INSTALL.md. Your cook store is not touched.

## Results

```text
OmaPit commit:
Omarchy version:
Date:

1.1 1.2 1.3 1.4      :
2.1 2.2 2.3 2.4 2.5 2.6:
3.1 3.2 3.3 3.4 3.5 3.6:
4.1 4.2 4.3          :
5.1 5.2 5.3          :
6.1 6.2 6.3          :
7.1 7.2 7.3 7.4      :   (optional)

Failures and notes:
```
