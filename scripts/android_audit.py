#!/usr/bin/env python3
"""Non-mutating compatibility audit of the upstream Rayburst checkout."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
checks = {
    'Tauri project': root / 'src-tauri' / 'tauri.conf.json',
    'Rust manifest': root / 'src-tauri' / 'Cargo.toml',
    'Frontend manifest': root / 'package.json',
    'Engine lifecycle': root / 'src-tauri' / 'src' / 'engine' / 'lifecycle.rs',
    'Native entry point': root / 'src-tauri' / 'src' / 'lib.rs',
}
report = {'project': 'Rayburst for Android', 'minSdk': 31, 'target': 'aarch64-linux-android', 'checks': {}, 'blockers': []}
for label, path in checks.items():
    report['checks'][label] = path.exists()
    if not path.exists():
        report['blockers'].append(f'Missing upstream file: {path.relative_to(root)}')

conf = checks['Tauri project']
if conf.exists():
    try:
        data = json.loads(conf.read_text(encoding='utf-8'))
        report['identifier'] = data.get('identifier')
        report['externalBin'] = data.get('bundle', {}).get('externalBin', [])
    except (OSError, ValueError) as exc:
        report['blockers'].append(f'Invalid Tauri config: {exc}')

# Desktop sidecars and system commands must not be assumed to run on Android.
report['blockers'].extend([
    'Port aria2 engine lifecycle to Android-supported execution model and package ARM64 engine',
    'Audit cfg-gating of desktop-only Tauri plugins and commands',
    'Implement Android foreground download service and notification permissions',
    'Implement Android SAF download directory handling and task persistence',
    'Verify mobile responsive UI and protocol coverage on device',
])
out = root / 'android-audit.json'
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=False))
