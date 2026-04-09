import httpx, json, sys

try:
    r = httpx.get(
        'http://localhost:42002/analytics/pass-rates',
        params={'lab': 'lab-05'},
        headers={'Authorization': 'Bearer my-secret-api-key'}
    )
    data = r.json()
    if not data:
        print("No pass rate data found for lab-05.")
    else:
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f'Error: {e}')
