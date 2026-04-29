#!/usr/bin/env python3
"""install.py — install the no-bs skill and hook into Claude Code.

Usage:
  Windows:       py -3 install.py
  macOS/Linux:   python3 install.py

Optional:
  --dry-run      print what would happen, change nothing
  --uninstall    reverse the install (remove files, drop the hook from settings.json)

What it does (idempotent — safe to re-run):
  1. Copies SKILL.md          to <config>/skills/no-bs/SKILL.md
  2. Copies hooks/no-bs-route.py to <config>/hooks/no-bs-route.py
  3. Copies commands/no-bs.md to <config>/commands/no-bs.md
  4. Patches <config>/settings.json under hooks.UserPromptSubmit to register
     the hook command (skipped if an entry already references no-bs-route)
  5. Creates <config>/no-bs-mode.json with {"mode": "on"} if missing

<config> resolution: $CLAUDE_CONFIG_DIR if set, else ~/.claude.

Fails OPEN — never partially-corrupts settings.json (writes via temp file + rename).
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


def config_dir() -> Path:
    return Path(os.environ.get('CLAUDE_CONFIG_DIR') or os.path.expanduser('~/.claude'))


def hook_command(hook_path: Path) -> str:
    """Build the platform-appropriate command string for settings.json."""
    if sys.platform.startswith('win'):
        return f'py -3 "{hook_path}"'
    return f'/usr/bin/env python3 "{hook_path}"'


def patch_settings(settings_path: Path, hook_path: Path, dry_run: bool) -> str:
    """Add the no-bs hook to settings.json under hooks.UserPromptSubmit. Idempotent.

    Returns one of: 'added', 'already-present', 'created'.
    """
    existed_before = settings_path.exists()
    existing = {}
    if existed_before:
        try:
            existing = json.loads(settings_path.read_text(encoding='utf-8'))
            if not isinstance(existing, dict):
                existing = {}
        except Exception as exc:
            raise RuntimeError(
                f'Cannot parse {settings_path}: {exc}. '
                'Fix the JSON manually, or back it up and re-run.'
            )

    hooks = existing.setdefault('hooks', {})
    if not isinstance(hooks, dict):
        raise RuntimeError(f'settings.json hooks field is not an object; aborting.')

    submit = hooks.setdefault('UserPromptSubmit', [])
    if not isinstance(submit, list):
        raise RuntimeError('settings.json hooks.UserPromptSubmit is not a list; aborting.')

    # Idempotency: skip if any existing entry's command already references the hook
    for entry in submit:
        if not isinstance(entry, dict):
            continue
        for h in entry.get('hooks', []) or []:
            if isinstance(h, dict) and 'no-bs-route' in str(h.get('command', '')):
                return 'already-present'

    submit.append({
        'matcher': '',
        'hooks': [{'type': 'command', 'command': hook_command(hook_path)}],
    })

    if dry_run:
        return 'added (dry-run)'

    # Atomic write: temp file + rename
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        mode='w', encoding='utf-8', delete=False,
        dir=str(settings_path.parent), prefix='.settings.json.tmp.',
    )
    try:
        json.dump(existing, tmp, indent=2)
        tmp.write('\n')
        tmp.close()
        os.replace(tmp.name, settings_path)
    except Exception:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
        raise

    return 'created' if not existed_before else 'added'


def unpatch_settings(settings_path: Path, dry_run: bool) -> str:
    """Remove no-bs hook entries from settings.json. Returns 'removed' / 'not-present' / 'no-file'."""
    if not settings_path.exists():
        return 'no-file'
    try:
        data = json.loads(settings_path.read_text(encoding='utf-8'))
    except Exception:
        return 'parse-error'

    submit = data.get('hooks', {}).get('UserPromptSubmit', [])
    if not isinstance(submit, list):
        return 'not-present'

    new_submit = []
    removed = False
    for entry in submit:
        if not isinstance(entry, dict):
            new_submit.append(entry)
            continue
        kept = []
        for h in entry.get('hooks', []) or []:
            if isinstance(h, dict) and 'no-bs-route' in str(h.get('command', '')):
                removed = True
                continue
            kept.append(h)
        if kept:
            entry['hooks'] = kept
            new_submit.append(entry)
        elif not entry.get('hooks'):
            # entry now has no hooks; drop it
            removed = True

    if not removed:
        return 'not-present'

    if dry_run:
        return 'removed (dry-run)'

    data['hooks']['UserPromptSubmit'] = new_submit
    tmp = tempfile.NamedTemporaryFile(
        mode='w', encoding='utf-8', delete=False,
        dir=str(settings_path.parent), prefix='.settings.json.tmp.',
    )
    try:
        json.dump(data, tmp, indent=2)
        tmp.write('\n')
        tmp.close()
        os.replace(tmp.name, settings_path)
    except Exception:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
        raise
    return 'removed'


def copy_file(src: Path, dst: Path, dry_run: bool) -> str:
    """Copy src to dst. Returns 'copied', 'unchanged', or 'created'."""
    if not src.exists():
        raise FileNotFoundError(f'Source missing: {src}')
    if dst.exists() and dst.read_bytes() == src.read_bytes():
        return 'unchanged'
    state = 'created' if not dst.exists() else 'copied'
    if dry_run:
        return f'{state} (dry-run)'
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return state


def write_mode_file(mode_path: Path, dry_run: bool) -> str:
    """Create no-bs-mode.json with mode=on if missing. Returns 'created', 'exists'."""
    if mode_path.exists():
        return 'exists'
    if dry_run:
        return 'created (dry-run)'
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps({'mode': 'on'}, indent=2) + '\n', encoding='utf-8')
    return 'created'


def install(dry_run: bool) -> int:
    repo = Path(__file__).resolve().parent
    cfg = config_dir()

    src_skill = repo / 'SKILL.md'
    src_hook = repo / 'hooks' / 'no-bs-route.py'
    src_cmd = repo / 'commands' / 'no-bs.md'

    dst_skill = cfg / 'skills' / 'no-bs' / 'SKILL.md'
    dst_hook = cfg / 'hooks' / 'no-bs-route.py'
    dst_cmd = cfg / 'commands' / 'no-bs.md'
    settings = cfg / 'settings.json'
    mode_file = cfg / 'no-bs-mode.json'

    print(f'no-bs install (config dir: {cfg})')
    if dry_run:
        print('  [DRY RUN -- no changes will be made]')
    print()

    try:
        r1 = copy_file(src_skill, dst_skill, dry_run); print(f'  SKILL.md           {dst_skill}: {r1}')
        r2 = copy_file(src_hook, dst_hook, dry_run);   print(f'  no-bs-route.py     {dst_hook}: {r2}')
        r3 = copy_file(src_cmd, dst_cmd, dry_run);     print(f'  no-bs.md (wrapper) {dst_cmd}: {r3}')
        r4 = patch_settings(settings, dst_hook, dry_run); print(f'  settings.json      {settings}: {r4}')
        r5 = write_mode_file(mode_file, dry_run);      print(f'  no-bs-mode.json    {mode_file}: {r5}')
    except Exception as exc:
        print(f'\nINSTALL FAILED: {exc}', file=sys.stderr)
        return 2

    print()
    if dry_run:
        print('Dry run complete. Re-run without --dry-run to apply.')
    else:
        print('Install complete. Restart Claude Code, then try /no-bs status in any chat.')
        print('To disable: /no-bs off. To re-enable: /no-bs on.')
    return 0


def uninstall(dry_run: bool) -> int:
    cfg = config_dir()
    dst_skill_dir = cfg / 'skills' / 'no-bs'
    dst_skill = dst_skill_dir / 'SKILL.md'
    dst_hook = cfg / 'hooks' / 'no-bs-route.py'
    dst_cmd = cfg / 'commands' / 'no-bs.md'
    settings = cfg / 'settings.json'
    mode_file = cfg / 'no-bs-mode.json'

    print(f'no-bs uninstall (config dir: {cfg})')
    if dry_run:
        print('  [DRY RUN -- no changes will be made]')
    print()

    def remove(path: Path, label: str):
        if not path.exists():
            print(f'  {label}: not present')
            return
        if dry_run:
            print(f'  {label}: would remove {path}')
            return
        try:
            path.unlink()
            print(f'  {label}: removed {path}')
        except Exception as exc:
            print(f'  {label}: failed ({exc})', file=sys.stderr)

    remove(dst_skill, 'SKILL.md')
    if dst_skill_dir.exists() and not any(dst_skill_dir.iterdir()):
        if not dry_run:
            dst_skill_dir.rmdir()
        print(f'  skill dir: removed {dst_skill_dir}')
    remove(dst_hook, 'hook')
    remove(dst_cmd, 'wrapper')
    remove(mode_file, 'mode file')
    try:
        r = unpatch_settings(settings, dry_run)
        print(f'  settings.json hook entry: {r}')
    except Exception as exc:
        print(f'  settings.json: failed ({exc})', file=sys.stderr)

    print()
    print('Uninstall complete.' if not dry_run else 'Dry run complete.')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Install or uninstall the no-bs skill and hook.')
    parser.add_argument('--dry-run', action='store_true', help='print what would happen, change nothing')
    parser.add_argument('--uninstall', action='store_true', help='reverse the install')
    args = parser.parse_args()

    if args.uninstall:
        return uninstall(args.dry_run)
    return install(args.dry_run)


if __name__ == '__main__':
    sys.exit(main())
