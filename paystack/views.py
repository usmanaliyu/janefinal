import json
from django.shortcuts import redirect, reverse
from django.http import JsonResponse
from django.views.generic import RedirectView, TemplateView
# Create your views here.
from . import settings, signals, utils
from .signals import payment_verified
from .utils import load_lib
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from core.models import Order, OrderItem, Address, Payment, Item


def verify_payment(request, order):
    amount = request.GET.get('amount')
    txrf = request.GET.get('trxref')
    PaystackAPI = load_lib()
    paystack_instance = PaystackAPI()
    response = paystack_instance.verify_payment(txrf, amount=int(amount))
    if response[0]:
        payment_verified.send(
            request=request,
            sender=PaystackAPI,
            ref=txrf,
            amount=int(amount) / 100,
            order=order)
        return redirect('core:pay')
        # return redirect(
        #     reverse('paystack:successful_verification', args=[order]))
    # return redirect(reverse('paystack:failed_verification', args=[order]))
    return redirect('core:pay-failed')


@receiver(payment_verified)
def on_payment_verified(request, sender, ref, amount, **kwargs):
    order = Order.objects.get(user=request.user, ordered=False)

    user = request.user
    email = request.user.email
    name = request.user.first_name
    name_2 = request.user.last_name
    number = order.shipping_address.phone
    address = order.shipping_address.street_address
    country = order.shipping_address.country
    state = order.shipping_address.state

    context = {
        'order': order,
        'amount': amount,
        'email': email,
        'name': name,
        'user': user,
        'ref': ref,
        "name_2": name_2,
        "address": address,
        "country": country,
        'state': state,
        'number': number
    }

    payment = Payment()
    order.ordered = True
    order.ref_code = ref
    # order_item.ordered = True
    payment.user = user
    payment.amount = amount
    payment.reference = ref
    payment.save()
    # attach payment to order

    order_items = order.items.all()

    order_items.update(ordered=True)
    for item in order_items:
        item.save()

    order.payment = payment
    order.save()
    # send email to user
    template = render_to_string('email_template.html', context)
    sale = EmailMessage(
        'Thank you for your order!!',
        template,
        "contact@janes-fashion.com",
        [email]

    )
    sale.fail_silently = False
    sale.send()
    template = render_to_string('sale_template.html', context)
    jane = EmailMessage(
        'We have received an order!!',
        template,
        "contact@janes-fashion.com",
        ['contact@janes-fashion.com']

    )
    jane.fail_silently = False
    jane.send()
    # print(user, sender, amount, ref, amount,  email)


class FailedView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if settings.PAYSTACK_FAILED_URL == 'core:pay-failed':
            return reverse(settings.PAYSTACK_FAILED_URL)
        return settings.PAYSTACK_FAILED_URL


def success_redirect_view(request, order_id):
    url = settings.PAYSTACK_SUCCESS_URL
    if url == 'core:pay':
        url = reverse(url)
    return redirect(url, permanent=True)


def failure_redirect_view(request, order_id):
    url = settings.PAYSTACK_FAILED_URL
    if url == 'core:pay-failed':
        url = reverse(url)
    return redirect(url, permanent=True)


class SuccessView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        if settings.PAYSTACK_SUCCESS_URL == 'paystack:success_page':
            return reverse(settings.PAYSTACK_SUCCESS_URL)
        return settings.PAYSTACK_SUCCESS_URL


def webhook_view(request):
    # ensure that all parameters are in the bytes representation
    PaystackAPI = load_lib()
    paystack_instance = PaystackAPI()
    signature = request.META['HTTP_X_PAYSTACK_SIGNATURE']
    paystack_instance.webhook_api.verify(
        signature, request.body, full_auth=True)
    # digest = utils.generate_digest(request.body)
    # if digest == signature:
    #     payload = json.loads(request.body)
    #     signals.event_signal.send(
    #         sender=request, event=payload['event'], data=payload['data'])
    return JsonResponse({'status': "Success"})
