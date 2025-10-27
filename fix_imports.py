"""
Script para corrigir imports relativos para absolutos em todos os arquivos Python.
"""

import re
from pathlib import Path

# Mapeamento de imports para corrigir
REPLACEMENTS = [
    (r'^from models\.state import', 'from src.models.state import'),
    (r'^from models import', 'from src.models import'),
    (r'^from config\.settings import', 'from src.config.settings import'),
    (r'^from config import', 'from src.config import'),
    (r'^from clients\.', 'from src.clients.'),
    (r'^from nodes\.', 'from src.nodes.'),
    (r'^from graph\.', 'from src.graph.'),
    (r'^from tools\.', 'from src.tools.'),
]

def fix_file(filepath):
    """Corrige imports em um arquivo."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        fixed_line = line
        for pattern, replacement in REPLACEMENTS:
            if re.match(pattern, line):
                fixed_line = re.sub(pattern, replacement, line)
                print(f"  {filepath.name}: {line.strip()} -> {fixed_line.strip()}")
                break
        fixed_lines.append(fixed_line)

    new_content = '\n'.join(fixed_lines)

    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    src_dir = Path('src')
    fixed_count = 0

    print("Corrigindo imports em todos os arquivos Python...\n")

    for py_file in src_dir.rglob('*.py'):
        if fix_file(py_file):
            fixed_count += 1

    print(f"\n{fixed_count} arquivos corrigidos!")

if __name__ == '__main__':
    main()
