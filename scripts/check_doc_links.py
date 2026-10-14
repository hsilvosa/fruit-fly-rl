"""Quick check of local Markdown links (file existence and, for same-repository headings, anchors). No imports from the package.
Usage: check_doc_links.py [file.md ...]   (default: every tracked and untracked Markdown file outside runs/, private/, data/, reports/)"""
import os, re, subprocess, sys

ROOT = 'C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'
os.chdir(ROOT)
LINK = re.compile(r'\]\(<?([^)\s<>]+?)>?(?:\s+"[^"]*")?\)')
FENCE = re.compile(r'^\s*(```|~~~)')


def slug(heading):
    text = re.sub(r'[`*_]', '', heading.strip().lower())
    text = re.sub(r'[^\w\- ]', '', text, flags=re.UNICODE)
    return text.replace(' ', '-')


def anchors(path, cache={}):
    if path not in cache:
        found, in_code = set(), False
        for line in open(path, encoding='utf-8', errors='replace'):
            if FENCE.match(line):
                in_code = not in_code
            elif not in_code and line.startswith('#'):
                found.add(slug(line.lstrip('#')))
        cache[path] = found
    return cache[path]


files = sys.argv[1:] or [p for p in subprocess.check_output(
    ['git', '-c', 'safe.directory=' + ROOT, 'ls-files', '--cached', '--others', '--exclude-standard', '*.md']).decode().split('\n')
    if p and not p.startswith(('runs/', 'private/', 'data/', 'reports/', '.claude/'))]
problems = 0
for path in files:
    in_code = False
    for number, line in enumerate(open(path, encoding='utf-8', errors='replace'), 1):
        if FENCE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        for target in LINK.findall(line):
            if re.match(r'^[a-z]+:', target):
                continue
            name, _, fragment = target.partition('#')
            resolved = path if not name else os.path.normpath(os.path.join(os.path.dirname(path), name)).replace('\\', '/')
            if not os.path.exists(resolved):
                print(f'{path}:{number}: missing target {target}'); problems += 1
            elif fragment and resolved.endswith('.md') and fragment.lower() not in anchors(resolved):
                print(f'{path}:{number}: missing anchor {target}'); problems += 1
print('files checked', len(files), 'problems', problems)
sys.exit(1 if problems else 0)
