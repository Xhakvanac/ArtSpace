"""
Script de Poblamiento y Validación Demostrativa: Módulo SCM ARTSPACE
Ejecución: python seed_scm.py
"""
import os
import sys
import django
from decimal import Decimal

# Asegurar codificación UTF-8 en consola de Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configurar entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artspace_project.settings')
django.setup()

from django.contrib.auth.models import User
from gallery.models import (
    ProveedorArte, InsumoAlmacen, OrdenEnvioSCM, DetalleEnvioItem,
    IncidenciaLogistica, PerfilCliente, TicketSoporte, InteraccionCRM
)
from gallery.scm_service import SCMIntegrationService


def run():
    print("=" * 60)
    print("[*] INICIANDO POBLAMIENTO DEMOSTRATIVO DE SCM (ARTSPACE)...")
    print("=" * 60)

    # 1. Proveedores Homologados
    p1, _ = ProveedorArte.objects.get_or_create(
        nombre_empresa='Maderas y Molduras Finas de México S.A. de C.V.',
        tipo='MOLDURAS_MADERA',
        defaults={
            'contacto_nombre': 'Ing. Roberto Silva Morales',
            'email': 'pedidos@maderasfinas.mx',
            'telefono': '+52 55 5543 9012',
            'tiempo_entrega_dias': 4,
            'calificacion_sla': Decimal('99.20'),
            'activo': True
        }
    )
    p2, _ = ProveedorArte.objects.get_or_create(
        nombre_empresa='Hahnemühle FineArt México Distribución',
        tipo='PAPEL_BELLAS_ARTES',
        defaults={
            'contacto_nombre': 'Lic. Andrea Lozano Casas',
            'email': 'contacto@hahnemuhle.com.mx',
            'telefono': '+52 55 8812 3456',
            'tiempo_entrega_dias': 3,
            'calificacion_sla': Decimal('98.75'),
            'activo': True
        }
    )
    p3, _ = ProveedorArte.objects.get_or_create(
        nombre_empresa='SafeArt Embalajes y Blindaje Frágil',
        tipo='EMBALAJE_SEGURIDAD',
        defaults={
            'contacto_nombre': 'Arq. David Méndez Galindo',
            'email': 'ventas@safeart.com.mx',
            'telefono': '+52 24 6462 1190',
            'tiempo_entrega_dias': 2,
            'calificacion_sla': Decimal('97.90'),
            'activo': True
        }
    )
    print("✅ Proveedores registrados correctamente.")

    # 2. Insumos con Clasificación ABC y Modelos Push/Pull
    insumo_a, _ = InsumoAlmacen.objects.get_or_create(
        sku='MOLD-NOGAL-A2',
        defaults={
            'nombre': 'Moldura Madera Nogal Sólido 42x59cm (A2)',
            'categoria_abc': 'A',
            'estrategia': 'HIBRIDO',
            'proveedor': p1,
            'stock_actual': 32,
            'stock_seguridad': 15,
            'punto_reorden': 25,
            'costo_unitario': Decimal('420.00'),
            'unidad_medida': 'Marco Ensamblado'
        }
    )
    insumo_b, _ = InsumoAlmacen.objects.get_or_create(
        sku='PAPEL-HAHN-308G',
        defaults={
            'nombre': 'Papel Photo Rag 308g 100% Algodón Libre de Ácido',
            'categoria_abc': 'B',
            'estrategia': 'PUSH',
            'proveedor': p2,
            'stock_actual': 18,
            'stock_seguridad': 20,
            'punto_reorden': 30,
            'costo_unitario': Decimal('280.00'),
            'unidad_medida': 'Bobina / Pliego'
        }
    )
    insumo_c, _ = InsumoAlmacen.objects.get_or_create(
        sku='CAJA-RIGIDA-A1',
        defaults={
            'nombre': 'Caja Triple Onda Amortiguada para Arte Frágil A1',
            'categoria_abc': 'C',
            'estrategia': 'PUSH',
            'proveedor': p3,
            'stock_actual': 45,
            'stock_seguridad': 25,
            'punto_reorden': 40,
            'costo_unitario': Decimal('115.00'),
            'unidad_medida': 'Caja Rígida'
        }
    )
    print("✅ Insumos de almacén (A, B, C) dados de alta con ROP y SS.")

    # 3. Usuario demo
    user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    perfil = None
    if user:
        perfil, _ = PerfilCliente.objects.get_or_create(usuario=user)

    # 4. Crear Órdenes de Envío Demostrativas
    scm_service = SCMIntegrationService(platform="ZOHO_INVENTORY")

    # Orden 1: Modelo Híbrido Push-Pull (En proceso y despachado)
    ord1, _ = OrdenEnvioSCM.objects.get_or_create(
        codigo_pedido='ART-SCM-2026-001',
        defaults={
            'cliente_nombre': 'Carlos Mendoza Ramos',
            'cliente_email': 'carlos.mendoza@coleccionistas.mx',
            'cliente_telefono': '+52 55 4912 8301',
            'perfil_crm': perfil,
            'estrategia_flujo': 'HIBRIDO_PUSHPULL',
            'transportista': 'DHL_EXPRESS',
            'direccion_destino': 'Av. Paseo de las Palmas 405, Lomas de Chapultepec, CDMX',
            'ciudad_destino': 'Ciudad de México',
            'pais_destino': 'México',
            'peso_volumetrico_kg': Decimal('3.20'),
            'seguro_arte_incluido': True,
            'monto_total_venta': Decimal('4200.00'),
            'comision_galeria_monto': Decimal('840.00'),
            'pago_artista_monto': Decimal('3360.00'),
            'estado_logistico': 'CHECKOUT_PAGADO'
        }
    )
    DetalleEnvioItem.objects.get_or_create(
        orden=ord1,
        titulo_obra='Metamorfosis Visual en Nogal',
        defaults={
            'artista_nombre': 'Alice Miller',
            'tipo_pieza': 'PRINT_ENMARCADO',
            'cantidad': 1,
            'precio_unitario': Decimal('4200.00'),
            'folio_certificado': 'CERT-AM-2026-881'
        }
    )
    scm_service.sincronizar_orden_con_scm(ord1)
    scm_service.generar_guia_despacho_courier(ord1)
    print(f"📦 Orden 1 creada: {ord1.codigo_pedido} | Guía: {ord1.numero_guia_awb} | Estado: {ord1.estado_logistico}")

    # Orden 2: Modelo Híbrido Entregado (Dispara automáticamente Puntos CRM y Art Club)
    ord2, _ = OrdenEnvioSCM.objects.get_or_create(
        codigo_pedido='ART-SCM-2026-002',
        defaults={
            'cliente_nombre': 'Dra. Elena Garza Villaseñor',
            'cliente_email': 'elena.garza@patronosarte.org',
            'cliente_telefono': '+52 81 8329 4000',
            'perfil_crm': perfil,
            'estrategia_flujo': 'HIBRIDO_PUSHPULL',
            'transportista': 'FEDEX_PRIORITY',
            'numero_guia_awb': 'FDX-261005-A93B12',
            'url_tracking': 'https://track.artspace.gallery/shipment/FDX-261005-A93B12',
            'direccion_destino': 'Calzada del Valle 210, San Pedro Garza García, NL',
            'ciudad_destino': 'Monterrey',
            'pais_destino': 'México',
            'peso_volumetrico_kg': Decimal('4.80'),
            'seguro_arte_incluido': True,
            'monto_total_venta': Decimal('6500.00'),
            'comision_galeria_monto': Decimal('1300.00'),
            'pago_artista_monto': Decimal('5200.00'),
            'estado_logistico': 'ENTREGADO'
        }
    )
    DetalleEnvioItem.objects.get_or_create(
        orden=ord2,
        titulo_obra='Sinfonía en Ocre y Añil (Edición Firmada)',
        defaults={
            'artista_nombre': 'Alice Miller',
            'tipo_pieza': 'PRINT_ENMARCADO',
            'cantidad': 1,
            'precio_unitario': Decimal('6500.00'),
            'folio_certificado': 'CERT-AM-2026-904'
        }
    )
    # Al crearse o guardarse con estado 'ENTREGADO', la señal Django ya acreditó puntos en CRM
    print(f"🎉 Orden 2 creada: {ord2.codigo_pedido} | Estado: ENTREGADO | Puntos acreditados al CRM!")

    # Orden 3: Incidencia Logística vinculada con Mesa de Ayuda CRM
    ord3, _ = OrdenEnvioSCM.objects.get_or_create(
        codigo_pedido='ART-SCM-2026-003',
        defaults={
            'cliente_nombre': 'Lic. Fernando Bañuelos',
            'cliente_email': 'f.banuelos@corporativo.mx',
            'cliente_telefono': '+52 33 3615 2200',
            'perfil_crm': perfil,
            'estrategia_flujo': 'PULL_COMISION',
            'transportista': 'DHL_EXPRESS',
            'numero_guia_awb': 'DHL-261005-X71900',
            'url_tracking': 'https://track.artspace.gallery/shipment/DHL-261005-X71900',
            'direccion_destino': 'Av. Américas 1500, Puerta de Hierro, Guadalajara, JAL',
            'ciudad_destino': 'Guadalajara',
            'pais_destino': 'México',
            'peso_volumetrico_kg': Decimal('6.00'),
            'seguro_arte_incluido': True,
            'monto_total_venta': Decimal('12500.00'),
            'comision_galeria_monto': Decimal('2500.00'),
            'pago_artista_monto': Decimal('10000.00'),
            'estado_logistico': 'INCIDENCIA'
        }
    )
    incidencia, _ = IncidenciaLogistica.objects.get_or_create(
        orden=ord3,
        motivo='DEMORA_TRANSPORTE',
        defaults={
            'descripcion': 'Cierre temporal de autopista por lluvias severas. Paquetería reprograma entrega con 48h adicionales.',
            'resuelta': False
        }
    )
    print(f"⚠️ Incidencia creada para {ord3.codigo_pedido}. Ticket de CRM generado: {incidencia.ticket_crm}")

    print("=" * 60)
    print("✅ POBLAMIENTO DEMOSTRATIVO SCM CONCLUIDO CON ÉXITO.")
    print("=" * 60)


if __name__ == '__main__':
    run()
