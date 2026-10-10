"""Registry of direct-transport device adapters.

An adapter is a module that turns one vendor's raw transport payload into
normalized channels. It never touches the store, the network or Bluetooth;
devices.py owns transport, persistence and freshness. See ADAPTERS.md.

Required module attributes:
  ADAPTER_ID       short stable identifier, e.g. 'chefiq'
  ADAPTER_VERSION  bump whenever decoded output can change; compatibility
                   evidence is scoped to this version
  NAME             human-readable vendor/family name
  TRANSPORT        'ble-advertisement' (the only direct transport today)
  DEFAULT_NAME     device name used when the advertisement has none
  payload_from(manufacturer_data) -> bytes | None
                   pick this adapter's payload out of a BLE advertisement's
                   {company_id: bytes} map, or None if it is not ours
  decode(payload)  -> {'protocol', 'format', 'evidence', 'channels',
                   'adapter', 'adapter_version'}; raise ValueError for
                   unknown, truncated or future layouts instead of guessing
  model_from_name(name) -> str   model label, 'Unknown' when not identifiable
  redact(payload)  -> bytes      copy safe to write into a shareable capture
"""
from adapters import chefiq

TRANSPORTS = {'ble-advertisement'}
REQUIRED = ('ADAPTER_ID', 'ADAPTER_VERSION', 'NAME', 'TRANSPORT', 'DEFAULT_NAME',
            'payload_from', 'decode', 'model_from_name', 'redact')

def problems(module):
    """Return contract violations for an adapter module (empty when valid)."""
    found = [f'missing {name}' for name in REQUIRED if not hasattr(module, name)]
    if found: return found
    if not isinstance(module.ADAPTER_ID, str) or not module.ADAPTER_ID.isidentifier():
        found.append('ADAPTER_ID must be a short identifier')
    version = str(module.ADAPTER_VERSION).split('.')
    if len(version) != 3 or not all(part.isdigit() for part in version):
        found.append('ADAPTER_VERSION must look like 1.2.3')
    if module.TRANSPORT not in TRANSPORTS:
        found.append(f'TRANSPORT must be one of {sorted(TRANSPORTS)}')
    for name in REQUIRED[5:]:
        if not callable(getattr(module, name)): found.append(f'{name} must be callable')
    return found

def _build(modules):
    registry = {}
    for module in modules:
        issues = problems(module)
        if issues: raise RuntimeError(f'Invalid adapter {getattr(module, "__name__", module)}: ' + '; '.join(issues))
        if module.ADAPTER_ID in registry: raise RuntimeError(f'Duplicate adapter id {module.ADAPTER_ID}')
        registry[module.ADAPTER_ID] = module
    return registry

REGISTRY = _build([chefiq])

def get(adapter_id):
    try: return REGISTRY[adapter_id]
    except KeyError: raise ValueError(f'Unknown adapter: {adapter_id}') from None

def match(manufacturer_data):
    """Return (adapter, payload) for the first adapter that claims this advertisement."""
    for adapter in REGISTRY.values():
        payload = adapter.payload_from(manufacturer_data)
        if payload is not None: return adapter, payload
    return None

def describe():
    return [{'id': a.ADAPTER_ID, 'name': a.NAME, 'version': a.ADAPTER_VERSION, 'transport': a.TRANSPORT}
            for a in REGISTRY.values()]
