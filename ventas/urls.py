from django.urls import path
from . import views
from . import stripe_views

urlpatterns = [
    path('carrito/',                   views.ver_carrito,          name='ver_carrito'),
    path('carrito/agregar/<int:pk>/',  views.agregar_al_carrito,   name='agregar_carrito'),
    path('carrito/eliminar/<int:pk>/', views.eliminar_del_carrito,  name='eliminar_carrito'),
    path('carrito/confirmar/',         views.confirmar_compra,      name='confirmar_compra'),
    path('mis-compras/',               views.ver_mis_compras,           name='mis_compras'),
    path('comprar/<int:pk>/',          views.agregar_al_carrito,    name='comprar_cliente'),

    # ── Pasarela Stripe ──────────────────────────────────────────────────────
    path('checkout/',          stripe_views.checkout,           name='checkout_stripe'),
    path('checkout/exito/',    stripe_views.checkout_exito,     name='checkout_exito'),
    path('checkout/cancelado/',stripe_views.checkout_cancelado, name='checkout_cancelado'),
]
