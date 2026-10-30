"""Copy the figures and tables that the site uses from notebooks/ into jb/.

The notebooks write to notebooks/figs/ and notebooks/tables/, which are not in
git. The site needs its own copies so it can be built from a clone. Run this
after re-running a notebook whose output appears on the site:

    python sync_figs.py

It reads the table of contents in myst.yml, finds every figs/... or tables/...
path in those pages, and copies the ones that exist. It reports referenced
files that are missing, and files in jb/figs or jb/tables that no page uses.
"""

import re
import shutil
from pathlib import Path

import yaml

JB = Path(__file__).parent
SRC = JB.parent / 'notebooks'
PATTERN = re.compile(r'(?<![\w/.])((?:figs|tables)/[\w./-]+\.(?:png|svg|html|csv))')


def toc_files(entries):
    for entry in entries:
        if 'file' in entry:
            yield entry['file']
        yield from toc_files(entry.get('children', []))


def main():
    config = yaml.safe_load((JB / 'myst.yml').read_text())
    used = set()
    for page in toc_files(config['project']['toc']):
        used |= set(PATTERN.findall((JB / page).read_text()))

    copied, missing = 0, []
    for rel in sorted(used):
        src, dst = SRC / rel, JB / rel
        if not src.exists():
            missing.append(rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copy2(src, dst)
            copied += 1

    unused = sorted(
        str(p.relative_to(JB))
        for d in ('figs', 'tables')
        for p in (JB / d).glob('*')
        if p.is_file() and str(p.relative_to(JB)) not in used
    )
    print(f'{len(used)} files referenced, {copied} copied or updated')
    for rel in missing:
        print('  missing in notebooks/:', rel)
    for rel in unused:
        print('  not used by any page:', rel)


if __name__ == '__main__':
    main()
