import json

with open('employees_metadata.json', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total employees: {len(data)}')
print('\nSearching for "Tai" or similar names:')

for code, info in sorted(data.items(), key=lambda x: x[1]['full_name']):
    name = info['full_name']
    if 'tai' in name.lower() or 'tài' in name.lower():
        print(f'  ✓ {name} ({code})')

print('\nAll employees (first 30):')
for i, (code, info) in enumerate(sorted(data.items(), key=lambda x: x[1]['full_name'])[:30], 1):
    print(f'{i}. {info["full_name"]} ({code})')
