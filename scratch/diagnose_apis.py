import os
import sys
import xmlrpc.client
import requests

print("==========================================")
print("1. PROBANDO CONEXIÓN CON ODOO XML-RPC")
print("==========================================")
# Probar con y sin /mcp, y con y sin punto en la base de datos
test_configs = [
    {"url": "https://space-art1.odoo.com", "db": "space-art1"},
    {"url": "https://space-art1.odoo.com", "db": "space-art1."},
    {"url": "https://space-art1.odoo.com/mcp", "db": "space-art1"},
]
username = "leopzfz@gmail.com"
api_key = "ad44c386e282fbc6d18a9db232bdc054a2da0e72_oak"

for cfg in test_configs:
    u = cfg["url"]
    d = cfg["db"]
    print(f"\nProbando URL='{u}', DB='{d}', User='{username}'...")
    try:
        common = xmlrpc.client.ServerProxy(f'{u}/xmlrpc/2/common', allow_none=True)
        version = common.version()
        print(f" -> Servidor Odoo responde versión: {version.get('server_version')}")
        
        uid = common.authenticate(d, username, api_key, {})
        print(f" -> Resultado de authenticate(db='{d}'): UID = {uid}")
        if uid:
            print(" -> ¡AUTENTICACIÓN EXITOSA EN ODOO! UID =", uid)
            models = xmlrpc.client.ServerProxy(f'{u}/xmlrpc/2/object', allow_none=True)
            # Consultar facturas de cliente
            invoices = models.execute_kw(d, uid, api_key, 'account.move', 'search_read', [
                [['move_type', '=', 'out_invoice']]
            ], {'fields': ['name', 'partner_id', 'amount_total', 'state'], 'limit': 3})
            print(f" -> Facturas encontradas en Odoo: {invoices}")
            break
    except Exception as e:
        print(f" -> Error con esta config: {e}")

print("\n==========================================")
print("2. PROBANDO CONEXIÓN CON ZOHO INVENTORY")
print("==========================================")
zoho_org = "940601046"
zoho_token = "1000.35bdf6c1c08a5bda7c04d35d6abb903e.7b49b683a75074bf66e93bc30635feaa"

headers = {
    "Authorization": f"Zoho-oauthtoken {zoho_token}",
    "Content-Type": "application/json"
}

# Probando dominios com y mx
domains = [
    "https://www.zohoapis.com",
    "https://www.zohoapis.mx",
    "https://inventory.zoho.com"
]

for dom in domains:
    url = f"{dom}/inventory/v1/organizations"
    print(f"\nProbando GET {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f" -> Status: {r.status_code}")
        print(f" -> Respuesta: {r.text[:300]}")
        if r.status_code == 200:
            print(" -> ¡AUTENTICACIÓN EXITOSA EN ZOHO!")
            break
    except Exception as e:
        print(f" -> Error de conexión: {e}")

# Probar endpoint de salesorders en zohoapis.com con el org_id
url_so = f"https://www.zohoapis.com/inventory/v1/salesorders?organization_id={zoho_org}"
print(f"\nProbando GET {url_so}...")
try:
    r = requests.get(url_so, headers=headers, timeout=8)
    print(f" -> Status: {r.status_code}")
    print(f" -> Respuesta: {r.text[:400]}")
except Exception as e:
    print(f" -> Error: {e}")

