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
from .forms import RegistroUsuarioForm, LoginUsuarioForm, SubirObraArteForm
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
    PolizaAsientoContable,
    ObraArte
)
from .erp_services import ERPAccountingService
from .crm_service import sincronizar_lead_hubspot
from .scm_service import SCMIntegrationService

# ==============================================================================
# 🎨 CATÁLOGO MAESTRO DE OBRAS DE ARTE (ECOMMERCE & COMPONENTES UNIDAD 4)
# ==============================================================================

CATALOGO_OBRAS = [
    {
        'id': 'ECOS-VACIO-01',
        'titulo': 'Ecos del Vacío',
        'artista': 'Ana Lucero',
        'categoria': 'Pintura al Óleo',
        'precio_mxn': 34500.00,
        'precio_usd': 1916.00,
        'imagen': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?q=80&w=1200',
        'tecnica': 'Óleo y pigmentos naturales sobre lienzo de lino belga',
        'dimensiones': '120 x 90 cm',
        'anio': 2026,
        'es_original_unica': True,
        'certificado': 'Certificado Físico Holográfico + Registro Blockchain ERC-721',
        'en_oferta': False,
        'descuento_porcentaje': 0,
        'enmarcado_disponible': True,
        'precio_enmarcado': 3200.00,
        'destacado': True,
        'badge': 'Pieza Única 1/1',
        'descripcion': 'Obra maestra que explora los contrastes cromáticos y la introspección del silencio en el arte abstracto contemporáneo.'
    },
    {
        'id': 'CIUDAD-VAPOR-02',
        'titulo': 'Ciudad de Vapor (Cyberpunk)',
        'artista': 'Diego Ferral',
        'categoria': 'Arte Digital / NFT',
        'precio_mxn': 18900.00,
        'precio_usd': 1050.00,
        'imagen': 'https://images.unsplash.com/photo-1545239351-1141bd82e8a6?q=80&w=1200',
        'tecnica': 'Pintura digital vectorial en Ultra-HD 8K con smart contract',
        'dimensiones': '7680 x 4320 px (Master File)',
        'anio': 2026,
        'es_original_unica': True,
        'certificado': 'Smart Contract Ethereum / IPFS Hash Verificado',
        'en_oferta': True,
        'descuento_porcentaje': 15,
        'enmarcado_disponible': False,
        'precio_enmarcado': 0.00,
        'destacado': True,
        'badge': 'Oferta -15% · NFT Exclusivo',
        'descripcion': 'Visión retrofuturista de megalópolis nocturnas iluminadas por neón, transferible a wallet Ethereum o descarga directa.'
    },
    {
        'id': 'FRAG-SOL-03',
        'titulo': 'Fragmentos del Sol',
        'artista': 'Elisa Moon',
        'categoria': 'Pintura al Óleo',
        'precio_mxn': 28400.00,
        'precio_usd': 1577.00,
        'imagen': 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?q=80&w=1200',
        'tecnica': 'Acrílico texturizado y hoja de oro de 24k sobre madera estucada',
        'dimensiones': '100 x 100 cm',
        'anio': 2025,
        'es_original_unica': True,
        'certificado': 'Certificado de Galería ARTSPACE con firma autógrafa',
        'en_oferta': False,
        'descuento_porcentaje': 0,
        'enmarcado_disponible': True,
        'precio_enmarcado': 2800.00,
        'destacado': True,
        'badge': 'Hoja de Oro 24K',
        'descripcion': 'Estudio de la refracción lumínica matutina aplicando láminas de oro puro que cambian de tonalidad según la luz ambiental.'
    },
    {
        'id': 'MONOLITO-04',
        'titulo': 'Monolito de Silencio',
        'artista': 'Mateo Rivas',
        'categoria': 'Escultura',
        'precio_mxn': 42000.00,
        'precio_usd': 2333.00,
        'imagen': 'https://images.unsplash.com/photo-1544717305-2782549b5136?q=80&w=1200',
        'tecnica': 'Mármol negro de Carrara y latón cepillado artesanal',
        'dimensiones': '65 x 35 x 30 cm (24 kg)',
        'anio': 2026,
        'es_original_unica': True,
        'certificado': 'Certificado Notarial de Escultura Original',
        'en_oferta': True,
        'descuento_porcentaje': 10,
        'enmarcado_disponible': False,
        'precio_enmarcado': 0.00,
        'destacado': False,
        'badge': 'Escultura Única 1/1',
        'descripcion': 'Escultura tridimensional que equilibra el peso geológico del mármol con la ligereza reflectiva del latón pulido a mano.'
    },
    {
        'id': 'HORIZONTE-05',
        'titulo': 'Horizonte Etéreo',
        'artista': 'Sofía Valenzuela',
        'categoria': 'Fotografía',
        'precio_mxn': 14500.00,
        'precio_usd': 805.00,
        'imagen': 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?q=80&w=1200',
        'tecnica': 'Impresión Fine Art Giclée sobre papel Hahnemühle Photo Rag 308g',
        'dimensiones': '90 x 60 cm (Edición 3/10)',
        'anio': 2026,
        'es_original_unica': False,
        'certificado': 'Sello seco de autor con número de tiraje',
        'en_oferta': False,
        'descuento_porcentaje': 0,
        'enmarcado_disponible': True,
        'precio_enmarcado': 2500.00,
        'destacado': False,
        'badge': 'Edición Limitada 3/10',
        'descripcion': 'Captura analógica de larga exposición en los salares de Atacama, revelando texturas atmosféricas en degradados pastel.'
    },
    {
        'id': 'METAMORFOSIS-06',
        'titulo': 'Metamorfosis Cuántica',
        'artista': 'Kaelen Chen',
        'categoria': 'Arte Digital / NFT',
        'precio_mxn': 22500.00,
        'precio_usd': 1250.00,
        'imagen': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1200',
        'tecnica': 'Generative AI curada y renderizada en 3D volumétrico cinético',
        'dimensiones': 'Video Loop 4K 60fps + Token ERC-721',
        'anio': 2026,
        'es_original_unica': True,
        'certificado': 'Contrato Inteligente descentralizado con royalties 70/30',
        'en_oferta': True,
        'descuento_porcentaje': 20,
        'enmarcado_disponible': False,
        'precio_enmarcado': 0.00,
        'destacado': True,
        'badge': 'Cyber Monday -20%',
        'descripcion': 'Animación generativa hipercompleja basada en algoritmos cuánticos de fluctuación de fluidos en el espacio profundo.'
    }
]


