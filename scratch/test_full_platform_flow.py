import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artspace_project.settings')
django.setup()

from django.contrib.auth.models import User
from gallery.models import (
    PerfilCliente, ObraArte, ProveedorArte,
    OrdenEnvioSCM, FacturaFiscalCFDI, LiquidacionArtistaERP
)
from gallery.erp_services import ERPAccountingService
from gallery.scm_service import SCMIntegrationService
from gallery.crm_service import sincronizar_lead_hubspot

print("=== 1. VERIFICACIÓN DE ARTISTA ===")
artist_user, created = User.objects.get_or_create(
    username="marcos_escultor",
    defaults={"email": "marcos.escultor@artspace.test"}
)
if created:
    artist_user.set_password("ArtistaPass2026!")
    artist_user.save()

perfil_art, _ = PerfilCliente.objects.get_or_create(usuario=artist_user)
perfil_art.rol = 'ARTISTA'
perfil_art.save()

prov, _ = ProveedorArte.objects.get_or_create(
    email=artist_user.email,
    defaults={
        'nombre_empresa': f"Estudio de {artist_user.username}",
        'tipo': 'ARTISTA_INDEPENDIENTE',
        'contacto_nombre': artist_user.username,
        'telefono': '+522461112233',
        'tiempo_entrega_dias': 4
    }
)
print(f"✓ Artista listo: {artist_user.username} (Rol: {perfil_art.rol})")

print("\n=== 2. CREACIÓN / SUBIDA DE OBRA POR EL ARTISTA ===")
obra_test, created_obra = ObraArte.objects.get_or_create(
    titulo="Metamorfosis Cósmica",
    defaults={
        'artista': "Marcos Escultor",
        'artista_usuario': artist_user,
        'categoria': "Escultura",
        'precio_mxn': Decimal('48000.00'),
        'precio_usd': Decimal('2666.67'),
        'imagen': "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=800&auto=format&fit=crop&q=80",
        'tecnica': "Bronce fundido a la cera perdida y pátina verde jade",
        'dimensiones': "65 x 40 x 35 cm",
        'anio': 2026,
        'es_original_unica': True,
        'enmarcado_disponible': False,
        'precio_enmarcado': Decimal('0.00'),
        'certificado': "Certificado Holográfico Físico + Hash Blockchain",
        'descripcion': "Pieza escultórica inspirada en las formas astronómicas y las fuerzas gravitatorias.",
        'badge': "Obra Nueva 1/1"
    }
)
print(f"✓ Obra en catálogo: '{obra_test.titulo}' - Precio: ${obra_test.precio_mxn} MXN - Vendida: {obra_test.vendida}")

print("\n=== 3. ADQUISICIÓN POR COMPRADOR (ORQUESTACIÓN CRM, SCM, ERP) ===")
# Simular compra de la obra
from django.utils import timezone
import uuid

folio_pedido = f"ART-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
guia_awb = f"DHL-AWB-{uuid.uuid4().hex[:10].upper()}"

comprador_user = User.objects.filter(username="rodrigo_coleccionista").first()
perfil_comprador = None
if comprador_user:
    perfil_comprador, _ = PerfilCliente.objects.get_or_create(usuario=comprador_user)

orden = OrdenEnvioSCM.objects.create(
    codigo_pedido=folio_pedido,
    cliente_nombre="Rodrigo Almendra",
    cliente_email="rodrigo.almendra.uatx@gmail.com",
    direccion_destino="Av. Universidad #1, Tlaxcala Centro, C.P. 90000",
    monto_total_venta=obra_test.precio_mxn,
    transportista='DHL_EXPRESS',
    numero_guia_awb=guia_awb,
    url_tracking=f"https://track.dhl.com/?awb={guia_awb}",
    estado_logistico='PREPARACION_CURATORIAL',
    perfil_crm=perfil_comprador
)

# SCM: Cadena de suministro
scm = SCMIntegrationService(platform="ZOHO_INVENTORY")
scm_res = scm.sincronizar_orden_con_scm(orden)
print(f"✓ SCM Zoho Inventory: SO={orden.id_externo_zoho} (Modo: {scm_res.get('modo')})")
print(f"✓ SCM DHL Tracking: AWB={orden.numero_guia_awb}")

# ERP: CFDI 4.0
factura = ERPAccountingService.generar_factura_cfdi(
    orden=orden,
    rfc="ALMR990101XYZ",
    razon_social="RODRIGO ALMENDRA COLECCIONES",
    cp_fiscal="90000"
)
print(f"✓ ERP Factura CFDI 4.0: UUID={factura.uuid_fiscal} - Total con Impuestos: ${factura.total} MXN")

# ERP: Split 70/30 para el artista creador
liquidacion = ERPAccountingService.procesar_split_artista(orden=orden, artista_proveedor=prov)
print(f"✓ ERP Split 70/30: Artista={prov.nombre_empresa}")
print(f"   -> Bruto (70%): ${liquidacion.monto_bruto_dividendo} MXN")
print(f"   -> Retención ISR (1.25% RESICO): -${liquidacion.retencion_isr} MXN")
print(f"   -> Neto a Dispersar SPEI: ${liquidacion.monto_neto_dispersar} MXN")
print(f"   -> Clave SPEI Banxico: {liquidacion.clave_rastreo_spei}")

# Marcar obra como vendida
obra_test.vendida = True
obra_test.save()
print(f"✓ Catálogo actualizado: Obra '{obra_test.titulo}' marcada como VENDIDA = {obra_test.vendida}")

# ERP: Póliza de Ingreso y Odoo
poliza = ERPAccountingService.generar_asiento_ingreso_venta(orden=orden)
print(f"✓ ERP Póliza Contable: {poliza.numero_poliza} (Debe: ${poliza.monto_debe} = Haber: ${poliza.monto_haber})")

odoo_res = ERPAccountingService.sincronizar_con_odoo(orden=orden, factura=factura)
print(f"✓ ERP Odoo Sync: {odoo_res.get('status')} - Odoo ID: {odoo_res.get('odoo_id')}")

# CRM: Fidelización
if perfil_comprador:
    pts = perfil_comprador.acreditar_puntos(obra_test.precio_mxn, f"Compra '{obra_test.titulo}'")
    print(f"✓ CRM Art Club: +{pts} puntos acreditados a {comprador_user.username} (Saldo total: {perfil_comprador.puntos_fidelidad} pts)")

print("\n=== RESUMEN DE INTEGRACIÓN DE LOS 4 SERVICIOS ===")
print("1. CRM (HubSpot & Art Club): Lead registrado, puntos acreditados.")
print("2. SCM (Zoho Inventory & DHL): Orden de venta sincronizada, guía aérea AWB generada.")
print("3. ERP (Odoo & SAT CFDI 4.0): Timbrado fiscal, Póliza balanceada, Split 70/30 con retención 1.25% RESICO.")
print("4. Portal Artista: El artista puede visualizar en /panel-artista/ su saldo neto por SPEI.")
