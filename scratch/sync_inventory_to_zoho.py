import os
import sys
import django
from decimal import Decimal

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artspace_project.settings')
django.setup()

import requests
from django.conf import settings
from gallery.models import ObraArte

zoho_org = getattr(settings, 'ZOHO_INVENTORY_ORG_ID', '940601046')
zoho_key = getattr(settings, 'ZOHO_INVENTORY_API_KEY', '')

headers = {
    "Authorization": f"Zoho-oauthtoken {zoho_key}",
    "Content-Type": "application/json"
}

print(f"Sincronizando inventario con Zoho Inventory (Org: {zoho_org})...\n")

obras = ObraArte.objects.all()
print(f"Total de obras en base de datos: {obras.count()}\n")

for obra in obras:
    nombre_item = f"{obra.titulo} ({obra.artista})"
    # 1. Verificar si ya existe en Zoho
    url_search = f"https://www.zohoapis.com/inventory/v1/items?organization_id={zoho_org}&search_text={obra.titulo[:20]}"
    try:
        r_search = requests.get(url_search, headers=headers, timeout=8)
        item_id = None
        if r_search.status_code == 200 and r_search.json().get('items'):
            for it in r_search.json()['items']:
                if obra.titulo.lower() in it.get('name', '').lower():
                    item_id = it['item_id']
                    print(f"✓ '{obra.titulo}' ya existe en Zoho (Item ID: {item_id})")
                    break

        # 2. Si no existe, crearlo
        if not item_id:
            url_create = f"https://www.zohoapis.com/inventory/v1/items?organization_id={zoho_org}"
            sku = f"ART-{obra.id:04d}-{obra.categoria[:3].upper()}"
            payload = {
                "name": nombre_item,
                "rate": float(obra.precio_mxn),
                "description": f"Categoría: {obra.categoria} | Técnica: {obra.tecnica} | Medidas: {obra.dimensiones} | Año: {obra.anio} | Cert: {obra.certificado}",
                "sku": sku,
                "initial_stock": 0 if obra.vendida else 1,
                "initial_stock_rate": float(obra.precio_mxn * Decimal('0.70'))
            }
            r_create = requests.post(url_create, json=payload, headers=headers, timeout=8)
            if r_create.status_code in [200, 201]:
                item_data = r_create.json().get('item', {})
                item_id = item_data.get('item_id')
                print(f"🎉 CREADO EN ZOHO: '{obra.titulo}' -> Item ID: {item_id} | Stock inicial: {payload['initial_stock']}")
            else:
                print(f"⚠️ Error al crear '{obra.titulo}' en Zoho ({r_create.status_code}): {r_create.text[:200]}")

        if item_id:
            obra.id_externo_zoho_item = str(item_id)
            obra.save(update_fields=['id_externo_zoho_item'])

    except Exception as e:
        print(f"❌ Error con '{obra.titulo}': {e}")

print("\n=======================================================")
print("Sincronización de catálogo finalizada con éxito.")
print("=======================================================")

