import requests

zoho_org = "940601046"
zoho_token = "1000.b70482bb7729e7f7799104d2a4a5a30c.db2a28b8d97411bef8ea671c44637ef8"

headers = {
    "Authorization": f"Zoho-oauthtoken {zoho_token}",
    "Content-Type": "application/json"
}

# 1. Probar en diferentes data centers de Zoho
domains = [
    "https://www.zohoapis.com",
    "https://inventory.zoho.com",
    "https://www.zohoapis.eu",
    "https://www.zohoapis.in"
]

for dom in domains:
    url = f"{dom}/inventory/v1/organizations"
    print(f"\nProbando GET {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=6)
        print(f"Status: {r.status_code}")
        print(f"Respuesta: {r.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

# 2. Probar endpoint de ventas
url_sales = f"https://www.zohoapis.com/inventory/v1/salesorders?organization_id={zoho_org}"
print(f"\nProbando GET {url_sales}...")
try:
    r = requests.get(url_sales, headers=headers, timeout=6)
    print(f"Status: {r.status_code}")
    print(f"Respuesta: {r.text[:400]}")
except Exception as e:
    print(f"Error: {e}")

