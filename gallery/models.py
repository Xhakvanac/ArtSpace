from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid


# ==========================================
# 1. MODELOS CRM (CLIENTES Y FIDELIZACIÓN)
# ==========================================

class LeadProspecto(models.Model):
    INTERES_CHOICES = [
        ('DIGITAL', 'Arte Digital / NFTs'),
        ('FISICO', 'Pintura y Escultura Física'),
        ('GENERAL', 'Interés General / Ambos')
    ]
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    nombre = models.CharField(max_length=100, blank=True, default="Coleccionista Prospecto", verbose_name="Nombre")
    interes_principal = models.CharField(max_length=15, choices=INTERES_CHOICES, default='GENERAL', verbose_name="Interés de Arte")
    origen = models.CharField(max_length=50, default='FOOTER_NEWSLETTER', verbose_name="Canal de Captación")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Lead / Prospecto"
        verbose_name_plural = "Leads / Prospectos"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre} ({self.email})"


class InteraccionCRM(models.Model):
    CANAL_CHOICES = [
        ('TICKET_WEB', 'Ticket Web'),
        ('CHATBOT', 'Chatbot FAQ Interactivo'),
        ('WHATSAPP', 'WhatsApp Business'),
        ('CORREO', 'Correo Electrónico')
    ]
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='interacciones', verbose_name="Usuario")
    lead = models.ForeignKey(LeadProspecto, on_delete=models.SET_NULL, null=True, blank=True, related_name='interacciones', verbose_name="Lead")
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, verbose_name="Canal de Comunicación")
    tipo_evento = models.CharField(max_length=100, default='CONSULTA_GENERAL', verbose_name="Tipo de Interacción")
    resumen = models.TextField(verbose_name="Resumen de la Interacción")
    fecha_interaccion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Interacción de Cliente"
        verbose_name_plural = "Bitácora de Interacciones Omnicanal"
        ordering = ['-fecha_interaccion']

    def __str__(self):
        return f"[{self.canal}] {self.tipo_evento} - {self.fecha_interaccion.strftime('%Y-%m-%d %H:%M')}"


class OportunidadPipeline(models.Model):
    ETAPA_CHOICES = [
        ('PROSPECCION', '1. Prospección'),
        ('CONTACTADO', '2. Contactado'),
        ('CALIFICADO', '3. Calificado'),
        ('PROPUESTA', '4. Propuesta / Cotización'),
        ('GANADO', '5. Cerrado Ganado'),
        ('PERDIDO', '6. Cerrado Perdido')
    ]
    lead = models.ForeignKey(LeadProspecto, on_delete=models.CASCADE, related_name='oportunidades', verbose_name="Lead / Prospecto")
    titulo = models.CharField(max_length=150, verbose_name="Obra o Trato de Interés")
    monto_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Monto Estimado (MXN)")
    etapa = models.CharField(max_length=20, choices=ETAPA_CHOICES, default='PROSPECCION', verbose_name="Etapa Comercial")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Apertura")
    fecha_cierre_esperada = models.DateField(null=True, blank=True, verbose_name="Fecha Cierre Estimada")

    class Meta:
        verbose_name = "Oportunidad de Venta"
        verbose_name_plural = "Pipeline de Ventas"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} - ${self.monto_estimado:,.2f} ({self.get_etapa_display()})"


class PerfilCliente(models.Model):
    TIER_CHOICES = [
        ('EXPLORER', 'Art Explorer (Bronce)'),
        ('COLLECTOR', 'Art Collector (Plata)'),
        ('PATRON', 'VIP Patron (Oro)')
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_crm', verbose_name="Usuario")
    puntos_fidelidad = models.PositiveIntegerField(default=0, verbose_name="Puntos de Arte Acumulados")
    nivel_tier = models.CharField(max_length=15, choices=TIER_CHOICES, default='EXPLORER', verbose_name="Nivel de Lealtad (Tier)")
    total_gastado = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Gasto Acumulado (MXN)")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono / WhatsApp")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Perfil de Cliente CRM"
        verbose_name_plural = "Perfiles de Clientes (Fidelización)"

    def __str__(self):
        return f"Perfil de {self.usuario.username} ({self.get_nivel_tier_display()}) - {self.puntos_fidelidad} pts"

    def acreditar_puntos(self, monto_gasto, concepto="Compra en galería"):
        puntos = int((float(monto_gasto) / 100.0) * 10)
        if puntos > 0:
            self.puntos_fidelidad += puntos
            self.total_gastado += models.Decimal(str(monto_gasto)) if hasattr(models, 'Decimal') else monto_gasto
            self._actualizar_tier()
            self.save()
            PuntosHistorial.objects.create(perfil=self, cantidad_puntos=puntos, concepto=concepto)
        return puntos

    def _actualizar_tier(self):
        if self.puntos_fidelidad >= 1500:
            self.nivel_tier = 'PATRON'
        elif self.puntos_fidelidad >= 500:
            self.nivel_tier = 'COLLECTOR'
        else:
            self.nivel_tier = 'EXPLORER'


