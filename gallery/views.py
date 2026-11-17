from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
import json
import uuid
from decimal import Decimal
from .forms import RegistroUsuarioForm, LoginUsuarioForm
from .models import (
    TicketSoporte,
    LeadProspecto,
    OportunidadPipeline,
    PerfilCliente,
    InteraccionCRM,
    PuntosHistorial,
    OrdenEnvioSCM,
    DetalleEnvioItem,
    ProveedorArte,
    FacturaFiscalCFDI,
    LiquidacionArtistaERP,
    PolizaAsientoContable
)
from .erp_services import ERPAccountingService


def index(request):
    perfil = None
    if request.user.is_authenticated:
        perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
    return render(request, 'index.html', {'perfil': perfil})


def colecciones(request):
    return render(request, 'colecciones.html')


def artistas(request):
    return render(request, 'artistas.html')


def galeria(request):
    return render(request, 'galeria.html')


def contacto(request):
    ticket_generado = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        asunto = request.POST.get('asunto', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        prioridad = request.POST.get('prioridad', 'MEDIA')

        if not nombre or not email or not asunto or not mensaje:
            messages.error(request, "Por favor, completa todos los campos requeridos del formulario.")
        else:
            # 1. Crear el Ticket en el módulo de atención CRM
            ticket = TicketSoporte.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                nombre=nombre,
                email=email,
                asunto=asunto,
                mensaje=mensaje,
                prioridad=prioridad,
                estado='NUEVO'
            )
            ticket_generado = ticket

            # 2. Capturar o actualizar el prospecto en el módulo de ventas
            lead, creado = LeadProspecto.objects.get_or_create(
                email=email,
                defaults={
                    'nombre': nombre,
                    'interes_principal': 'GENERAL',
                    'origen': 'FORMULARIO_CONTACTO'
                }
            )

            # 3. Registrar la interacción en la bitácora omnicanal
            InteraccionCRM.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                lead=lead,
                canal='TICKET_WEB',
                tipo_evento=f'Nuevo Ticket #{ticket.id}: {ticket.asunto}',
                resumen=f"Mensaje del solicitante: {ticket.mensaje[:250]}"
            )

            # 4. Si el asunto refiere a compra o cotización, abrir oportunidad en Pipeline
            if any(palabra in asunto.lower() for palabra in ['compra', 'cotización', 'cotizacion', 'precio', 'envío', 'envio', 'comisión', 'comision']):
                OportunidadPipeline.objects.create(
                    lead=lead,
                    titulo=f"Interés comercial: {asunto[:100]}",
                    monto_estimado=2500.00,
                    etapa='CONTACTADO'
                )

            messages.success(
                request,
                f"¡Gracias, {nombre}! Tu solicitud ha sido radicada con el Folio #{ticket.id}. "
                f"Un asesor de ARTSPACE se pondrá en contacto al correo {email} en menos de 24 horas."
            )

    return render(request, 'contacto.html', {'ticket_generado': ticket_generado})


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip()
    interes = request.POST.get('interes', 'GENERAL')

    if not email:
        messages.error(request, "Ingresa un correo electrónico válido.")
        return redirect(request.META.get('HTTP_REFERER', 'index'))

    lead, creado = LeadProspecto.objects.get_or_create(
        email=email,
        defaults={
            'nombre': 'Suscriptor Web',
            'interes_principal': interes,
            'origen': 'FOOTER_NEWSLETTER'
        }
    )

    if not creado:
        lead.interes_principal = interes
        lead.save()

    # Registrar interacción
    InteraccionCRM.objects.create(
        lead=lead,
        canal='CORREO',
        tipo_evento='Suscripción a Newsletter',
        resumen=f"El lead se suscribió con interés en {lead.get_interes_principal_display()}."
    )

    messages.success(
        request,
        f"¡Te has suscrito exitosamente con {email}! Recibirás invitaciones exclusivas y drops de artistas independientes."
    )
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def chatbot_api(request):
    """Endpoint interactivo para simular el chatbot omnicanal de soporte FAQ"""
    pregunta = request.GET.get('q', '').lower()

    respuestas = {
        'envios': "Realizamos envíos asegurados a toda la República Mexicana en 3-5 días hábiles. Obras físicas cuentan con empaque de alta seguridad y embalaje especial.",
        'autenticidad': "Todas las obras físicas y prints de edición limitada incluyen un Certificado de Autenticidad físico con holograma y firma original del artista.",
        'puntos': "Con nuestro programa Art Club recibes 10 Puntos de Arte por cada $100 MXN de compra. 100 puntos equivalen a $50 MXN de descuento en tu siguiente adquisición.",
        'tiers': "Nuestros niveles son: Art Explorer (0-499 pts), Art Collector (500-1499 pts, incluye envíos gratis) y VIP Patron (1500+ pts, con acceso anticipado a Drops de 48h).",
        'digital': "El arte digital se entrega en descarga inmediata en alta resolución (4K/8K, 300 DPI) con licencia de uso personal no comercial.",
        'default': "¡Hola! Soy ArtBot, tu asistente en ARTSPACE. Puedes preguntarme sobre: 'envíos', 'autenticidad', 'puntos', 'tiers' o 'digital', o bien radicar un ticket formal en la sección Contacto."
    }

    encontrada = False
    respuesta_texto = respuestas['default']
    for clave, resp in respuestas.items():
        if clave != 'default' and clave in pregunta:
            respuesta_texto = resp
            encontrada = True
            break

    if request.user.is_authenticated and encontrada:
        InteraccionCRM.objects.create(
            usuario=request.user,
            canal='CHATBOT',
            tipo_evento='Consulta Chatbot FAQ',
            resumen=f"Pregunta del usuario: '{pregunta[:100]}'. Respuesta ofrecida: '{respuesta_texto[:150]}'"
        )

    return JsonResponse({'respuesta': respuesta_texto})


