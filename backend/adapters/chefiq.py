"""Dependency-free CHEF iQ advertisement decoder.

Packet layout adapted from Invader444/chefiq-ble (MIT, see CHEFIQ-LICENSE.txt).
https://github.com/Invader444/chefiq-ble/blob/master/src/chefiq_ble/parser.py
CQ60 5.0.0 is the upstream verified anchor. Other supported layouts are
experimental. Future major versions are rejected rather than guessed.
"""
import struct

MANUFACTURER_ID = 0x05CD
ADAPTER_VERSION = '0.2.0'

def decode(payload):
    if not isinstance(payload, bytes) or not 2 <= len(payload) <= 18:
        raise ValueError('Not a CHEF iQ probe payload (2–18 bytes required).')
    packet = payload[0] & 15
    version = (payload[1] >> 4, payload[1] & 15, payload[0] >> 4)
    if packet not in (0, 1, 3): raise ValueError('Unsupported packet type.')
    if version[0] > 5: raise ValueError('Unsupported protocol version.')
    fmt = 'v3' if version[0] >= 3 else 'v2' if version[0] == 2 else 'legacy'
    channels = {}
    def temperature(role, offset):
        if offset + 2 > len(payload): return
        value = struct.unpack_from('<h', payload, offset)[0] / 10
        # Invalid sentinel clears a channel; never leave a stale valid value fresh.
        channels[role] = value if -40 <= value <= 600 else None
    def battery(offset):
        channels['battery'] = payload[offset] if payload[offset] <= 100 else None
    if packet == 1:
        minimum = 6 if fmt == 'v3' else 14
        if len(payload) < minimum: raise ValueError('Truncated temperature packet.')
        if fmt == 'v3':
            temperature('ambient', 2); temperature('food', 4)
            for i in range(4): temperature('tip'+str(i+1), 6+i*2)
        elif fmt == 'v2':
            battery(2); temperature('ambient', 4); temperature('food', 6)
            for i in range(3): temperature('tip'+str(i+1), 8+i*2)
        else:
            battery(8); temperature('food', 10); temperature('ambient', 12)
    elif packet == 3:
        if len(payload) < 8: raise ValueError('Truncated status packet.')
        if fmt == 'v3':
            if len(payload) < 10: raise ValueError('Truncated V3 status packet.')
            battery(8)
    return {'protocol': '.'.join(map(str, version)), 'format': fmt,
            'evidence': 'upstream-verified' if version == (5,0,0) else 'experimental',
            'channels': channels, 'adapter': 'chefiq', 'adapter_version': ADAPTER_VERSION}
