"""
Vistas de la pasarela de pagos con Stripe (modo test / sandbox).

Flujo:
  1. GET  /ventas/checkout/         → muestra formulario de tarjeta + resumen
  2. POST /ventas/checkout/         → crea PaymentIntent en Stripe, confirma pago
  3. GET  /ventas/checkout/exito/   → pago OK  → registra ventas en BD
  4. GET  /ventas/checkout/cancel/  → pago cancelado → vuelve al carrito

Tarjeta de prueba Stripe: 4242 4242 4242 4242  |  cualquier fecha futura  |  cualquier CVV
"""

import json
from requests import request
import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _

from inventario.models import Vehiculo
from ventas.models import Venta
from ventas.services import confirmar_compra_vehiculos

# ─── helpers internos del carrito (mismo patrón que views.py) ─────────────────

def _get_carrito(request):
    return request.session.get('carrito', [])

def _save_carrito(request, lista):
    request.session['carrito'] = lista
    request.session.modified = True


# ─── 1. Página de checkout ────────────────────────────────────────────────────

@login_required
def checkout(request):
    """Muestra el formulario de pago con Stripe Elements."""
    pks = _get_carrito(request)
    if not pks:
        messages.warning(request, _('Tu carrito está vacío.'))
        return redirect('ver_carrito')

    vehiculos = list(Vehiculo.objects.filter(pk__in=pks, estado='en_venta'))
    if not vehiculos:
        messages.error(request, _('Ningún vehículo de tu carrito está disponible.'))
        _save_carrito(request, [])
        return redirect('ver_carrito')

    total_cop = sum(v.precio for v in vehiculos)

    # Stripe trabaja en centavos (enteros). COP no tiene centavos reales,
    # pero Stripe lo acepta igual multiplicando × 100.
    total_centavos = int(total_cop * 100)

    # Crear (o reutilizar) el PaymentIntent guardado en sesión
    intent_id = request.session.get('stripe_intent_id')
    intent = None

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        if intent_id:
            # Verificar que el intent previo siga pendiente
            intent = stripe.PaymentIntent.retrieve(intent_id)
            if intent.status not in ('requires_payment_method', 'requires_confirmation'):
                intent = None  # ya fue usado → crear uno nuevo

        if intent is None:
            intent = stripe.PaymentIntent.create(
                amount=total_centavos,
                currency='cop',
                metadata={
                    'user_id': str(request.user.pk),
                    'vehiculos': ','.join(str(pk) for pk in pks),
                },
                description=f'CarNest – compra de {len(vehiculos)} vehículo(s)',
            )
            request.session['stripe_intent_id'] = intent.id

    except stripe.error.StripeError as e:
        messages.error(request, f'Error al conectar con Stripe: {e.user_message}')
        return redirect('ver_carrito')

    context = {
        'vehiculos': vehiculos,
        'total': total_cop,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
    }
    return render(request, 'ventas/checkout.html', context)


# ─── 2. Éxito: Stripe redirige aquí tras pago confirmado ─────────────────────

@login_required
def checkout_exito(request):
    """
    Stripe redirige aquí con ?payment_intent=pi_xxx&payment_intent_client_secret=...
    Verificamos el estado del intent y registramos la venta.
    """
    intent_id = request.GET.get('payment_intent') or request.session.get('stripe_intent_id')
    if not intent_id:
        messages.error(request, _('No se encontró información del pago.'))
        return redirect('ver_carrito')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        intent = stripe.PaymentIntent.retrieve(intent_id)
    except stripe.error.StripeError as e:
        messages.error(request, f'Error verificando el pago: {e.user_message}')
        return redirect('ver_carrito')

    if intent.status != 'succeeded':
        messages.error(
            request,
            _(f'El pago no fue completado (estado: {intent.status}). Intenta de nuevo.')
        )
        return redirect('checkout_stripe')

    # Verificar que no hayamos procesado ya este intent (idempotencia)
    if Venta.objects.filter(stripe_payment_intent=intent_id).exists():
        messages.info(request, _('Esta compra ya fue registrada anteriormente.'))
        _save_carrito(request, [])
        request.session.pop('stripe_intent_id', None)
        return redirect('mis_compras')

    # Obtener PKs del metadata del intent (fuente de verdad)
    # Obtener PKs del metadata del intent (fuente de verdad)
    metadata = intent["metadata"] if "metadata" in intent else {}

    pks_str = metadata["vehiculos"] if "vehiculos" in metadata else ""

    if not pks_str:
        messages.error(request, _('No se encontraron vehículos asociados al pago.'))
        return redirect('ver_carrito')

    pks = [int(pk) for pk in pks_str.split(',') if pk]

    vehiculos, comprados, errores = confirmar_compra_vehiculos(pks, request.user)

    # Asociar payment_intent a las ventas creadas
    if comprados:
        Venta.objects.filter(
            comprador=request.user,
            vehiculo__in=vehiculos,
            stripe_payment_intent='',
        ).update(
            stripe_payment_intent=intent_id,
            stripe_status='succeeded',
        )

    # Limpiar sesión
    _save_carrito(request, [])
    request.session.pop('stripe_intent_id', None)

    if comprados:
        messages.success(
            request,
            _('¡Pago exitoso! Vehículos comprados: ') + ', '.join(comprados)
        )
    if errores:
        messages.warning(
            request,
            _('Algunos vehículos no pudieron procesarse: ') + '; '.join(errores)
        )

    return redirect('mis_compras')


# ─── 3. Cancelación ──────────────────────────────────────────────────────────

@login_required
def checkout_cancelado(request):
    messages.info(request, _('Pago cancelado. Tu carrito sigue intacto.'))
    return redirect('ver_carrito')
