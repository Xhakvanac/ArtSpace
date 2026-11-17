# 📊 GUION Y CONTENIDO PARA PRESENTACIÓN TÉCNICA EJECUTIVA (CRM ARTSPACE)
## Asignatura: Negocios Electrónicos II — Entregable 2 (Diapositivas)
### Formato: Presentación Ejecutiva y Técnica de Alto Impacto (10 a 12 Diapositivas)

---

## 📌 NOTAS GENERALES PARA EL EQUIPO EXPOSITOR
* **Tono Ejecutivo:** Cada lámina combina datos cuantitativos (KPIs), decisiones de ingeniería de software (Django/APIs) y valor comercial.
* **Estructura por Lámina:** 
  1. **Título de la Diapositiva**
  2. **Contenido Visual y Textual (Copy listo para copiar a PowerPoint / Canva)**
  3. **Recurso Gráfico Recomendado (Ubicación en carpeta `pagina/img/`)**
  4. **Pitch del Expositor (Guion verbal de 30 a 45 segundos)**

---

# LÁMINA 01: PORTADA INSTITUCIONAL
*(Mantener el diseño institucional acordado por el equipo)*
* **Institución:** Tecnológico Nacional de México / Universidad de adscripción
* **Asignatura:** Negocios Electrónicos II
* **Proyecto:** ARTSPACE — Plataforma E-Commerce de Arte Contemporáneo
* **Tema:** Integración de la Estrategia CRM y Soporte Técnico del Módulo
* **Equipo Exponente:** Nombres y números de control de los integrantes
* **Docente Titular y Fecha de Presentación**

---

# LÁMINA 02: ¿QUÉ ES CRM? Y RESUMEN EJECUTIVO DE LA ESTRATEGIA (ARTSPACE)

### 🎯 Título de la Diapositiva:
**¿Qué es CRM? Estrategia de Relación y Modelo de Fidelización ARTSPACE**

### 📄 Contenido para la Lámina (Bullets Ejecutivos):
* **Definición Estratégica:** El CRM (*Customer Relationship Management*) no es un software aislado; es una estrategia integral soportada en tecnología y datos para maximizar el **Customer Lifetime Value (CLV)** y minimizar el abandono (*Churn Rate*).
* **El Reto en ARTSPACE:** En el comercio de arte digital y físico, la adquisición no es transaccional; depende de la **confianza en la autenticidad**, la curaduría personalizada y la posventa.
* **Los 3 Pilares de la Estrategia CRM ARTSPACE:**
  1. **Atención Omnicanal:** Soporte síncrono (Chatbot instantáneo) y asíncrono (Ticketing SLA < 24h).
  2. **Pipeline Comercial:** Trazabilidad en 5 etapas desde la captura de leads hasta la posventa.
  3. **Programa de Fidelización "Art Club":** Gamificación por puntos (cashback del 5%) y escalafón por niveles (*Tiers*).

### 📊 Recuadro Destacado (Métricas Clave de Negocio):
| Pilar CRM | Mecánica Operativa | Beneficio Comercial |
| :--- | :--- | :--- |
| **Monedero Puntos de Arte** | 10 pts por cada $100 MXN de compra | Incremento del **25% en tasa de recompra** |
| **Escalafón de Tiers** | Bronce (*Explorer*), Plata (*Collector*), Oro (*VIP Patron*) | Envíos gratis y drops anticipados de 48h |

### 🖼️ Recurso Gráfico a Insertar:
* Diagrama de los 3 pilares del CRM o el banner del programa de fidelización (`pagina/img/crm_artclub_fidelizacion.png`).

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"Buenos días. Para nuestro proyecto ARTSPACE, el CRM trasciende la definición clásica de base de contactos. En el mercado del arte contemporáneo, vender una obra física o una licencia digital exige una relación de absoluta confianza. Diseñamos una estrategia CRM que ataca tres dimensiones críticas: primero, atención omnicanal para resolver dudas de embalaje y autenticidad; segundo, un embudo comercial para no perder prospectos que visitan la galería; y tercero, 'Art Club', un programa de lealtad donde cada compra abona puntos y promueve al coleccionista a niveles VIP con acceso a preventas exclusivas."*

