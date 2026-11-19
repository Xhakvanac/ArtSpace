"""
Módulo de Integración API del CRM - ARTSPACE
Permite sincronizar eventos locales (captura de leads, clientes y compras)
con soluciones CRM en la nube (ej. HubSpot CRM API v3).
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

HUBSPOT_CONTACTS_API = "https://api.hubapi.com/crm/v3/objects/contacts"


def sincronizar_lead_hubspot(email, nombre="Coleccionista Prospecto", interes="GENERAL"):
    """
    Despacha una petición HTTP POST hacia la API de HubSpot CRM
    para registrar o actualizar un contacto en el pipeline comercial.
    """
    token = getattr(settings, 'HUBSPOT_ACCESS_TOKEN', None)
    if not token:
        logger.warning("CRM WARNING: 'HUBSPOT_ACCESS_TOKEN' no definido en settings. Operando en modo simulación.")
        return {
            'status': 'simulado',
            'mensaje': f'Lead {email} registrado localmente. Sincronización en la nube simulada exitosa.'
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "properties": {
            "email": email,
            "firstname": nombre,
            "company": f"ARTSPACE - Interés: {interes}"
        }
    }

    try:
        response = requests.post(HUBSPOT_CONTACTS_API, json=payload, headers=headers, timeout=5)
        if response.status_code in [200, 201]:
            logger.info(f"CRM SUCCESS: Lead {email} sincronizado exitosamente con HubSpot.")
            return {'status': 'sincronizado', 'codigo': response.status_code}
        else:
            logger.error(f"CRM API ERROR ({response.status_code}): {response.text}")
            return {'status': 'error', 'codigo': response.status_code, 'detalle': response.text}
    except requests.exceptions.RequestException as exc:
        logger.error(f"CRM CONNECTION ERROR: {exc}")
        return {'status': 'excepcion', 'detalle': str(exc)}