class PuntosHistorial(models.Model):
    perfil = models.ForeignKey(PerfilCliente, on_delete=models.CASCADE, related_name='historial_puntos', verbose_name="Perfil")
    cantidad_puntos = models.IntegerField(verbose_name="Variación de Puntos (+/-)")
    concepto = models.CharField(max_length=200, verbose_name="Concepto de Movimiento")
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Transacción")

    class Meta:
        verbose_name = "Movimiento de Puntos"
        verbose_name_plural = "Historial de Puntos"
        ordering = ['-fecha_movimiento']

    def __str__(self):
        return f"{self.perfil.usuario.username}: {self.cantidad_puntos:+d} pts ({self.concepto})"


class TicketSoporte(models.Model):
    ESTADO_CHOICES = [
        ('NUEVO', 'Nuevo / Sin Asignar'),
        ('PROCESO', 'En Proceso de Atención'),
        ('RESUELTO', 'Resuelto / Solución Enviada'),
        ('CERRADO', 'Cerrado Definitivo')
    ]
    PRIORIDAD_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta / Urgente')
    ]
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets', verbose_name="Usuario Registrado")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Solicitante")
    email = models.EmailField(verbose_name="Correo Electrónico")
    asunto = models.CharField(max_length=200, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Descripción de la Consulta")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='NUEVO', verbose_name="Estado")
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA', verbose_name="Prioridad")
    respuesta = models.TextField(blank=True, null=True, verbose_name="Respuesta del Agente")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_resolucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Resolución")

    class Meta:
        verbose_name = "Ticket de Soporte"
        verbose_name_plural = "Tickets de Soporte"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Ticket #{self.id}: {self.asunto} ({self.get_estado_display()})"


# ==========================================
# 2. MODELOS SCM (CADENA DE SUMINISTRO)
# ==========================================

class ProveedorArte(models.Model):
    TIPO_CHOICES = [
        ('MOLDURAS_MADERA', 'Molduras y Marcos de Madera Noble (Nogal/Roble)'),
        ('PAPEL_BELLAS_ARTES', 'Papel de Algodón Fine Art (Hahnemühle / Canson)'),
        ('TINTAS_PIGMENTADAS', 'Tintas Pigmentadas UltraChrome K3'),
        ('EMBALAJE_SEGURIDAD', 'Materiales de Embalaje Rígido e Isotérmico'),
        ('ARTISTA_INDEPENDIENTE', 'Artista Independiente / Creador Directo')
    ]
    nombre_empresa = models.CharField(max_length=150, verbose_name="Nombre o Razón Social")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de Proveedor")
    contacto_nombre = models.CharField(max_length=100, verbose_name="Persona de Contacto")
    email = models.EmailField(verbose_name="Correo de Órdenes")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    tiempo_entrega_dias = models.PositiveIntegerField(default=5, verbose_name="Lead Time Promedio (Días)")
    calificacion_sla = models.DecimalField(max_digits=5, decimal_places=2, default=98.0, verbose_name="Cumplimiento SLA (%)")
    activo = models.BooleanField(default=True, verbose_name="Proveedor Activo")

    class Meta:
        verbose_name = "Proveedor SCM"
        verbose_name_plural = "Proveedores de la Cadena (SCM)"
        ordering = ['nombre_empresa']

    def __str__(self):
        return f"{self.nombre_empresa} ({self.get_tipo_display()})"


class OrdenEnvioSCM(models.Model):
    ESTRATEGIA_CHOICES = [
        ('HIBRIDO_PUSHPULL', 'Híbrido Push-Pull (Lámina Base Push + Enmarcado Pull)'),
        ('PUSH_STOCK', 'Push Puro (Print Preimpreso Inmediato)'),
        ('PULL_COMISION', 'Pull Puro (Obra Original / Encargo Directo a Artista)'),
        ('DIGITAL_INSTANTANEO', 'Digital Puro (Descarga Inmediata CDN/IPFS)')
    ]
    TRANSPORTISTA_CHOICES = [
        ('DHL_EXPRESS', 'DHL Express (Art Air Priority)'),
        ('FEDEX_PRIORITY', 'FedEx Priority Art Services'),
        ('ESTAFETA_TERRESTRE', 'Estafeta Terrestre Segura'),
        ('DESCARGA_DIGITAL', 'Servidor de Activos Digitales ARTSPACE CDN')
    ]
    ESTADO_CHOICES = [
        ('CHECKOUT_PAGADO', '1. Pedido Pagado / Pendiente de Asignación'),
        ('PREPARACION_CURATORIAL', '2. Curaduría y Picking en Almacén'),
        ('EMPACADO_ESPECIALIZADO', '3. Empacado Antichoque y Certificado Adjunto'),
        ('DESPACHADO_TRANSITO', '4. Recolectado / En Tránsito de Transporte'),
        ('EN_RUTA_ENTREGA', '5. En Ruta de Entrega (Última Milla)'),
        ('ENTREGADO', '6. Entregado Conforme al Cliente'),
        ('INCIDENCIA', '7. Incidencia / Retenido en Aduana o Paquetería'),
        ('CANCELADO', '8. Cancelado / Retorno Logística Inversa')
    ]
    codigo_pedido = models.CharField(max_length=30, unique=True, verbose_name="Código de Pedido (Folio)")
    cliente_nombre = models.CharField(max_length=120, verbose_name="Nombre del Destinatario")
    cliente_email = models.EmailField(verbose_name="Correo Electrónico")
    cliente_telefono = models.CharField(max_length=25, blank=True, verbose_name="Teléfono Destino")
    estrategia_flujo = models.CharField(max_length=25, choices=ESTRATEGIA_CHOICES, default='HIBRIDO_PUSHPULL', verbose_name="Estrategia Logística")
    transportista = models.CharField(max_length=25, choices=TRANSPORTISTA_CHOICES, default='DHL_EXPRESS', verbose_name="Transportista Asignado")
    numero_guia_awb = models.CharField(max_length=50, blank=True, verbose_name="Número de Guía / Tracking AWB")
    url_tracking = models.URLField(blank=True, verbose_name="URL de Seguimiento en Vivo")
    estado_logistico = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='CHECKOUT_PAGADO', verbose_name="Estado del Despacho")
    direccion_destino = models.TextField(verbose_name="Dirección Completa de Envío")
    ciudad_destino = models.CharField(max_length=100, default="Ciudad de México", verbose_name="Ciudad / Estado")
    pais_destino = models.CharField(max_length=60, default="México", verbose_name="País")
    peso_volumetrico_kg = models.DecimalField(max_digits=6, decimal_places=2, default=2.5, verbose_name="Peso Volumétrico (kg)")
    seguro_arte_incluido = models.BooleanField(default=True, verbose_name="Póliza de Seguro de Arte Incluida")
    monto_total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Monto Total Pagado (MXN)")
    comision_galeria_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Comisión ARTSPACE (MXN)")
    pago_artista_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Liquidación a Artista (MXN)")
    id_externo_zoho = models.CharField(max_length=60, blank=True, null=True, verbose_name="ID Externo (Zoho/Odoo SCM)")
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Checkout")
    fecha_despacho = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Real de Despacho")
    fecha_entrega_estimada = models.DateField(null=True, blank=True, verbose_name="Fecha Estimada de Entrega")
    fecha_entrega_real = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Real de Entrega")
    perfil_crm = models.ForeignKey(PerfilCliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_scm', verbose_name="Perfil CRM (Fidelización)")

    class Meta:
        verbose_name = "Orden de Envío SCM"
        verbose_name_plural = "Órdenes de Envío y Despacho (SCM)"
        ordering = ['-fecha_pedido']

    def __str__(self):
        return f"{self.codigo_pedido} - {self.cliente_nombre} ({self.get_estado_logistico_display()})"


class IncidenciaLogistica(models.Model):
    MOTIVO_CHOICES = [
        ('DEMORA_TRANSPORTE', 'Retraso de la Paquetería por Condiciones Climáticas'),
        ('DIRECCION_ERRONEA', 'Dirección Incompleta o Destinatario Ausente'),
        ('DANIO_EMBALAJE', 'Daño Reportado en Embalaje Exterior'),
        ('RETENCION_ADUANA', 'Retención por Inspección Aduanera Internacional'),
        ('RECLAMACION_CLIENTE', 'Inconformidad del Cliente con la Enmarcación')
    ]
    orden = models.ForeignKey(OrdenEnvioSCM, on_delete=models.CASCADE, related_name='incidencias', verbose_name="Orden Afectada")
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES, verbose_name="Causa de la Incidencia")
    descripcion = models.TextField(verbose_name="Bitácora de la Incidencia")
    resuelta = models.BooleanField(default=False, verbose_name="Incidencia Resuelta")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Reporte")
    ticket_crm = models.OneToOneField(TicketSoporte, on_delete=models.SET_NULL, null=True, blank=True, related_name='incidencia_scm', verbose_name="Ticket CRM Vinculado")

    class Meta:
        verbose_name = "Incidencia Logística"
        verbose_name_plural = "Mesa de Incidencias Logísticas (SCM)"
        ordering = ['-fecha_registro']