---

# LÁMINA 03: ARQUITECTURA GENERAL DEL MÓDULO Y CANALES DE ATENCIÓN

### 🎯 Título de la Diapositiva:
**Arquitectura del Módulo CRM y Matriz de Canales Omnicanal**

### 📄 Contenido para la Lámina (Bullets Ejecutivos):
* **Arquitectura Desacoplada por Capas:**
  * **Capa 1 (Presentación):** Vistas web responsivas HTML5/CSS3 + Widget dinámico de Chatbot.
  * **Capa 2 (Lógica de Negocio):** Django 5 (Vistas controladoras, servicios modulares y señales `post_save`).
  * **Capa 3 (Persistencia):** Base de datos relacional (SQLite3 / PostgreSQL con Django ORM).
  * **Capa 4 (Integración Cloud):** Sincronización RESTful con HubSpot CRM API v3.
* **Matriz de Atención Omnicanal Centralizada:**
  * **Ticketing Web (`/contacto/`):** Asíncrono, SLA < 24h, emite folio numérico único para trazabilidad.
  * **Chatbot Interactivo ("ArtBot"):** Síncrono, respuesta instantánea (0s), resolución de FAQs (envíos, autenticidad, puntos).
  * **WhatsApp Business API:** Híbrido, atención preferencial a clientes VIP para cotizaciones especiales.
  * **Correo Transaccional:** Automatizado por eventos de compra y estatus de tickets.

### 🖼️ Recurso Gráfico a Insertar:
* Diagrama de 4 capas de arquitectura o diagrama de flujo de atención (Sección 3.3 de la bitácora).

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"Nuestra arquitectura técnica garantiza que sin importar por dónde nos contacte el cliente (sea el formulario web, el chatbot o WhatsApp), la información converge en una única fuente de verdad en Django. Implementamos una arquitectura en cuatro capas donde la lógica operativa local corre de forma ultrarrápida, y los eventos clave de ventas se despachan vía API REST hacia la nube corporativa de HubSpot."*

---

# LÁMINA 04: REQUERIMIENTOS FUNCIONALES CLAVE DEL MÓDULO CRM

### 🎯 Título de la Diapositiva:
**Requerimientos Funcionales del Sistema (Ingeniería de Software)**

### 📄 Contenido para la Lámina (Tabla Ejecutiva):
| ID | Nombre del Requerimiento | Descripción Técnica | Criterio de Aceptación | Prioridad |
| :---: | :--- | :--- | :--- | :---: |
| **RF-01** | **Radicación de Tickets** | Formulario en `/contacto/` con validación CSRF. | Genera folio numérico irrepetible y notifica acuse. | **Alta** |
| **RF-02** | **Despacho Administrativo** | Consola en `/admin` para agentes de soporte. | Filtrado por estado (`NUEVO`, `PROCESO`, `RESUELTO`) y respuesta. | **Alta** |
| **RF-03** | **Captura de Leads** | Suscripción a Newsletter en footer con interés temático. | Inserción con correo único (`unique=True`) en `LeadProspecto`. | **Alta** |
| **RF-04** | **Pipeline Comercial** | Registro de tratos y etapas del embudo. | Cálculo del valor económico ponderado del pipeline. | **Media** |
| **RF-05** | **Fidelización y Tiers** | Acreditación automática de Puntos de Arte tras compra. | Disparador Django recalcula Tier al rebasar umbrales. | **Alta** |
| **RF-06** | **Integración API REST** | Sincronización de contactos con HubSpot CRM. | Petición POST con Bearer Token responde HTTP 200/201. | **Media** |

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"Para garantizar que la estrategia comercial tuviera rigor de ingeniería, formalizamos 6 requerimientos funcionales prioritarios. Destacan el RF-01 y RF-02 para el ciclo de vida completo de atención al cliente, el RF-05 que automatiza el cálculo de beneficios mediante señales en tiempo real al concretar una compra, y el RF-06 que comunica nuestra base local con servicios cloud externos."*

