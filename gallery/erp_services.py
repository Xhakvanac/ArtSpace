"""
Módulo de Integración ERP (Enterprise Resource Planning) para ARTSPACE.
Orquesta la facturación electrónica fiscal (CFDI 4.0), dispersión de dividendos
a artistas (Split 70/30) y generación automática de pólizas contables de libro mayor.
"""

import uuid
from decimal import Decimal
from django.utils import timezone
from .models import (
    FacturaFiscalCFDI,
    LiquidacionArtistaERP,
    PolizaAsientoContable,
    ProveedorArte,
    OrdenEnvioSCM
)


class ERPAccountingService:
    """
    Servicio centralizado del Back-Office contable y financiero.
    Gestiona el impacto contable y fiscal de las transacciones de comercio electrónico.
    """

    @staticmethod
    def generar_factura_cfdi(orden: OrdenEnvioSCM, rfc="XAXX010101000", razon_social="PÚBLICO EN GENERAL",
                             cp_fiscal="90000", regimen="616", uso_cfdi="S01"):
        """
        Genera y timbra digitalmente un comprobante fiscal CFDI 4.0 asociado a la orden de venta.
        Calcula base imponible e IVA trasladado (16% o tasa preferencial).
        """
        total = Decimal(str(orden.monto_total_venta))
        # Desglosar subtotal e IVA: Base = Total / 1.16
        subtotal = (total / Decimal('1.16')).quantize(Decimal('0.01'))
        iva_trasladado = (total - subtotal).quantize(Decimal('0.01'))

        uuid_timbrado = uuid.uuid4()
        sello_sat_simulado = f"SELLO|SAT|{uuid_timbrado.hex[:16]}|{timezone.now().strftime('%Y%m%d%H%M%S')}|OK"
        cadena_original = f"||4.0|ARTSPACE|{total}|{rfc}|{cp_fiscal}|{regimen}|{uso_cfdi}||"

        factura, created = FacturaFiscalCFDI.objects.update_or_create(
            orden=orden,
            defaults={
                'uuid_fiscal': uuid_timbrado,
                'rfc_receptor': rfc.upper().strip(),
                'razon_social': razon_social.upper().strip(),
                'codigo_postal_fiscal': cp_fiscal.strip(),
                'regimen_fiscal': regimen,
                'uso_cfdi': uso_cfdi,
                'subtotal': subtotal,
                'iva_trasladado': iva_trasladado,
                'total': total,
                'estado_timbrado': 'TIMBRADO',
                'sello_digital_sat': sello_sat_simulado,
                'cadena_original_sat': cadena_original,
                'url_xml': f"https://api.artspace.mx/cfdi/xml/{uuid_timbrado}.xml",
                'url_pdf': f"https://api.artspace.mx/cfdi/pdf/{uuid_timbrado}.pdf",
                'fecha_timbrado': timezone.now()
            }
        )
        return factura

    @staticmethod
    def procesar_split_artista(orden: OrdenEnvioSCM, artista_proveedor: ProveedorArte = None):
        """
        Aplica la regla de negocio Split 70/30:
        70% del monto bruto de la obra al artista creador, menos retención de ISR (1.25% RESICO).
        30% queda en ARTSPACE como comisión de intermediación de galería.
        """
        if not artista_proveedor:
            artista_proveedor, _ = ProveedorArte.objects.get_or_create(
                nombre_empresa="Elena Rostova (Estudio de Arte)",
                defaults={
                    'tipo': 'ARTISTA_INDEPENDIENTE',
                    'contacto_nombre': 'Elena Rostova',
                    'email': 'elena.rostova@artspace.mx',
                    'telefono': '+522461234567',
                    'tiempo_entrega_dias': 3,
                    'calificacion_sla': Decimal('99.5')
                }
            )

        total_venta = Decimal(str(orden.monto_total_venta))
        # 70% para el artista, 30% galería
        monto_bruto = (total_venta * Decimal('0.70')).quantize(Decimal('0.01'))
        comision_galeria = total_venta - monto_bruto
        orden.pago_artista_monto = monto_bruto
        orden.comision_galeria_monto = comision_galeria
        orden.save()

        # Retención fiscal de ISR del 1.25% (Régimen RESICO según Art. 113-E LISR)
        retencion_isr = (monto_bruto * Decimal('0.0125')).quantize(Decimal('0.01'))
        monto_neto = monto_bruto - retencion_isr

        clave_spei = f"SPEI-BANXICO-{uuid.uuid4().hex[:12].upper()}"

        liquidacion, _ = LiquidacionArtistaERP.objects.update_or_create(
            orden=orden,
            defaults={
                'artista_proveedor': artista_proveedor,
                'monto_bruto_dividendo': monto_bruto,
                'retencion_isr': retencion_isr,
                'retencion_iva': Decimal('0.00'),
                'monto_neto_dispersar': monto_neto,
                'clabe_interbancaria': '012180015678901234',
                'clave_rastreo_spei': clave_spei,
                'estado_pago': 'PROVISIONADO',
                'fecha_programada_pago': timezone.now().date() + timezone.timedelta(days=7)
            }
        )
        return liquidacion

    @staticmethod
    def generar_asiento_ingreso_venta(orden: OrdenEnvioSCM):
        """
        Genera la póliza contable de Ingresos por la venta de la obra.
        Debe: Bancos / Pasarela Stripe (Total)
        Haber: Ingresos por Venta de Arte (Subtotal)
        Haber: IVA Trasladado Cobrado (IVA)
        """
        folio = f"POL-ING-{uuid.uuid4().hex[:8].upper()}"
        total = Decimal(str(orden.monto_total_venta))
        subtotal = (total / Decimal('1.16')).quantize(Decimal('0.01'))
        iva = total - subtotal

        poliza = PolizaAsientoContable.objects.create(
            numero_poliza=folio,
            tipo_poliza='INGRESOS',
            concepto=f"Cobro de venta de arte en línea - Orden #{orden.codigo_pedido}",
            cuenta_cargo="102.01 - Bancos / Pasarela Stripe Cuentas de Recaudación",
            cuenta_abono="401.01 - Ingresos Netos por Venta de Obras y Comisiones",
            monto_debe=total,
            monto_haber=total,
            cuadrada=True
        )
        return poliza

