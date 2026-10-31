"""Check that the Python code in every notebook parses.

Reads the jupytext notebooks in notebooks/ and the Python .ipynb files in
notebooks/ and examples/, joins the code cells, and reports syntax errors.
Lines that start with a magic (%) or shell command (!) are skipped. This
doesn't run anything, so it needs no data.
"""

import ast
import sys
from pathlib import Path

import jupytext

ROOT = Path(__file__).resolve().parents[2]


def notebooks():
    yield from sorted(ROOT.glob('notebooks/*.md'))
    yield ROOT / 'notebooks/process.ipynb'
    yield from sorted(ROOT.glob('examples/*/*.ipynb'))


def code(nb):
    lines = []
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        for line in cell.source.splitlines():
            if line.lstrip().startswith(('%', '!')):
                line = ''
            lines.append(line)
        lines.append('')
    return '\n'.join(lines)


def main():
    errors = 0
    count = 0
    for path in notebooks():
        nb = jupytext.read(path)
        language = nb.metadata.get('kernelspec', {}).get('language', 'python')
        if language != 'python':
            continue
        count += 1
        try:
            ast.parse(code(nb), filename=str(path))
        except SyntaxError as e:
            errors += 1
            print(f'{path.relative_to(ROOT)}: {e.msg} (code line {e.lineno})')
    print(f'Checked {count} notebooks, {errors} with syntax errors')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
