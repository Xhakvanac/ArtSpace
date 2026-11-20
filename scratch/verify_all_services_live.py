import os
import sys
import json
import xmlrpc.client
import requests
import urllib.request

print("================================================================")
print("🔍 AUDITORÍA Y VERIFICACIÓN INTEGRAL DE SERVICIOS - ARTSPACE")
print("================================================================\n")

# ----------------------------------------------------------------------
# 1. VERIFICACIÓN DE HUBSPOT CRM
# ----------------------------------------------------------------------
print("1. PROBANDO HUBSPOT CRM (Cloud API v3)...")
hubspot_token = "pat-na1-bcd74f74-28ac-4203-b248-2f7b3cc317b5"
hubspot_url = "https://api.hubapi.com/crm/v3/objects/contacts"
headers_hs = {
    "Authorization": f"Bearer {hubspot_token}",
    "Content-Type": "application/json"
}
payload_hs = {
    "properties": {
        "email": "auditoria.artspace.2026@gmail.com",
        "firstname": "Auditoría",
        "lastname": "Técnica UATx",
        "company": "Verificación de Servicios E2E"
    }
}
try:
    r_hs = requests.post(hubspot_url, json=payload_hs, headers=headers_hs, timeout=8)
    if r_hs.status_code in [200, 201]:
        print(f" -> ✅ HUBSPOT CRM CONECTADO EXITOSAMENTE (HTTP {r_hs.status_code})")
        print(f"    Contacto creado: ID={r_hs.json().get('id')} ({r_hs.json().get('properties', {}).get('email')})")
    elif r_hs.status_code == 409:
        print(f" -> ✅ HUBSPOT CRM CONECTADO EXITOSAMENTE (HTTP 409 - El contacto ya existe en tu portal)")
    else:
        print(f" -> ⚠️ HubSpot Respondió HTTP {r_hs.status_code}: {r_hs.text[:200]}")
except Exception as e:
    print(f" -> ❌ Error conectando a HubSpot: {e}")

# ----------------------------------------------------------------------
# 2. VERIFICACIÓN DE ODOO ERP
# ----------------------------------------------------------------------
print("\n2. PROBANDO ODOO ERP (XML-RPC)...")
odoo_url = "https://space-art1.odoo.com"
odoo_db = "space-art1"
odoo_user = "leopzfz@gmail.com"
odoo_key = "c15127eb6fd9a4caa4a7aaf2349fd1fb1a2a937b_oak"

try:
    common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common', allow_none=True)
    uid = common.authenticate(odoo_db, odoo_user, odoo_key, {})
    if uid:
        print(f" -> ✅ ODOO ERP CONECTADO EXITOSAMENTE (UID={uid})")
        models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object', allow_none=True)
        invoices = models.execute_kw(odoo_db, uid, odoo_key, 'account.move', 'search_read', [
            [['move_type', '=', 'out_invoice']]
        ], {'fields': ['id', 'ref', 'partner_id', 'amount_total', 'state'], 'limit': 3})
        print(f"    Facturas actuales en Odoo Contabilidad: {len(invoices)} encontradas.")
        for inv in invoices:
            print(f"     * Factura ID #{inv['id']} | Ref: {inv['ref']} | Total: ${inv['amount_total']} MXN | Estado: {inv['state']}")
    else:
        print(f" -> ❌ Odoo falló autenticación (UID=False)")
except Exception as e:
    print(f" -> ❌ Error en Odoo: {e}")

# ----------------------------------------------------------------------
# 3. VERIFICACIÓN DE ZOHO INVENTORY SCM
# ----------------------------------------------------------------------
print("\n3. PROBANDO ZOHO INVENTORY SCM...")
zoho_org = "940601046"
zoho_key = "1000.3e40701fe24e8dc564dcd6aa11b7118f.61edc5b5c3bf05459f08f87f95f443f0"
headers_zh = {
    "Authorization": f"Zoho-oauthtoken {zoho_key}",
    "Content-Type": "application/json"
}

# Probar endpoint de organizaciones y salesorders
url_zh_org = "https://www.zohoapis.com/inventory/v1/organizations"
url_zh_so = f"https://www.zohoapis.com/inventory/v1/salesorders?organization_id={zoho_org}"

try:
    r_zh = requests.get(url_zh_org, headers=headers_zh, timeout=8)
    print(f" -> Consulta Organizaciones Zoho: HTTP {r_zh.status_code}")
    print(f"    Respuesta: {r_zh.text[:250]}")
except Exception as e:
    print(f" -> Error en organizaciones Zoho: {e}")

try:
    r_zh2 = requests.get(url_zh_so, headers=headers_zh, timeout=8)
    print(f" -> Consulta Sales Orders Zoho: HTTP {r_zh2.status_code}")
    print(f"    Respuesta: {r_zh2.text[:250]}")
    if r_zh2.status_code in [200, 201]:
        print(" -> ✅ ZOHO INVENTORY CONECTADO EXITOSAMENTE")
except Exception as e:
    print(f" -> Error en Sales Orders Zoho: {e}")

# ----------------------------------------------------------------------
# 4. PRUEBA DEL FLUJO TRANSACCIONAL COMPLETO EN LA PLATAFORMA LOCAL
# ----------------------------------------------------------------------
print("\n4. PROBANDO ORQUESTADOR DE CHECKOUT E2E (ARTSPACE LOCAL SERVER)...")
checkout_url = "http://127.0.0.1:8000/api/v1/checkout/process/"
checkout_payload = {
    "cliente_nombre": "Coleccionista Verificación Final",
    "cliente_email": "coleccionista.final@artspace.test",
    "direccion": "Av. Reforma #222, CDMX",
    "total_pago": 36000.00,
    "obra_titulo": "Metamorfosis Cósmica",
    "obra_tipo": "ORIGINAL_UNICA",
    "rfc": "XAXX010101000",
    "razon_social": "PÚBLICO EN GENERAL",
    "codigo_postal_fiscal": "06600"
}

try:
    req_chk = urllib.request.Request(
        checkout_url,
        data=json.dumps(checkout_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req_chk, timeout=10) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print(f" -> ✅ CHECKOUT EJECUTADO EXITOSAMENTE:")
        print(f"    * Folio Pedido SCM: {res.get('codigo_pedido')}")
        print(f"    * Guía Courier DHL: {res.get('guia_awb')}")
        print(f"    * ID en Odoo ERP: {res.get('id_externo_odoo_erp')}")
        print(f"    * Folio Fiscal SAT CFDI 4.0 (UUID): {res.get('factura_fiscal', {}).get('uuid_sat')}")
        print(f"    * Póliza Contable Cuadrada (Debe==Haber): {res.get('asiento_contable_libro_mayor', {}).get('numero_poliza')}")
except Exception as e:
    print(f" -> ❌ Error ejecutando checkout: {e}")

print("\n================================================================")
print("FIN DEL DIAGNÓSTICO")
print("================================================================")