class DetalleEnvioItem(models.Model):
    TIPO_PIEZA_CHOICES = [
        ('ORIGINAL_UNICA', 'Obra Original Única'),
        ('PRINT_ENMARCADO', 'Print de Colección con Marco Nogal'),
        ('PRINT_ROLLO', 'Lámina Fine Art en Tubo Rígido'),
        ('NFT_DIGITAL', 'Licencia de Arte Digital 4K / NFT')
    ]
    orden = models.ForeignKey(OrdenEnvioSCM, on_delete=models.CASCADE, related_name='items', verbose_name="Orden de Envío")
    titulo_obra = models.CharField(max_length=150, verbose_name="Título de la Obra")
    artista_nombre = models.CharField(max_length=100, verbose_name="Nombre del Artista")
    tipo_pieza = models.CharField(max_length=30, choices=TIPO_PIEZA_CHOICES, default='PRINT_ENMARCADO', verbose_name="Tipo de Pieza")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Precio Unitario (MXN)")
    folio_certificado = models.CharField(max_length=50, blank=True, verbose_name="Folio de Certificado de Autenticidad")

    class Meta:
        verbose_name = "Ítem de Envío"
        verbose_name_plural = "Detalle de Piezas en Orden"


class InsumoAlmacen(models.Model):
    ABC_CHOICES = [
        ('A', 'Categoría A: Alto Valor / Rotación Crítica (Molduras Nogal, Cristales UV)'),
        ('B', 'Categoría B: Valor Intermedio (Papeles Fine Art, Barnices)'),
        ('C', 'Categoría C: Bajo Valor / Consumibles (Tubos, Cinta, Pluriball)')
    ]
    ESTRATEGIA_CHOICES = [
        ('PUSH', 'Push: Stock Preventivo Basado en Pronóstico'),
        ('PULL', 'Pull: Aprovisionamiento Sobre Demanda / Justo a Tiempo'),
        ('HIBRIDO', 'Híbrido Push-Pull: Insumo Estándar con Personalización Final')
    ]
    sku = models.CharField(max_length=30, unique=True, verbose_name="Código SKU")
    nombre = models.CharField(max_length=150, verbose_name="Descripción del Insumo")
    categoria_abc = models.CharField(max_length=2, choices=ABC_CHOICES, default='B', verbose_name="Clasificación ABC")
    estrategia = models.CharField(max_length=10, choices=ESTRATEGIA_CHOICES, default='HIBRIDO', verbose_name="Estrategia SCM")
    stock_actual = models.PositiveIntegerField(default=0, verbose_name="Stock Físico en Bodega")
    stock_seguridad = models.PositiveIntegerField(default=10, verbose_name="Stock de Seguridad (SS)")
    punto_reorden = models.PositiveIntegerField(default=25, verbose_name="Punto de Reorden (ROP)")
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Costo Unitario (MXN)")
    unidad_medida = models.CharField(max_length=20, default="Pieza", verbose_name="Unidad de Medida")
    proveedor = models.ForeignKey(ProveedorArte, on_delete=models.SET_NULL, null=True, related_name='insumos', verbose_name="Proveedor Principal")
    fecha_ultima_revision = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Insumo de Almacén"
        verbose_name_plural = "Inventario y Stock de Insumos (SCM)"
        ordering = ['categoria_abc', 'nombre']

    def __str__(self):
        return f"[{self.sku}] {self.nombre} (Stock: {self.stock_actual})"


