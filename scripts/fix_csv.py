import csv
import collections

specific = {
    'backend\\src\\app\\sync\\sources\\anime_offline.py': 'STUB - dummy adapter, no real data ingestion',
    'backend\\src\\app\\sync\\sources\\anilist.py': 'STUB - dummy adapter, no real data ingestion',
    'backend\\src\\app\\sync\\sources\\mangadex.py': 'STUB - dummy adapter, no real data ingestion',
    'backend\\src\\app\\sync\\sources\\jikan.py': 'STUB - dummy adapter, no real data ingestion',
    'backend\\src\\app\\routers\\_deprecated_auth.py': 'DEAD CODE - old router, not registered anywhere',
    'backend\\src\\app\\repositories\\_deprecated_refresh_token_repository.py': 'DEAD CODE - broken imports, orphaned',
    'backend\\src\\app\\core\\rate_limiter.py': 'STUB - no-op, no actual rate limiting',
    'backend\\tests\\debug_path.py': 'DUMMY - debugging aid, not a real test',
}

prefix_map = {
    'src\\': 'DEAD CODE - old version superseded by backend/src/',
    'backend\\tests\\phase9_social.py': 'REAL integration test (NOT auto-discovered - missing test_ prefix)',
    'backend\\tests\\phase10_watchparty.py': 'REAL integration test (NOT auto-discovered)',
    'backend\\tests\\phase11_notifications.py': 'REAL integration test (NOT auto-discovered)',
    'backend\\tests\\phase12_setup.py': 'REAL integration test (NOT auto-discovered)',
}

rows = []
with open('checkfiles.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fp = row['FilePath']
        summary = None
        if fp in specific:
            summary = specific[fp]
        elif fp.startswith('backend\\tests\\test_'):
            summary = 'REAL - backend test file'
        elif fp.startswith('backend\\tests\\'):
            summary = 'REAL - backend test file'
        elif fp.startswith('backend\\src\\app\\routes\\'):
            summary = 'REAL - API route handler'
        elif fp.startswith('backend\\src\\app\\services\\'):
            summary = 'REAL - business logic service'
        elif fp.startswith('backend\\src\\app\\repositories\\'):
            summary = 'REAL - data access repository'
        elif fp.startswith('backend\\src\\app\\models\\'):
            summary = 'REAL - SQLModel table definition'
        elif fp.startswith('backend\\src\\app\\schemas\\'):
            summary = 'REAL - Pydantic request/response schema'
        elif fp.startswith('backend\\src\\app\\sync\\'):
            summary = 'REAL - sync pipeline code (adapters are STUB)'
        elif fp.startswith('backend\\src\\app\\external\\'):
            summary = 'REAL - HTTP client for external API'
        elif fp.startswith('backend\\src\\app\\workers\\'):
            summary = 'REAL - Celery worker task'
        elif fp.startswith('backend\\src\\app\\commands\\'):
            summary = 'REAL - CLI command'
        elif fp.startswith('backend\\src\\app\\core\\'):
            summary = 'REAL - core infrastructure (auth, config)'
        elif fp.startswith('backend\\src\\app\\'):
            summary = 'REAL - backend application code'
        elif fp.startswith('backend\\src\\'):
            summary = 'REAL - backend source'
        elif fp.startswith('backend\\'):
            summary = 'REAL - backend file'
        elif fp.startswith('frontend\\src\\pages\\social\\'):
            summary = 'STUB - placeholder page, only renders title text'
        elif fp.startswith('frontend\\src\\pages\\profile\\'):
            summary = 'STUB - placeholder page, only renders title text'
        elif fp.startswith('frontend\\src\\pages\\'):
            summary = 'REAL - Vue page component'
        elif fp.startswith('frontend\\src\\__tests__'):
            summary = 'REAL - frontend test'
        elif '\\__tests__\\' in fp:
            summary = 'REAL - frontend component test'
        elif fp.startswith('frontend\\src\\stores\\'):
            summary = 'REAL - Pinia store'
        elif fp.startswith('frontend\\src\\composables\\'):
            summary = 'REAL - Vue composable'
        elif fp.startswith('frontend\\src\\components\\'):
            summary = 'REAL - Vue shared component'
        elif fp.startswith('frontend\\src\\router\\'):
            summary = 'REAL - Vue router config'
        elif fp.startswith('frontend\\src\\types\\'):
            summary = 'REAL - TypeScript type definitions'
        elif fp.startswith('frontend\\src\\boot\\'):
            summary = 'REAL - Quasar boot file'
        elif fp.startswith('frontend\\src\\layouts\\'):
            summary = 'REAL - Vue layout component'
        elif fp.startswith('frontend\\src\\css\\'):
            summary = 'REAL - CSS/SCSS styles'
        elif fp.startswith('frontend\\src\\'):
            summary = 'REAL - Frontend source file'
        elif fp.startswith('frontend\\'):
            summary = 'REAL - Frontend file'
        elif fp.startswith('infra\\'):
            summary = 'REAL - Infrastructure config (Docker, Nginx)'
        elif fp.startswith('docs\\'):
            summary = 'REAL - Documentation'
        elif fp.startswith('scripts\\'):
            summary = 'REAL - Utility script'
        elif fp.startswith('src\\'):
            summary = 'DEAD CODE - old version superseded by backend/src/'
        else:
            summary = 'REAL - Project root file'

        for prefix, s in prefix_map.items():
            if fp.startswith(prefix):
                summary = s
                break
        if fp in specific:
            summary = specific[fp]

        row['Summary'] = summary
        rows.append(row)

with open('checkfiles.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['FilePath', 'Hash', 'Length', 'LastWrite', 'Summary'])
    writer.writeheader()
    writer.writerows(rows)

c = collections.Counter(r['Summary'] for r in rows)
for s, count in c.most_common():
    print(f'  {s}: {count}')

# Show uncategorized
uncategorized = [r for r in rows if r['Summary'] in ('Project root file', 'Unknown - needs classification')]
if uncategorized:
    print(f'\n{len(uncategorized)} uncategorized files')
