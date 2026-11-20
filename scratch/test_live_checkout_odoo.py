import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/checkout/process/"
payload = {
    "cliente_nombre": "Rodrigo Almendra UATx",
    "cliente_email": "rodrigo.almendra.uatx@gmail.com",
    "direccion": "Campus Rectoría UATx, Av. Universidad #1, Tlaxcala Centro, C.P. 90000",
    "total_pago": 48000.00,
    "obra_titulo": "Metamorfosis Cósmica",
    "obra_tipo": "ORIGINAL_UNICA",
    "rfc": "ALMR990101XYZ",
    "razon_social": "RODRIGO ALMENDRA COLECCIONES UATX",
    "codigo_postal_fiscal": "90000"
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("RESULTADO DE CHECKOUT EN VIVO:")
        print("Status:", res.get('status'))
        print("Folio Pedido:", res.get('codigo_pedido'))
        print("Guía DHL AWB:", res.get('guia_awb'))
        print("ID Odoo ERP:", res.get('id_externo_odoo_erp'))
        print("UUID SAT CFDI 4.0:", res.get('factura_fiscal', {}).get('uuid_sat'))
        print("Puntos Ganados CRM:", res.get('crm_lealtad', {}).get('puntos_ganados'))
except Exception as e:
    print("Error:", e)