# ==========================================
# 3. MODELOS ERP (FINANZAS Y FACTURACIÓN)
# ==========================================

class FacturaFiscalCFDI(models.Model):
    REGIMEN_CHOICES = [
        ('601', '601 - General de Ley Personas Morales'),
        ('605', '605 - Sueldos y Salarios'),
        ('612', '612 - Personas Físicas con Actividades Empresariales'),
        ('626', '626 - Régimen Simplificado de Confianza (RESICO)'),
        ('616', '616 - Sin obligaciones fiscales')
    ]
    USO_CHOICES = [
        ('G01', 'G01 - Adquisición de mercancías'),
        ('G03', 'G03 - Gastos en general'),
        ('S01', 'S01 - Sin efectos fiscales'),
        ('CP01', 'CP01 - Pagos')
    ]
    ESTADO_TIMBRADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Timbrado'),
        ('TIMBRADO', 'Timbrado Exitoso ante PAC / SAT'),
        ('ERROR', 'Error en Validación Fiscal'),
        ('CANCELADO', 'CFDI Cancelado')
    ]
    orden = models.OneToOneField(OrdenEnvioSCM, on_delete=models.CASCADE, related_name='factura_cfdi', verbose_name="Orden de Venta Asociada")
    uuid_fiscal = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="Folio Fiscal SAT (UUID)")
    rfc_receptor = models.CharField(max_length=13, default='XAXX010101000', verbose_name="RFC del Receptor")
    razon_social = models.CharField(max_length=150, default='PÚBLICO EN GENERAL', verbose_name="Razón Social / Nombre")
    codigo_postal_fiscal = models.CharField(max_length=5, default='90000', verbose_name="Código Postal Fiscal")
    regimen_fiscal = models.CharField(max_length=5, choices=REGIMEN_CHOICES, default='616', verbose_name="Régimen Fiscal")
    uso_cfdi = models.CharField(max_length=5, choices=USO_CHOICES, default='S01', verbose_name="Uso de CFDI")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Subtotal (Base Imponible)")
    iva_trasladado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="IVA Trasladado (16%)")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Total Facturado (MXN)")
    estado_timbrado = models.CharField(max_length=15, choices=ESTADO_TIMBRADO_CHOICES, default='PENDIENTE', verbose_name="Estado de Timbrado")
    odoo_invoice_id = models.IntegerField(null=True, blank=True, verbose_name="ID de Factura en Odoo ERP")
    sello_digital_sat = models.TextField(null=True, blank=True, verbose_name="Sello Digital SAT")
    cadena_original_sat = models.TextField(null=True, blank=True, verbose_name="Cadena Original de Certificación")
    url_xml = models.URLField(null=True, blank=True, verbose_name="Enlace de Descarga XML")
    url_pdf = models.URLField(null=True, blank=True, verbose_name="Enlace de Representación Impresa PDF")
    fecha_timbrado = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora de Timbrado")

    class Meta:
        verbose_name = "Factura Fiscal CFDI 4.0"
        verbose_name_plural = "ERP: Facturación Electrónica SAT (CFDI 4.0)"
        ordering = ['-fecha_timbrado']


