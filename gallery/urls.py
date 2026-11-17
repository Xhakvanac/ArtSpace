from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('colecciones/', views.colecciones, name='colecciones'),
    path('artistas/', views.artistas, name='artistas'),
    path('galeria/', views.galeria, name='galeria'),
    path('contacto/', views.contacto, name='contacto'),
    path('newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('chatbot-api/', views.chatbot_api, name='chatbot_api'),
    path('simular-compra/', views.simular_compra_demo, name='simular_compra_demo'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    # API Contract REST Endpoints (v1)
    path('api/v1/cart/hold/', views.api_cart_hold, name='api_cart_hold'),
    path('api/v1/tax/calculate/', views.api_tax_calculate, name='api_tax_calculate'),
    path('api/v1/checkout/process/', views.api_checkout_process, name='api_checkout_process'),
    path('api/v1/orders/<str:codigo_pedido>/track/', views.api_order_track, name='api_order_track'),
]