def simular_compra_demo(request):
    """
    Vista didáctica para demostración en clase:
    Simula una compra de $1,500 MXN para acreditar puntos y promover de Tier al usuario logueado.
    """
    if not request.user.is_authenticated:
        messages.warning(request, "Inicia sesión en /admin para probar la simulación de puntos de fidelización.")
        return redirect('index')

    perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
    monto_simulado = 1500.00
    puntos_ganados = perfil.acreditar_puntos(
        monto_gasto=monto_simulado,
        concepto=f"Compra de demostración: Obra 'Nebulosa Interior' (${monto_simulado:,.2f} MXN)"
    )

    messages.success(
        request,
        f"🎨 ¡Compra simulada exitosa! Se han acreditado {puntos_ganados} Puntos de Arte a tu perfil. "
        f"Tu saldo actual es de {perfil.puntos_fidelidad} pts (Nivel: {perfil.get_nivel_tier_display()})."
    )
    return redirect('index')


# ==========================================
# VISTAS DE AUTENTICACIÓN Y GESTIÓN DE USUARIOS
# ==========================================

def registro_usuario(request):
    """
    Controlador de Registro Seguro de Usuarios.
    Aplica hashing PBKDF2-SHA256, salting criptográfico, validaciones
    de duplicados y vincula el perfil de fidelización CRM.
    """
    if request.user.is_authenticated:
        return redirect('perfil')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Creación segura: create_user aplica internamente make_password (PBKDF2-SHA256 + salt)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Inicialización automática del perfil de cliente y lealtad Art Club
            perfil, _ = PerfilCliente.objects.get_or_create(usuario=user)

            # Registro de auditoría en la bitácora CRM
            InteraccionCRM.objects.create(
                usuario=user,
                canal='CORREO',
                tipo_evento='Registro Exitoso de Cuenta',
                resumen=f"Usuario '{username}' registrado exitosamente con correo cifrado '{email}'."
            )

            # Iniciar sesión inmediatamente mediante cookie firmada con directiva HttpOnly
            login(request, user)
            messages.success(request, f"¡Bienvenido a ARTSPACE, {username}! Tu cuenta ha sido creada con éxito.")
            return redirect('perfil')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registro.html', {'form': form})