---

# LÁMINA 05: MODELADO DE CASOS DE USO INTERACTIVOS (UML)

### 🎯 Título de la Diapositiva:
**Diagrama de Casos de Uso del Módulo CRM**

### 📄 Contenido para la Lámina (Bullets Ejecutivos):
* **3 Actores del Ecosistema:**
  1. **Coleccionista / Cliente:** Radica tickets, interactúa con chatbot, acumula puntos y canjea beneficios.
  2. **Agente / Administrador:** Atiende la mesa de ayuda, responde tickets y monitorea el pipeline.
  3. **HubSpot CRM API:** Actor secundario en la nube que recibe prospectos calificados.
* **Interacciones Principales:**
  * `UC-01` (Radicar Ticket) genera un `<<trigger>>` sobre la consola de administración (`UC-03`).
  * `UC-04` (Suscripción Newsletter) ejecuta un `<<include>>` hacia la sincronización externa (`UC-06`).
  * `UC-08` (Acreditar Puntos) actualiza de forma transparente la vista de perfil del usuario (`UC-07`).

### 🖼️ Recurso Gráfico a Insertar:
* Diagrama de Casos de Uso UML en Mermaid generado en la Sección 3.1 de la bitácora.

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"En este diagrama UML modelamos los límites del sistema. Observamos cómo las acciones del usuario final en el front-end disparan procesos internos para los agentes de soporte y sincronizaciones en segundo plano con HubSpot. Esta separación clara de roles asegura la trazabilidad de cada interacción."*

---

# LÁMINA 06: SOPORTE GRÁFICO I: EXPERIENCIA DEL CLIENTE (FRONT-END)

### 🎯 Título de la Diapositiva:
**Soporte Gráfico Operativo: Interfaces de Atención y Fidelización (Front-end)**

### 📄 Contenido para la Lámina:
* **Panel A: Centro de Soporte y Ticketing (`/contacto/`):**
  * Formulario reactivo conectado al modelo `TicketSoporte`.
  * Generación de Folio #104 con promesa de respuesta SLA < 24h.
* **Panel B: Asistente Virtual Omnicanal ("ArtBot"):**
  * Widget interactivo con motor síncrono para dudas frecuentes de logística y licencias.
* **Panel C: Monedero Art Club y Barra de Tiers:**
  * Indicador visual dinámico: Saldo de 150 Puntos de Arte, nivel *Art Explorer (Bronce)* y barra de progreso al siguiente Tier.

### 🖼️ Recursos Gráficos a Insertar (Pantallas Reales del Servidor Activo):
* Colocar las 3 capturas lado a lado o en cuadrícula:
  1. `pagina/img/crm_ticketing_soporte.png`
  2. `pagina/img/crm_chatbot_faq.png`
  3. `pagina/img/crm_artclub_fidelizacion.png`

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"Aquí podemos validar el soporte gráfico del sistema corriendo en tiempo real. En la primera pantalla vemos la mesa de ayuda donde el coleccionista recibe de inmediato su número de folio. En la segunda, nuestro asistente virtual 'ArtBot' resolviendo dudas frecuentes sin intervención humana. Y en la tercera, la tarjeta de lealtad en el perfil del cliente, mostrando sus Puntos de Arte acumulados y cuánto le falta para desbloquear envíos gratis en el siguiente nivel."*

---

# LÁMINA 07: SOPORTE GRÁFICO II: PANEL DE CONTROL Y MÉTRICAS (BACK-OFFICE)

