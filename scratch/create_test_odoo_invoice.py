import xmlrpc.client

u = "https://space-art1.odoo.com"
d = "space-art1"
user = "leopzfz@gmail.com"
api_key = "c15127eb6fd9a4caa4a7aaf2349fd1fb1a2a937b_oak"

common = xmlrpc.client.ServerProxy(f'{u}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(d, user, api_key, {})
models = xmlrpc.client.ServerProxy(f'{u}/xmlrpc/2/object', allow_none=True)

# 1. Crear o buscar partner
partners = models.execute_kw(d, uid, api_key, 'res.partner', 'search_read', [[['name', '=', 'Rodrigo Almendra']]], {'fields': ['id', 'name']})
if partners:
    partner_id = partners[0]['id']
else:
    partner_id = models.execute_kw(d, uid, api_key, 'res.partner', 'create', [{
        'name': 'Rodrigo Almendra (Coleccionista)',
        'email': 'rodrigo.almendra.uatx@gmail.com',
        'customer_rank': 1
    }])
print("Partner ID en Odoo:", partner_id)

# 2. Crear factura de prueba out_invoice
invoice_id = models.execute_kw(d, uid, api_key, 'account.move', 'create', [{
    'move_type': 'out_invoice',
    'partner_id': partner_id,
    'ref': 'ART-TEST-E2E-2026',
    'narration': 'Factura de prueba de sincronización ARTSPACE ERP -> Odoo Contabilidad | CFDI 4.0 SAT UUID: e5f789a2-1111-4444-9999-abcdef012345',
    'invoice_line_ids': [
        (0, 0, {
            'name': 'Obra de Arte: Ecos del Vacío (Elena Rostova) - Pieza Única 1/1',
            'quantity': 1,
            'price_unit': 42000.00
        })
    ]
}])
print(f"¡FACTURA CREADA EN ODOO CON ÉXITO! ID de Factura = {invoice_id}")