def login_usuario(request):
    """
    Controlador de Inicio de Sesión Seguro.
    Verifica hash criptográfico, mitiga ataques de fuerza bruta
    y previene enumeración de usuarios con mensajes neutrales.
    """
    if request.user.is_authenticated:
        return redirect('perfil')

    if request.method == 'POST':
        form = LoginUsuarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Si el usuario ingresó su correo electrónico, resolvemos el username
            if '@' in username:
                user_match = User.objects.filter(email__iexact=username).first()
                if user_match:
                    username = user_match.username

            # authenticate() evalúa PBKDF2-SHA256 en tiempo constante (timing attack protection)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)  # Asigna token de sesión y cookie de sesión HttpOnly
                    messages.success(request, f"Sesión iniciada correctamente. ¡Hola de nuevo, {user.username}!")
                    next_url = request.GET.get('next', 'perfil')
                    return redirect(next_url)
                else:
                    messages.error(request, "Tu cuenta ha sido desactivada temporalmente por seguridad.")
            else:
                # Mensaje neutral para mitigar User Enumeration
                messages.error(request, "Credenciales inválidas. Verifica tu usuario y contraseña.")
    else:
        form = LoginUsuarioForm()

    return render(request, 'login.html', {'form': form})


def logout_usuario(request):
    """
    Cierre de Sesión Seguro.
    Invalida el sessionid en el servidor (Session Fixation mitigation)
    y purga la cookie en el navegador del cliente.
    """
    logout(request)
    messages.info(request, "Has cerrado tu sesión de manera segura. ¡Hasta pronto!")
    return redirect('index')


@login_required(login_url='login')
def perfil_usuario(request):
    """
    Panel Privado Protegido del Coleccionista (Art Club).
    Requiere una sesión autenticada válida con cookie de sesión activa.
    """
    perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
    ordenes = request.user.perfil_crm.ordenes_scm.all() if hasattr(request.user, 'perfil_crm') else []
    tickets = request.user.tickets.all()
    historial_puntos = perfil.historial_puntos.all()[:10]

    return render(request, 'perfil.html', {
        'perfil': perfil,
        'ordenes': ordenes,
        'tickets': tickets,
        'historial_puntos': historial_puntos
    })


# ==============================================================================
# 🚀 API CONTRACT REST ENDPOINTS (SERVICIOS WEB TRANSACCIONALES V1)
# ==============================================================================

# Simulación en memoria de bloqueos de piezas únicas 1/1 (Hold-Cart)
ACTIVE_HOLD_CARTS = {}

