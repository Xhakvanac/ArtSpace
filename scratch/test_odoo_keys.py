import xmlrpc.client

u = "https://space-art1.odoo.com"
d = "space-art1"
user = "leopzfz@gmail.com"
keys = [
    "ad44c386e282fbc6d18a9db232bdc054a2da0e72_oak",
    "ad44c386e282fbc6d18a9db232bdc054a2da0e72",
]

common = xmlrpc.client.ServerProxy(f'{u}/xmlrpc/2/common', allow_none=True)
for k in keys:
    print(f"Probando key: {k}...")
    try:
        uid = common.authenticate(d, user, k, {})
        print(f" -> Resultado UID: {uid}")
    except Exception as e:
        print(f" -> Error: {e}")

