import requests

zoho_org = "940601046"
zoho_key = "1000.3e40701fe24e8dc564dcd6aa11b7118f.61edc5b5c3bf05459f08f87f95f443f0"

headers = {
    "Authorization": f"Zoho-oauthtoken {zoho_key}",
    "Content-Type": "application/json"
}

# 1. Consultar contactos para ver si existe un customer_id
url_contacts = f"https://www.zohoapis.com/inventory/v1/contacts?organization_id={zoho_org}"
r = requests.get(url_contacts, headers=headers)
print("Contactos en Zoho:")
print("Status:", r.status_code)
contacts = r.json().get('contacts', [])
print(f"Total contactos: {len(contacts)}")
customer_id = None
if contacts:
    customer_id = contacts[0]['contact_id']
    print("Primer contact_id:", customer_id, contacts[0]['contact_name'])
else:
    # Crear un contacto si no hay
    url_create_contact = f"https://www.zohoapis.com/inventory/v1/contacts?organization_id={zoho_org}"
    r_c = requests.post(url_create_contact, json={
        "contact_name": "Rodrigo Almendra",
        "email": "rodrigo.almendra.uatx@gmail.com"
    }, headers=headers)
    print("Crear contacto:", r_c.status_code, r_c.text[:200])
    if r_c.status_code in [200, 201]:
        customer_id = r_c.json().get('contact', {}).get('contact_id')

# 2. Consultar o crear items en Zoho
url_items = f"https://www.zohoapis.com/inventory/v1/items?organization_id={zoho_org}"
r_it = requests.get(url_items, headers=headers)
print("\nItems en Zoho:")
print("Status:", r_it.status_code)
items = r_it.json().get('items', [])
print(f"Total items: {len(items)}")
item_id = None
if items:
    item_id = items[0]['item_id']
    print("Primer item_id:", item_id, items[0]['name'])
else:
    # Crear un item si no hay
    r_item_create = requests.post(url_items, json={
        "name": "Metamorfosis Cósmica",
        "rate": 48000.00
    }, headers=headers)
    print("Crear item:", r_item_create.status_code, r_item_create.text[:200])
    if r_item_create.status_code in [200, 201]:
        item_id = r_item_create.json().get('item', {}).get('item_id')

# 3. Crear Sales Order
if customer_id and item_id:
    url_so = f"https://www.zohoapis.com/inventory/v1/salesorders?organization_id={zoho_org}"
    so_payload = {
        "customer_id": customer_id,
        "date": "2026-11-19",
        "line_items": [
            {
                "item_id": item_id,
                "quantity": 1,
                "rate": 48000.00
            }
        ],
        "reference_number": "ART-202611-TEST"
    }
    r_so = requests.post(url_so, json=so_payload, headers=headers)
    print("\nCrear Sales Order:")
    print("Status:", r_so.status_code)
    print("Respuesta:", r_so.text[:300])