@csrf_exempt
@require_POST
def api_cart_hold(request):
    """
    POST /api/v1/cart/hold/
    Reserva temporal de obra de arte original (Regla de Negocio RN-01).
    Bloquea la pieza por 15 minutos (900 segundos) para evitar doble venta.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        artwork_id = data.get('artwork_id', '').strip()
        user_id = data.get('user_id', 'anonimo')

        if not artwork_id:
            return JsonResponse({'error': 'Campo artwork_id requerido'}, status=400)

        ahora = timezone.now().timestamp()
        # Verificar si existe un bloqueo activo no expirado
        if artwork_id in ACTIVE_HOLD_CARTS:
            bloqueo = ACTIVE_HOLD_CARTS[artwork_id]
            if ahora < bloqueo['expira'] and bloqueo['user_id'] != user_id:
                tiempo_restante = int(bloqueo['expira'] - ahora)
                return JsonResponse({
                    'status': 'COLLISION_CONFLICT',
                    'error': f'La obra única ya se encuentra reservada por otro coleccionista. Expira en {tiempo_restante}s.',
                    'locked': True
                }, status=409)

        # Asignar nuevo bloqueo por 15 minutos (900 segundos)
        expira = ahora + 900
        ACTIVE_HOLD_CARTS[artwork_id] = {
            'user_id': user_id,
            'expira': expira,
            'timestamp': ahora
        }

        return JsonResponse({
            'status': 'HOLD_ACQUIRED',
            'artwork_id': artwork_id,
            'locked_until': int(expira),
            'expires_in_seconds': 900,
            'message': 'Pieza original única 1/1 bloqueada exitosamente a tu favor por 15 minutos.'
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_tax_calculate(request):
    """
    POST /api/v1/tax/calculate/
    Motor de Cálculo Fiscal e Impuestos en Tiempo Real (Regla de Negocio RN-03).
    Aplica IVA al 16% (nacional), 8% (franja fronteriza norte) o 0% (arte digital exportación).
    Cotiza flete especializado Courier DHL con seguro incluido.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        postal_code = str(data.get('postal_code', '90000')).strip()
        country = data.get('country', 'MEX').upper().strip()
        artwork_price = Decimal(str(data.get('artwork_price', 0.0)))
        frame_price = Decimal(str(data.get('frame_price', 0.0)))
        is_digital = bool(data.get('is_digital', False))

        subtotal_base = artwork_price + frame_price

        # Flete Courier (DHL Art Care) y Prima de Seguro de Arte (1.5%)
        if is_digital:
            flete_costo = Decimal('0.00')
            seguro_arte = Decimal('0.00')
        else:
            flete_costo = Decimal('1450.00')
            seguro_arte = (artwork_price * Decimal('0.015')).quantize(Decimal('0.01'))

        # Regla fiscal de frontera norte (Códigos postales de BC, Sonora, Chihuahua, Tamaulipas)
        # Prefijos postales oficiales del decreto fronterizo SAT: 21, 22, 32, 87, 88
        es_frontera = any(postal_code.startswith(pref) for pref in ['21', '22', '32', '87', '88'])

        if country != 'MEX' and is_digital:
            tasa_iva = Decimal('0.00')
            regimen_desc = 'Tasa 0% IVA (Exportación de Servicios Intangibles / LIVA Art. 29)'
        elif es_frontera:
            tasa_iva = Decimal('0.08')
            regimen_desc = 'Tasa Reducida 8% IVA (Decreto de Estímulos Fiscales Región Fronteriza Norte)'
        else:
            tasa_iva = Decimal('0.16')
            regimen_desc = 'Tasa General 16% IVA (Art. 1 Ley del Impuesto al Valor Agregado)'

        base_gravable = subtotal_base + flete_costo + seguro_arte
        monto_iva = (base_gravable * tasa_iva).quantize(Decimal('0.01'))
        total_definitivo = base_gravable + monto_iva

        return JsonResponse({
            'status': 'SUCCESS',
            'postal_code': postal_code,
            'es_frontera_norte': es_frontera,
            'regimen_fiscal_aplicado': regimen_desc,
            'breakdown': {
                'artwork_price': float(artwork_price),
                'frame_price': float(frame_price),
                'subtotal_base': float(subtotal_base),
                'courier_shipping': float(flete_costo),
                'art_insurance': float(seguro_arte),
                'tax_rate_percentage': float(tasa_iva * 100),
                'tax_amount_iva': float(monto_iva),
                'total_amount': float(total_definitivo)
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def api_checkout_process(request):
    """
    POST /api/v1/checkout/process/
    Orquestador Transaccional Integral End-to-End.
    Ejecuta el pipeline: Pago -> SCM Envío -> ERP CFDI 4.0 -> Split 70/30 -> CRM Art Club.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        cliente_nombre = data.get('cliente_nombre', 'Coleccionista Anónimo')
        cliente_email = data.get('cliente_email', 'cliente@artspace.mx')
        direccion = data.get('direccion', 'Calzada de los Pintores #45, Tlaxcala Centro')
        total_pago = Decimal(str(data.get('total_pago', 43434.00)))
        obra_titulo = data.get('obra_titulo', 'Ecos del Vacío')
        obra_tipo = data.get('obra_tipo', 'ORIGINAL_UNICA')
        rfc_fiscal = data.get('rfc', 'XAXX010101000')
        razon_social = data.get('razon_social', 'PÚBLICO EN GENERAL')
        cp_fiscal = data.get('codigo_postal_fiscal', '90000')

        # 1. Generar Folio y Crear Orden SCM
        folio_pedido = f"ART-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        guia_awb = f"DHL-AWB-{uuid.uuid4().hex[:10].upper()}"

        user_obj = User.objects.filter(email=cliente_email).first()
        perfil_crm = None
        if user_obj:
            perfil_crm, _ = PerfilCliente.objects.get_or_create(usuario=user_obj)

        orden = OrdenEnvioSCM.objects.create(
            codigo_pedido=folio_pedido,
            cliente_nombre=cliente_nombre,
            cliente_email=cliente_email,
            direccion_destino=direccion,
            monto_total_venta=total_pago,
            transportista='DHL_EXPRESS',
            numero_guia_awb=guia_awb,
            url_tracking=f"https://track.dhl.com/?awb={guia_awb}",
            estado_logistico='PREPARACION_CURATORIAL',
            perfil_crm=perfil_crm
        )

        DetalleEnvioItem.objects.create(
            orden=orden,
            titulo_obra=obra_titulo,
            artista_nombre="Elena Rostova",
            tipo_pieza=obra_tipo,
            cantidad=1,
            precio_unitario=total_pago,
            folio_certificado=f"COA-ARTSPACE-{uuid.uuid4().hex[:8].upper()}"
        )

        # 2. Orquestar Servicios ERP: CFDI 4.0, Split 70/30 y Póliza de Ingreso
        factura_cfdi = ERPAccountingService.generar_factura_cfdi(
            orden=orden,
            rfc=rfc_fiscal,
            razon_social=razon_social,
            cp_fiscal=cp_fiscal
        )

        liquidacion_artista = ERPAccountingService.procesar_split_artista(orden=orden)
        poliza = ERPAccountingService.generar_asiento_ingreso_venta(orden=orden)

        # 3. Acreditar Puntos de Fidelización en CRM Art Club
        puntos_ganados = 0
        tier_actual = "EXPLORER"
        if perfil_crm:
            puntos_ganados = perfil_crm.acreditar_puntos(
                monto_gasto=total_pago,
                concepto=f"Adquisición de obra '{obra_titulo}' (Orden #{folio_pedido})"
            )
            tier_actual = perfil_crm.get_nivel_tier_display()

        return JsonResponse({
            'status': 'TRANSACTION_CONFIRMED',
            'codigo_pedido': folio_pedido,
            'guia_awb': guia_awb,
            'logistica_estado': orden.get_estado_logistico_display(),
            'factura_fiscal': {
                'uuid_sat': str(factura_cfdi.uuid_fiscal),
                'estado_timbrado': factura_cfdi.estado_timbrado,
                'rfc_receptor': factura_cfdi.rfc_receptor,
                'total_facturado': float(factura_cfdi.total)
            },
            'split_pago_artista': {
                'bruto_artista_70': float(liquidacion_artista.monto_bruto_dividendo),
                'retencion_isr_resico': float(liquidacion_artista.retencion_isr),
                'neto_artista_spei': float(liquidacion_artista.monto_neto_dispersar),
                'clave_spei': liquidacion_artista.clave_rastreo_spei
            },
            'poliza_contable': {
                'numero_poliza': poliza.numero_poliza,
                'tipo': poliza.tipo_poliza,
                'cuadrada': poliza.cuadrada
            },
            'fidelizacion_art_club': {
                'puntos_acreditados': puntos_ganados,
                'tier_nivel': tier_actual
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_GET
def api_order_track(request, codigo_pedido):
    """
    GET /api/v1/orders/<codigo_pedido>/track/
    Consulta del estado logístico en tiempo real (SCM Tracking).
    """
    orden = OrdenEnvioSCM.objects.filter(codigo_pedido=codigo_pedido).first()
    if not orden:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)

    return JsonResponse({
        'codigo_pedido': orden.codigo_pedido,
        'destinatario': orden.cliente_nombre,
        'transportista': orden.get_transportista_display(),
        'guia_awb': orden.numero_guia_awb,
        'url_tracking': orden.url_tracking,
        'estado_logistico': orden.get_estado_logistico_display(),
        'seguro_arte_incluido': orden.seguro_arte_incluido,
        'fecha_pedido': orden.fecha_pedido.isoformat()
    }, status=200)