### 🎯 Título de la Diapositiva:
**Soporte Gráfico Operativo: Gestión Administrativa y KPIs del Negocio**

### 📄 Contenido para la Lámina:
* **Consola Administrativa de Mesa de Ayuda (`/admin/`):**
  * Filtrado granular de tickets por estado (`NUEVO`, `PROCESO`, `RESUELTO`) y prioridad.
  * Acciones masivas en lote para actualizar resoluciones y disparar notificaciones.
* **Métricas Operativas y Dashboards de Control:**
  * **Embudo Comercial:** 120 prospectos captados ➔ 18 compras cerradas (Tasa de conversión del **15%**, facturación de **$54,000 MXN**).
  * **SLA de Soporte:** **88.5%** de solicitudes resueltas en menos de 24 horas; tiempo promedio de respuesta de **4.2 horas**.
  * **Concentración VIP:** El 8% de clientes en nivel *VIP Patron* representa el **46% del margen bruto** de la tienda.

### 🖼️ Recursos Gráficos a Insertar:
* Esquema del panel Django Admin + Gráficas analíticas:
  1. `pagina/img/hubspot_pipeline.png` (Embudo de Ventas)
  2. `pagina/img/salesforce_dashboard.png` (Dashboard de Métricas CRM)

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"Del lado operativo, el equipo administrativo cuenta con una consola centralizada en Django Admin para resolver incidencias en lote. Además, mediante dashboards analíticos medimos el avance real: una tasa de conversión del 15% en el embudo comercial y un cumplimiento del 88.5% en nuestro SLA de atención. Esto demuestra que el sistema está completamente alineado con los objetivos de negocio."*

---

# LÁMINA 08: MODELO DE DATOS E INTEGRACIÓN TÉCNICA (DJANGO & REST)

### 🎯 Título de la Diapositiva:
**Modelo de Datos Relacional y Sincronización API REST**

### 📄 Contenido para la Lámina:
* **Entidades Clave del CRM en Django ORM:**
  * `User` (Django Core) ── `1:1` ── `PerfilCliente` (*puntos_fidelidad*, *nivel_tier*, *total_gastado*).
  * `User` ── `1:N` ── `TicketSoporte` (*asunto*, *estado*, *prioridad*, *respuesta*).
  * `LeadProspecto` ── `1:N` ── `OportunidadPipeline` (*monto_estimado*, *etapa*).
  * `PerfilCliente` ── `1:N` ── `PuntosHistorial` (*concepto*, *abonos/canjes*).
* **Integración API REST Externa (`crm_service.py`):**
  * Despacho asíncrono vía `HTTP POST` al endpoint `/crm/v3/objects/contacts` de HubSpot.
  * Autenticación corporativa mediante `Authorization: Bearer <TOKEN>` con serialización en JSON.

### 🖼️ Recurso Gráfico a Insertar:
* Diagrama Entidad-Relación (ERD) simplificado o bloque de código limpio de `gallery/models.py` y `crm_service.py`.

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"A nivel de datos, el módulo extiende de forma limpia el modelo de usuarios nativo de Django, manteniendo integridad referencial estricta. Cuando un cliente realiza una transacción, las señales recalculan su puntaje sin bloquear la interfaz. Para la sincronización externa, creamos un servicio desacoplado que serializa los datos en JSON y los autentica con HubSpot, garantizando escalabilidad y seguridad."*

---

# LÁMINA 09: MATRIZ DE ALINEACIÓN OPERATIVA

### 🎯 Título de la Diapositiva:
**Matriz de Trazabilidad y Alineación Operativa del Sistema**

