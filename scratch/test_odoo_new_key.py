import xmlrpc.client

u = "https://space-art1.odoo.com"
d = "space-art1"
user = "leopzfz@gmail.com"
keys = [
    "c15127eb6fd9a4caa4a7aaf2349fd1fb1a2a937b_oak",
    "c15127eb6fd9a4caa4a7aaf2349fd1fb1a2a937b",
]

common = xmlrpc.client.ServerProxy(f'{u}/xmlrpc/2/common', allow_none=True)
for k in keys:
    print(f"Probando key: {k}...")
    try:
        uid = common.authenticate(d, user, k, {})
        print(f" -> Resultado UID: {uid}")
        if uid:
            print(" -> ¡AUTENTICACIÓN EXITOSA EN ODOO! UID =", uid)
            models = xmlrpc.client.ServerProxy(f'{u}/xmlrpc/2/object', allow_none=True)
            user_data = models.execute_kw(d, uid, k, 'res.users', 'read', [[uid]], {'fields': ['name', 'login', 'company_id']})
            print(f" -> Datos del usuario en Odoo: {user_data}")
            
            # Probar si puede consultar o crear facturas en account.move
            account_moves = models.execute_kw(d, uid, k, 'account.move', 'search_count', [[['move_type', '=', 'out_invoice']]])
            print(f" -> Facturas out_invoice en Odoo Contabilidad: {account_moves}")
            break
    except Exception as e:
        print(f" -> Error: {e}")