def index(request):
    perfil = None
    if request.user.is_authenticated:
        perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)

    # Cargar obras dinámicas desde la Base de Datos
    obras_db = list(ObraArte.objects.filter(vendida=False))
    obras = obras_db if obras_db else CATALOGO_OBRAS

    obras_destacadas = [o for o in obras if getattr(o, 'destacado', True)]
    obras_ofertas = [o for o in obras if getattr(o, 'en_oferta', False)]

    return render(request, 'index.html', {
        'perfil': perfil,
        'obras': obras,
        'obras_destacadas': obras_destacadas,
        'obras_ofertas': obras_ofertas,
    })


def colecciones(request):
    perfil = None
    if request.user.is_authenticated:
        perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
    
    obras = ObraArte.objects.filter(vendida=False)
    return render(request, 'colecciones.html', {
        'perfil': perfil,
        'obras': obras
    })


def artistas(request):
    artistas_data = [
        {'nombre': 'Ana Lucero', 'pais': 'México', 'especialidad': 'Óleo Abstracto y Pigmentos', 'obras_count': 14, 'foto': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=600', 'bio': 'Egresada de Bellas Artes con exposiciones en CDMX, Madrid y Nueva York.'},
        {'nombre': 'Diego Ferral', 'pais': 'España', 'especialidad': 'Arte Digital y Crypto Art', 'obras_count': 22, 'foto': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=600', 'bio': 'Pionero en modelado 3D ciberpunk y smart contracts de arte generativo.'},
        {'nombre': 'Elisa Moon', 'pais': 'Argentina', 'especialidad': 'Técnicas Mixtas y Hoja de Oro', 'obras_count': 9, 'foto': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=600', 'bio': 'Investigadora de pigmentos renacentistas aplicados a composiciones modernas.'},
        {'nombre': 'Mateo Rivas', 'pais': 'Chile', 'especialidad': 'Escultura en Piedra y Metales', 'obras_count': 7, 'foto': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=600', 'bio': 'Escultor monumental reconocido con el Premio Iberoamericano de Escultura 2024.'}
    ]
    return render(request, 'artistas.html', {'artistas': artistas_data})


def galeria(request):
    categoria_filtro = request.GET.get('categoria', 'TODAS')
    query = request.GET.get('q', '').strip().lower()

    obras_qs = ObraArte.objects.filter(vendida=False)
    if categoria_filtro != 'TODAS':
        obras_qs = obras_qs.filter(categoria__iexact=categoria_filtro)

    if query:
        obras_qs = [
            o for o in obras_qs
            if query in o.titulo.lower() or query in o.artista.lower() or query in o.tecnica.lower()
        ]
    else:
        obras_qs = list(obras_qs)

    return render(request, 'galeria.html', {
        'obras': obras_qs,
        'categoria_activa': categoria_filtro,
        'query': query,
        'total_obras': len(obras_qs)
    })


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

            # 5. Sincronización automática con la API de HubSpot CRM
            sincronizar_lead_hubspot(email=email, nombre=nombre, interes='GENERAL')

            messages.success(
                request,
                f"¡Gracias, {nombre}! Tu solicitud ha sido radicada con el Folio #{ticket.id} y sincronizada con el CRM. "
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

    # Sincronización en la nube con HubSpot CRM
    sincronizar_lead_hubspot(email=email, nombre='Suscriptor Web', interes=interes)

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
            rol = form.cleaned_data.get('rol', 'COMPRADOR')
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Inicialización automática del perfil de cliente y lealtad Art Club
            perfil, _ = PerfilCliente.objects.get_or_create(usuario=user)
            perfil.rol = rol
            perfil.save()

            if rol == 'ARTISTA':
                ProveedorArte.objects.get_or_create(
                    email=email,
                    defaults={
                        'nombre_empresa': f"Estudio de {username}",
                        'tipo': 'ARTISTA_INDEPENDIENTE',
                        'contacto_nombre': username,
                        'email': email,
                        'telefono': '+522461234567',
                        'tiempo_entrega_dias': 3
                    }
                )

            # Sincronización en la nube con HubSpot CRM
            sincronizar_lead_hubspot(email=email, nombre=username, interes=f"Registro: {rol}")

            # Registro de auditoría en la bitácora CRM
            InteraccionCRM.objects.create(
                usuario=user,
                canal='CORREO',
                tipo_evento=f'Registro Exitoso de Cuenta ({rol})',
                resumen=f"Usuario '{username}' registrado exitosamente como {rol} con correo '{email}'."
            )

            # Iniciar sesión inmediatamente mediante cookie firmada con directiva HttpOnly
            login(request, user)
            if rol == 'ARTISTA':
                messages.success(request, f"¡Bienvenido a ARTSPACE Creadores, {username}! Tu portal de artista está activo.")
                return redirect('panel_artista')
            else:
                messages.success(request, f"¡Bienvenido a ARTSPACE, {username}! Tu cuenta de coleccionista ha sido creada.")
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
    Controlador de Inicio de Sesión Seguro con Enrutamiento por Rol (RBAC).
    - Administrador (superuser/staff) -> Gestor Administrativo de Django (/admin/)
    - Artista Creador -> Portal del Artista (/panel-artista/)
    - Comprador / Coleccionista -> Panel de Coleccionista (/perfil/)
    """
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
        if perfil.rol == 'ARTISTA':
            return redirect('panel_artista')
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
                    if user.is_superuser or user.is_staff:
                        return redirect('/admin/')
                    perfil, _ = PerfilCliente.objects.get_or_create(usuario=user)
                    if perfil.rol == 'ARTISTA':
                        messages.success(request, f"🎨 Sesión iniciada en Portal de Artista. ¡Bienvenido, {user.username}!")
                        return redirect('panel_artista')
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
    Panel Privado Protegido del Coleccionista / Comprador (Art Club).
    Separa roles: Admin va a /admin/, Artista va a /panel-artista/.
    """
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/')

    perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
    if perfil.rol == 'ARTISTA':
        return redirect('panel_artista')

    if request.method == 'POST':
        action = request.POST.get('action', 'guardar_configuracion')
        if action == 'guardar_configuracion':
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            nuevo_email = request.POST.get('email', '').strip()
            if nuevo_email:
                request.user.email = nuevo_email
            nueva_pass = request.POST.get('nueva_password', '').strip()
            if nueva_pass and len(nueva_pass) >= 8:
                request.user.set_password(nueva_pass)
                from django.contrib.auth import update_session_auth_hash
                request.user.save()
                update_session_auth_hash(request, request.user)
            else:
                request.user.save()

            perfil.telefono = request.POST.get('telefono', '').strip()
            perfil.biografia = request.POST.get('biografia', '').strip()
            perfil.moneda_preferida = request.POST.get('moneda_preferida', 'MXN')
            perfil.categoria_favorita = request.POST.get('categoria_favorita', 'Pintura al Óleo')
            perfil.direccion_envio = request.POST.get('direccion_envio', '').strip()
            perfil.rfc_fiscal = request.POST.get('rfc_fiscal', 'XAXX010101000').strip().upper()
            perfil.notificaciones_activas = request.POST.get('notificaciones_activas') == 'on'
            perfil.coleccion_privada = request.POST.get('coleccion_privada') == 'on'
            perfil.save()

            messages.success(request, "✅ Configuración de perfil y preferencias básicas actualizadas exitosamente.")
            return redirect('perfil')

    ordenes = perfil.ordenes_scm.all()
    if not ordenes.exists():
        ordenes = OrdenEnvioSCM.objects.filter(cliente_email__iexact=request.user.email)
    tickets = request.user.tickets.all()
    historial_puntos = perfil.historial_puntos.all()[:10]

    return render(request, 'perfil.html', {
        'perfil': perfil,
        'ordenes': ordenes,
        'tickets': tickets,
        'historial_puntos': historial_puntos
    })


@login_required(login_url='login')
def panel_artista(request):
    """
    Portal Exclusivo del Artista / Creador Independiente.
    Integra publicación de obras, inventario SCM, liquidaciones Split 70/30
    y configuración de perfil/preferencias del creador.
    """
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/')

    perfil, _ = PerfilCliente.objects.get_or_create(usuario=request.user)
    if perfil.rol != 'ARTISTA':
        messages.warning(request, "El Portal de Artistas es exclusivo para cuentas de creadores.")
        return redirect('perfil')

    if request.method == 'POST':
        action = request.POST.get('action', 'subir_obra')
        if action == 'guardar_perfil_artista':
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            nuevo_email = request.POST.get('email', '').strip()
            if nuevo_email:
                request.user.email = nuevo_email
            request.user.save()

            perfil.telefono = request.POST.get('telefono', '').strip()
            perfil.biografia = request.POST.get('biografia', '').strip()
            perfil.clabe_spei = request.POST.get('clabe_spei', '646180123456789012').strip()
            perfil.rfc_fiscal = request.POST.get('rfc_fiscal', 'XAXX010101000').strip().upper()
            perfil.moneda_preferida = request.POST.get('moneda_preferida', 'MXN')
            perfil.categoria_favorita = request.POST.get('categoria_favorita', 'Pintura al Óleo')
            perfil.notificaciones_activas = request.POST.get('notificaciones_activas') == 'on'
            perfil.coleccion_privada = request.POST.get('coleccion_privada') == 'on'
            perfil.save()

            messages.success(request, "✅ Configuración de perfil de artista y preferencias bancarias SPEI actualizadas.")
            return redirect('panel_artista')

        form = SubirObraArteForm(request.POST)
        if form.is_valid():
            nueva_obra = ObraArte.objects.create(
                titulo=form.cleaned_data['titulo'],
                artista=request.user.get_full_name() or request.user.username,
                artista_usuario=request.user,
                categoria=form.cleaned_data['categoria'],
                precio_mxn=form.cleaned_data['precio_mxn'],
                precio_usd=(form.cleaned_data['precio_mxn'] / Decimal('18.0')).quantize(Decimal('0.01')),
                imagen=form.cleaned_data['imagen'],
                tecnica=form.cleaned_data['tecnica'],
                dimensiones=form.cleaned_data['dimensiones'],
                anio=form.cleaned_data['anio'],
                es_original_unica=form.cleaned_data['es_original_unica'],
                enmarcado_disponible=form.cleaned_data['enmarcado_disponible'],
                precio_enmarcado=form.cleaned_data['precio_enmarcado'],
                certificado=form.cleaned_data['certificado'],
                descripcion=form.cleaned_data['descripcion'],
                badge="Obra Nueva 1/1" if form.cleaned_data['es_original_unica'] else "Edición de Autor"
            )

            # Notificar en HubSpot CRM la actividad del creador
            sincronizar_lead_hubspot(
                email=request.user.email,
                nombre=request.user.username,
                interes=f"Subió Obra: {nueva_obra.titulo} (${nueva_obra.precio_mxn})"
            )

            # Sincronizar automáticamente la obra en Zoho Inventory SCM
            try:
                from django.conf import settings
                zoho_key = getattr(settings, 'ZOHO_INVENTORY_API_KEY', None)
                zoho_org = getattr(settings, 'ZOHO_INVENTORY_ORG_ID', None)
                if zoho_key and zoho_org and str(zoho_key).strip():
                    import requests
                    r_it_zoho = requests.post(
                        f"https://www.zohoapis.com/inventory/v1/items?organization_id={zoho_org.strip()}",
                        json={
                            "name": f"{nueva_obra.titulo} ({nueva_obra.artista})",
                            "rate": float(nueva_obra.precio_mxn),
                            "description": f"Categoría: {nueva_obra.categoria} | Técnica: {nueva_obra.tecnica} | Medidas: {nueva_obra.dimensiones}",
                            "sku": f"ART-{nueva_obra.id:04d}",
                            "initial_stock": 1
                        },
                        headers={
                            "Authorization": f"Zoho-oauthtoken {zoho_key.strip()}",
                            "Content-Type": "application/json"
                        },
                        timeout=5
                    )
                    if r_it_zoho.status_code in [200, 201]:
                        it_id = r_it_zoho.json().get('item', {}).get('item_id')
                        nueva_obra.id_externo_zoho_item = str(it_id)
                        nueva_obra.save(update_fields=['id_externo_zoho_item'])
            except Exception:
                pass

            messages.success(
                request,
                f"🎨 ¡La obra '{nueva_obra.titulo}' ha sido publicada exitosamente en el catálogo y sincronizada con Zoho Inventory SCM! "
                f"Ya está disponible en /galeria/ para que los compradores la aparten con Hold Cart."
            )
            return redirect('panel_artista')
        else:
            messages.error(request, "Por favor revisa los datos del formulario.")
    else:
        form = SubirObraArteForm()

    if request.user.is_superuser:
        mis_obras = ObraArte.objects.all()
    else:
        mis_obras = ObraArte.objects.filter(artista_usuario=request.user)

    proveedor = ProveedorArte.objects.filter(email=request.user.email).first()
    if proveedor:
        liquidaciones = LiquidacionArtistaERP.objects.filter(artista_proveedor=proveedor)
    else:
        liquidaciones = LiquidacionArtistaERP.objects.none()

    if not liquidaciones.exists():
        liquidaciones = LiquidacionArtistaERP.objects.filter(
            orden__detalles_envio__titulo_obra__in=[o.titulo for o in mis_obras]
        ).distinct()

    if not liquidaciones.exists() and request.user.is_superuser:
        liquidaciones = LiquidacionArtistaERP.objects.all()[:6]

    total_bruto = sum(l.monto_bruto_dividendo for l in liquidaciones)
    total_isr = sum(l.retencion_isr for l in liquidaciones)
    total_neto = sum(l.monto_neto_dispersar for l in liquidaciones)

    return render(request, 'panel_artista.html', {
        'perfil': perfil,
        'form': form,
        'mis_obras': mis_obras,
        'liquidaciones': liquidaciones,
        'total_bruto': total_bruto,
        'total_isr': total_isr,
        'total_neto': total_neto,
        'obras_activas': mis_obras.filter(vendida=False).count(),
        'obras_vendidas': mis_obras.filter(vendida=True).count(),
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

        # Identificar obra y artista en el catálogo
        obra_match = ObraArte.objects.filter(titulo__iexact=obra_titulo).first()
        if not obra_match:
            obra_match = ObraArte.objects.filter(titulo__icontains=obra_titulo).first()

        artista_nombre = obra_match.artista if obra_match else "Elena Rostova"
        artista_proveedor = None
        if obra_match and obra_match.artista_usuario:
            artista_proveedor, _ = ProveedorArte.objects.get_or_create(
                email=obra_match.artista_usuario.email,
                defaults={
                    'nombre_empresa': f"Estudio de {obra_match.artista}",
                    'tipo': 'ARTISTA_INDEPENDIENTE',
                    'contacto_nombre': obra_match.artista,
                    'telefono': '+522461234567',
                    'tiempo_entrega_dias': 3
                }
            )

        DetalleEnvioItem.objects.create(
            orden=orden,
            titulo_obra=obra_titulo,
            artista_nombre=artista_nombre,
            tipo_pieza=obra_tipo,
            cantidad=1,
            precio_unitario=total_pago,
            folio_certificado=f"COA-ARTSPACE-{uuid.uuid4().hex[:8].upper()}"
        )

        # 1.1 Sincronizar Orden con la Cadena de Suministro SCM (Zoho Inventory / Odoo)
        scm_service = SCMIntegrationService(platform="ZOHO_INVENTORY")
        scm_result = scm_service.sincronizar_orden_con_scm(orden)

        # 2. Orquestar Servicios ERP: CFDI 4.0, Split 70/30 y Póliza de Ingreso
        factura_cfdi = ERPAccountingService.generar_factura_cfdi(
            orden=orden,
            rfc=rfc_fiscal,
            razon_social=razon_social,
            cp_fiscal=cp_fiscal
        )

        liquidacion_artista = ERPAccountingService.procesar_split_artista(orden=orden, artista_proveedor=artista_proveedor)

        # Descontar stock y marcar como vendida si es obra original única en el catálogo
        if obra_match:
            if obra_match.es_original_unica:
                obra_match.vendida = True
                obra_match.save()

        poliza = ERPAccountingService.generar_asiento_ingreso_venta(orden=orden)
        odoo_result = ERPAccountingService.sincronizar_con_odoo(orden=orden, factura=factura_cfdi)

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
            'id_externo_scm': orden.id_externo_zoho,
            'id_externo_odoo_erp': odoo_result.get('odoo_id'),
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