class LiquidacionArtistaERP(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('PROVISIONADO', '1. Pasivo Provisionado en Contabilidad'),
        ('PROGRAMADO', '2. Pago Programado en Calendario de Tesorería'),
        ('DISPERSADO_SPEI', '3. Dispersión Realizada vía SPEI / CEP'),
        ('CONCILIADO', '4. Pago Conciliado en Estado de Cuenta')
    ]
    orden = models.OneToOneField(OrdenEnvioSCM, on_delete=models.CASCADE, related_name='liquidacion_artista_erp', verbose_name="Orden de Venta")
    artista_proveedor = models.ForeignKey(ProveedorArte, on_delete=models.CASCADE, related_name='liquidaciones', verbose_name="Artista Creador (Proveedor)")
    monto_bruto_dividendo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Dividendo Bruto Artista (70%)")
    retencion_isr = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Retención de ISR (1.25% RESICO o 10%)")
    retencion_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Retención de IVA (si aplica)")
    monto_neto_dispersar = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Monto Neto a Transferir al Artista")
    clabe_interbancaria = models.CharField(max_length=18, default='012180015678901234', verbose_name="CLABE Interbancaria Destino")
    clave_rastreo_spei = models.CharField(max_length=40, null=True, blank=True, verbose_name="Clave de Rastreo SPEI / Banxico")
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='PROVISIONADO', verbose_name="Estado de Tesorería")
    odoo_payment_id = models.IntegerField(null=True, blank=True, verbose_name="ID de Pago en Odoo ERP")
    fecha_programada_pago = models.DateField(null=True, blank=True, verbose_name="Fecha Programada de Dispersión")
    fecha_dispersion_real = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora de Transferencia SPEI")

    class Meta:
        verbose_name = "Liquidación a Artista (Split Payment)"
        verbose_name_plural = "ERP: Cuentas por Pagar a Artistas (Split 70/30)"
        ordering = ['-fecha_programada_pago']


