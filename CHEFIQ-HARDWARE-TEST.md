# CHEF iQ hand-warming test

Local test on October 5, 2026. Detected a real CQ60 advertising protocol 4.0.0 through macOS Bluetooth. Food temperature began at 25.1°C (77.2°F) and reached 33.0°C; all four tip channels rose during hand warming. No readings were mapped to the active demo cook.

Food reception and response to warming are verified. Ambient returned an invalid sensor value, and battery was unavailable. Accuracy against the manufacturer app, cooking performance, range, reconnection and alarms remain unverified.

Setup: Bleak in a dedicated Python virtual environment, with the local app servers restarted on that interpreter against the existing journal database. Linux/BlueZ reception has not been tested.
