"""
Servicio de Integración SCM (Supply Chain Management) para ARTSPACE.
Conector para Zoho Inventory, Odoo SCM y APIs de Paquetería (DHL / FedEx).
"""
import uuid
from decimal import Decimal
from django.utils import timezone


class SCMIntegrationService:
    """
    Gestiona la comunicación entre el core de e-commerce en Django
    y plataformas ERP/SCM como Zoho Inventory u Odoo.
    """

    def __init__(self, platform="ZOHO_INVENTORY"):
        self.platform = platform
        self.api_version = "v1"

    def sincronizar_orden_con_scm(self, orden_envio):
        """
        Envía los datos de una orden confirmada en el Checkout hacia Zoho Inventory u Odoo SCM.
        Genera el ID externo y la orden de venta (Sales Order).
        """
        payload = {
            "customer_name": orden_envio.cliente_nombre,
            "customer_email": orden_envio.cliente_email,
            "reference_number": orden_envio.codigo_pedido,
            "shipping_address": orden_envio.direccion_destino,
            "strategy": orden_envio.estrategia_flujo,
            "line_items": [
                {
                    "item_name": item.titulo_obra,
                    "artist": item.artista_nombre,
                    "type": item.tipo_pieza,
                    "quantity": item.cantidad,
                    "rate": float(item.precio_unitario),
                    "certificate": item.folio_certificado,
                }
                for item in orden_envio.items.all()
            ],
            "total_amount": float(orden_envio.monto_total_venta),
            "carrier": orden_envio.transportista,
            "created_at": orden_envio.fecha_pedido.isoformat() if orden_envio.fecha_pedido else timezone.now().isoformat(),
        }

        # Simulación de respuesta REST API desde Zoho Inventory
        if not orden_envio.id_externo_zoho:
            external_id = f"ZOHO-SO-{uuid.uuid4().hex[:8].upper()}"
            orden_envio.id_externo_zoho = external_id
            orden_envio.save(update_fields=['id_externo_zoho'])

        return {
            "status": "SUCCESS",
            "platform": self.platform,
            "external_sales_order_id": orden_envio.id_externo_zoho,
            "payload_sent": payload,
        }

    def generar_guia_despacho_courier(self, orden_envio):
        """
        Simula la interacción con la API de paquetería (DHL Express / FedEx Priority).
        Genera el número de rastreo (Air Waybill) y la URL de tracking.
        """
        if orden_envio.transportista == 'DESCARGA_DIGITAL':
            orden_envio.numero_guia_awb = f"DIGITAL-TOKEN-{uuid.uuid4().hex[:12].upper()}"
            orden_envio.url_tracking = f"https://artspace.gallery/descargas/{orden_envio.codigo_pedido}/"
        else:
            prefijo = "DHL" if orden_envio.transportista == 'DHL_EXPRESS' else "FDX"
            awb = f"{prefijo}-{timezone.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            orden_envio.numero_guia_awb = awb
            orden_envio.url_tracking = f"https://track.artspace.gallery/shipment/{awb}"

        orden_envio.estado_logistico = 'DESPACHADO_TRANSITO'
        orden_envio.fecha_despacho = timezone.now()
        orden_envio.save(update_fields=['numero_guia_awb', 'url_tracking', 'estado_logistico', 'fecha_despacho'])

        return {
            "awb": orden_envio.numero_guia_awb,
            "tracking_url": orden_envio.url_tracking,
            "status": orden_envio.estado_logistico,
        }

    def procesar_webhook_entrega(self, numero_guia_awb, status="ENTREGADO"):
        """
        Recibe un webhook simulado de la paquetería actualizando el estado de la entrega.
        """
        from .models import OrdenEnvioSCM
        try:
            orden = OrdenEnvioSCM.objects.get(numero_guia_awb=numero_guia_awb)
            if status == "ENTREGADO":
                orden.estado_logistico = 'ENTREGADO'
                orden.fecha_entrega_real = timezone.now()
                orden.save()
                return {"success": True, "message": f"Orden {orden.codigo_pedido} marcada como ENTREGADA."}
            elif status == "INCIDENCIA":
                orden.estado_logistico = 'INCIDENCIA'
                orden.save()
                return {"success": True, "message": f"Orden {orden.codigo_pedido} registrada con INCIDENCIA."}
        except OrdenEnvioSCM.DoesNotExist:
            return {"success": False, "message": "Guía no encontrada"}