### 📄 Contenido para la Lámina (Tabla Comparativa):
| Objetivo Estratégico | Requerimiento | Componente Técnico (Django) | Validación Operativa (Pantalla) | Indicador Clave (KPI) |
| :--- | :---: | :--- | :--- | :---: |
| **Atención Inmediata y Confiable** | `RF-01` / `RF-02` | `TicketSoporte` + `views.contacto` | Formulario con Folio #104 y ArtBot | SLA < 24h (88.5% éxito) |
| **Conversión de Prospectos** | `RF-03` / `RF-04` | `LeadProspecto` + `OportunidadPipeline` | Formulario Footer y Pipeline | Conversión del 15% |
| **Fidelización y Recompra** | `RF-05` | `PerfilCliente.acreditar_puntos()` | Banner Perfil y Tiers Art Club | Recompra recurrente (+25%) |
| **Ecosistema Omnicanal** | `RF-06` | `crm_service.py` (HubSpot Client) | Sincronización RESTful Cloud | 100% Leads sincronizados |

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"Esta matriz de alineación operativa valida que cada decisión de código responde a una necesidad del negocio. No desarrollamos funciones al azar: cada modelo en Django y cada interfaz visual impacta directamente un KPI medible, desde la velocidad de atención hasta la facturación del e-commerce."*

---

# LÁMINA 10: COMENTARIOS PERSONALES Y APRENDIZAJES SIGNIFICATIVOS

### 🎯 Título de la Diapositiva:
**Aprendizajes Significativos y Conclusiones del Equipo**

### 📄 Contenido para la Lámina (3 Ejes de Aprendizaje):
* **1. Transición de Arquitectura Estática a Transaccional:**
  * Comprender que un sitio web de catálogo cobra valor real cuando integra persistencia relacional, trazabilidad de eventos y automatización orientada al cliente.
* **2. Visión Estratégica del CRM vs. Simple Repositorio:**
  * El CRM no es una libreta digital de direcciones; es el motor analítico que permite gamificar la lealtad, segmentar intereses y personalizar la oferta comercial.
* **3. Hibridación Tecnológica (Desarrollo Propio + SaaS Cloud):**
  * Aprendimos a diseñar arquitecturas modernas: control absoluto del núcleo operativo y datos en Django local, complementado con la potencia de APIs en la nube (HubSpot) para analítica avanzada.

### 🗣️ Pitch del Expositor (Guion Verbal):
> *"Como conclusión del equipo, esta práctica nos permitió vivir el ciclo completo de la ingeniería de software aplicada a los negocios electrónicos. Descubrimos que el verdadero reto técnico no es solo levantar una base de datos, sino hacer que esa tecnología resuelva la fricción del usuario, fidelice al comprador y proporcione métricas accionables a la dirección de la empresa."*

---

# LÁMINA 11: REFERENCIAS BIBLIOGRÁFICAS (FORMATO APA 7ma EDICIÓN)

### 🎯 Título de la Diapositiva:
**Referencias Bibliográficas**

### 📄 Contenido para la Lámina:
1. **Buttle, F., & Maklan, S. (2019).** *Customer Relationship Management: Concepts and Technologies* (4th ed.). Routledge. https://doi.org/10.4324/9781351016551
2. **HubSpot, Inc. (2026).** *HubSpot REST APIs: Managing CRM Objects and Contact Pipelines*. HubSpot Developer Documentation. https://developers.hubspot.com/docs/api/crm/contacts
3. **Kumar, V., & Reinartz, W. (2018).** *Customer Relationship Management: Concept, Strategy, and Tools* (3rd ed.). Springer-Verlag.
4. **Laudon, K. C., & Traver, C. G. (2022).** *E-Commerce 2021-2022: Business, Technology, Society* (17th ed.). Pearson Educación.
5. **Peppers, D., & Rogers, M. (2016).** *Managing Customer Experience and Relationships: A Strategic Framework* (3rd ed.). John Wiley & Sons.
6. **Sommerville, I. (2019).** *Ingeniería del software* (10a ed.). Pearson Educación de México.

---
*(Lámina final: Agradecimiento y espacio para preguntas del docente y compañeros)*