class OrdenCompraInsumoERP(models.Model):
    ESTADO_PO_CHOICES = [
        ('BORRADOR_RFQ', '1. Solicitud de Presupuesto (RFQ Automática)'),
        ('APROBADA', '2. Orden de Compra Aprobada (PO Formal)'),
        ('EN_TRANSITO', '3. Insumos en Tránsito con Transportista'),
        ('RECIBIDO_ALMACEN', '4. Mercancía Recibida e Inspeccionada'),
        ('FACTURADA', '5. Factura de Proveedor Asentada en Contabilidad')
    ]
    codigo_po = models.CharField(max_length=30, unique=True, verbose_name="Código de Orden de Compra (PO)")
    insumo = models.ForeignKey(InsumoAlmacen, on_delete=models.CASCADE, related_name='ordenes_compra_erp', verbose_name="Insumo Crítico a Reabastecer")
    proveedor = models.ForeignKey(ProveedorArte, on_delete=models.CASCADE, related_name='ordenes_suministro_erp', verbose_name="Proveedor Homologado")
    cantidad_solicitada = models.PositiveIntegerField(verbose_name="Cantidad de Reposición (Lote EOQ)")
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Unitario Pactado")
    total_compra = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total de la Orden de Compra")
    estado_po = models.CharField(max_length=20, choices=ESTADO_PO_CHOICES, default='BORRADOR_RFQ', verbose_name="Estado de la Orden de Compra")
    odoo_purchase_id = models.IntegerField(null=True, blank=True, verbose_name="ID de Purchase Order en Odoo ERP")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_entrega_estimada = models.DateField(null=True, blank=True, verbose_name="Fecha de Entrega Estimada")

    class Meta:
        verbose_name = "Orden de Compra ERP (Abasto ROP)"
        verbose_name_plural = "ERP: Compras y Reabastecimiento Automatizado"
        ordering = ['-fecha_creacion']


class PolizaAsientoContable(models.Model):
    TIPO_POLIZA_CHOICES = [
        ('DIARIO', 'Póliza de Diario (Consumo de Insumos / COGS)'),
        ('INGRESOS', 'Póliza de Ingresos (Cobro de Ventas en Pasarela)'),
        ('EGRESOS', 'Póliza de Egresos (Dispersión a Artistas / Compras)')
    ]
    numero_poliza = models.CharField(max_length=30, unique=True, verbose_name="Número de Póliza Contable")
    tipo_poliza = models.CharField(max_length=10, choices=TIPO_POLIZA_CHOICES, default='DIARIO', verbose_name="Tipo de Póliza")
    concepto = models.CharField(max_length=255, verbose_name="Concepto del Asiento Contable")
    cuenta_cargo = models.CharField(max_length=100, default="501.01 - Costo de Mercancías Vendidas (COGS)", verbose_name="Cuenta de Cargo (Debe)")
    cuenta_abono = models.CharField(max_length=100, default="115.01 - Inventario de Materias Primas / Almacén", verbose_name="Cuenta de Abono (Haber)")
    monto_debe = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Debe (Cargo)")
    monto_haber = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Haber (Abono)")
    cuadrada = models.BooleanField(default=True, verbose_name="Póliza Cuadrada (Debe == Haber)")
    odoo_move_id = models.IntegerField(null=True, blank=True, verbose_name="ID de Póliza en Odoo General Ledger")
    fecha_asiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Contabilización")

    class Meta:
        verbose_name = "Póliza Contable ERP"
        verbose_name_plural = "ERP: Pólizas y Asientos de Libro Mayor"
        ordering = ['-fecha_asiento']

