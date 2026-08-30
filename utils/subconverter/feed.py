import sys
from pathlib import Path


def load_uris(path):
    text = Path(path).read_text(encoding='utf-8')
    return [line.strip() for line in text.splitlines() if line.strip() and '://' in line]


def set_url(ini_text, section, url):
    marker = f'[{section}]'
    start = ini_text.find(marker)
    if start < 0:
        raise SystemExit(f'section {section} not found')
    end = ini_text.find('\n[', start + 1)
    if end < 0:
        end = len(ini_text)
    block = ini_text[start:end]
    lines = []
    replaced = False
    for line in block.splitlines():
        if line.startswith('url='):
            lines.append('url=' + url)
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append('url=' + url)
    return ini_text[:start] + '\n'.join(lines) + ini_text[end:]


if __name__ == '__main__':
    section = sys.argv[1]
    src = sys.argv[2]
    ini_path = Path(sys.argv[3] if len(sys.argv) > 3 else 'generate.ini')
    uris = load_uris(src)
    if not uris:
        raise SystemExit(f'no URIs in {src}')
    ini_path.write_text(set_url(ini_path.read_text(encoding='utf-8'), section, '|'.join(uris)), encoding='utf-8')
    print(f'Fed {len(uris)} URIs to [{section}]')
