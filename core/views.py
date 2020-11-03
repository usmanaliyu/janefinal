from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ReviewForm, CheckoutForm, RefundForm, CouponForm, ContactForm, NewsletterForm
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from .filters import ItemFilter
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage

from django.utils.decorators import method_decorator


from .models import (
    Team,
    Item,
    Wishlist,
    Reviews,
    OrderItem,
    Order,
    Address,
    Payment,
    Coupon,
    Refund,
    UserProfile,
    Category,
    HomepageBanner,
    HomesideBanner,
    ShoptopBanner,
    ShopbottomBanner,

    Contact,
    Slider,
    Newsletter,
    About
)

# Create your views here.


class HomeView(ListView):
    model = Item
    context_object_name = 'product'
    template_name = 'index.html'

    def get_queryset(self):
        qs = Item.objects.order_by('-pub_date')

        return qs

    def post(self, request, *args, **kwargs):
        newsletter = NewsletterForm(self.request.POST)

        if newsletter.is_valid():
            email = newsletter.cleaned_data.get('email')
            existing = Newsletter.objects.filter(email=email).count()

            if existing == 0:
                news = Newsletter(
                    email=email
                )
                news.save()
                messages.success(
                    self.request, 'You have signup for the newsletter')
                return redirect('core:home')
            else:
                messages.success(
                    self.request, 'You have already used this email')
                return redirect('core:home')
        messages.error(self.request, 'You haven\'t for the newsletter')
        return redirect('core:home')

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'newarrivals': Item.objects.filter(new_arrival=True)[:4],
            'homepage': HomepageBanner.objects.order_by('-date')[:1],
            'homeside': HomesideBanner.objects.order_by('-date')[:1],
            "shopbottom": ShopbottomBanner.objects.order_by('-date')[:1],
            'shoptop': ShoptopBanner.objects.order_by('-date')[:1],
            'slider': Slider.objects.order_by('-date')[:3],
            'newsletter': NewsletterForm(),
            'category_list': Category.objects.all()
        })
        return context


class ShopView(ListView):
    model = Item
    template_name = 'shop-sidebar.html'
    context_object_name = 'category_list'
    paginate_by = 18

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ItemFilter(
            self.request.GET, queryset=self.get_queryset())
        context.update({
            'category_list': Category.objects.all()
        })
        return context

    def get_queryset(self):
        qs = Item.objects.order_by('-pub_date')
        return qs

    def post(self, request, *args, **kwargs):
        newsletter = NewsletterForm(self.request.POST)

        if newsletter.is_valid():
            email = newsletter.cleaned_data.get('email')
            existing = Newsletter.objects.filter(email=email).count()

            if existing == 0:
                news = Newsletter(
                    email=email
                )
                news.save()
                messages.success(
                    self.request, 'You have signup for the newsletter')
                return redirect('core:shop')
            else:
                messages.success(
                    self.request, 'You have already used this email')
                return redirect('core:shop')
        messages.error(self.request, 'You haven\'t for the newsletter')
        return redirect('core:shop')


class AboutView(TemplateView):
    template_name = 'about.html'

    def post(self, request, *args, **kwargs):
        newsletter = NewsletterForm(self.request.POST)

        if newsletter.is_valid():
            email = newsletter.cleaned_data.get('email')
            existing = Newsletter.objects.filter(email=email).count()

            if existing == 0:
                news = Newsletter(
                    email=email
                )
                news.save()
                messages.success(
                    self.request, 'You have signup for the newsletter')
                return redirect('core:about')
            else:
                messages.success(
                    self.request, 'You have already used this email')
                return redirect('core:about')
        messages.error(self.request, 'You haven\'t for the newsletter')
        return redirect('core:about')

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context.update({
            'newsletter': NewsletterForm(),
            'homeside': HomesideBanner.objects.order_by('-date')[:1],
            'about': About.objects.order_by('-date')[:1],
            'team': Team.objects.all(),
            'category_list': Category.objects.all()

        })
        return context


class DetailView(DetailView):
    model = Item
    context_object_name = 'product'
    template_name = 'product-single.html'

    def post(self, request, *args, **kwargs):
        form = ReviewForm(self.request.POST)

        if form.is_valid():
            review = form.cleaned_data.get('review')
            user = self.request.user
            item = self.get_object()

            review = Reviews(
                user=user,
                item=item,
                review=review
            )
            review.save()
            messages.success(
                self.request, 'Yay, you are amazing for the review')
            return redirect('core:details', slug=item.slug)
        messages.error(self.request, 'Oh no, you didn\'t any review')
        return redirect('core:details', slug=self.get_object().slug)

    def get_object(self, **kwargs):
        qs = super().get_object(**kwargs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip = get_object_or_404(Item, slug=self.get_object().slug)
        trip_related = trip.tags.similar_objects()[:4]
        context.update({
            'form': ReviewForm(),
            "trip_related": trip_related,
            'category_list': Category.objects.all()

        })
        return context


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            category_list = Category.objects.all()
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'category_list': category_list
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm(self.request.POST or None)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_phone = form.cleaned_data.get(
                        'shipping_phone')
                    shipping_state = form.cleaned_data.get(
                        'shipping_state')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            phone=shipping_phone,
                            country=shipping_country,
                            state=shipping_state,
                            zip=shipping_zip,
                            address_type='S'

                        )
                        coupon = Coupon(
                            code=shipping_state,
                            amount=1000
                        )
                        coupon.save()

                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.coupon = coupon
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_phone = form.cleaned_data.get(
                        'billing_phone')
                    billing_state = form.cleaned_data.get(
                        'billing_state')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            phone=billing_phone,
                            state=billing_state,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                return redirect('core:payment')
            messages.error(self.request, 'You didn\'t enter any address')
            return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class CartView(TemplateView):
    template_name = 'cart.html'

    def get(self, *args, **kwargs):
        try:
            shoptop = ShoptopBanner.objects.order_by('-date')[:2]
            category_list = Category.objects.all()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                'category_list': category_list


            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class FaqView(TemplateView):
    template_name = 'faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({

            'category_list':  Category.objects.all()
        })
        return context


class ContactView(TemplateView):
    template_name = 'contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': ContactForm(),
            'category_list':  Category.objects.all()
        })
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(self.request.POST or None)

        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            contact = Contact(
                name=name,
                email=email,
                subject=subject,
                message=message

            )
            contact.save()
            context = {
                "name": name,
                "subject": subject,
                "message": message,
                "email": email
            }
            template = render_to_string('contact_template.html', context)
            mail = sale = EmailMessage(
                'We have a new mail',
                template,
                "contact@janes-fashion.com",
                ['contact@janes-fashion.com']

            )
            mail.fail_silently = False
            mail.send()
            return redirect('core:contact-success')


class ContactSuccessView(TemplateView):
    template_name = "contact-success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({

            'category_list':  Category.objects.all()
        })
        return context


class LoginView(TemplateView):
    template_name = 'login.html'


class SignupView(TemplateView):
    template_name = 'signin.html'


class ForgotView(TemplateView):
    template_name = 'forget-password.html'


class ConfirmView(TemplateView):
    template_name = 'confirmation.html'


class PaystackView(TemplateView):
    template_name = "purchase-confirmation.html"

    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)

        user = self.request.user

        email = self.request.user.email
        amount = order.get_total()

        context = {
            'order': order,
            "email": email,
            "amount": amount,
            'category_list':  Category.objects.all()
        }

        if order.shipping_address or order.billing_address:
            return render(self.request,  "purchase-confirmation.html", context)
        else:
            messages.error(self.request, "You have no billing address")
            return redirect('core:checkout')


class OrderView(LoginRequiredMixin, TemplateView):
    template_name = "order.html"

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        context.update({
            'order': Order.objects.filter(user=self.request.user, ordered=True),

            'category_list':  Category.objects.all()
        })
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    queryset = Order.objects.all()
    context_object_name = 'order'
    template_name = "order_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({

            'category_list':  Category.objects.all()
        })
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context.update({
            'wishlist': Wishlist.objects.filter(user=self.request.user),
            'category_list':  Category.objects.all()
        })
        return context


def click(request):

    return render(request, 'contact.html')


# class PricingView(TemplateView):
#     template_name =   "pricing.html"

class AddressView(LoginRequiredMixin, TemplateView):
    template_name = "address.html"

    def get_context_data(self, **kwargs):
        context = super(AddressView, self).get_context_data(**kwargs)
        context.update({
            'order': Order.objects.filter(user=self.request.user, ordered=True),
            'category_list':  Category.objects.all()
        })
        return context


def handler404(request, exception):
    return render(request, '404.html')


@login_required
def wishlist_home(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wish_qs = Wishlist.objects.filter(user=request.user, item=item)
    if wish_qs.exists():
        wish_qs[0].delete()
        messages.error(request, "You have removed an item to your wishlist")
        return redirect('core:home')
    Wishlist.objects.create(user=request.user, item=item)
    messages.success(request, "You have added an item to your wishlist")
    return redirect('core:home')


@login_required
def wishlist(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wish_qs = Wishlist.objects.filter(user=request.user, item=item)
    if wish_qs.exists():
        wish_qs[0].delete()
        messages.error(request, "You have removed an item to your wishlist")
        return redirect('core:shop')
    Wishlist.objects.create(user=request.user, item=item)
    messages.success(request, "You have added an item to your wishlist")
    return redirect('core:shop')


@login_required
def wishlist_product(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wish_qs = Wishlist.objects.filter(user=request.user, item=item)
    if wish_qs.exists():
        wish_qs[0].delete()
        messages.error(request, "You have removed an item to your wishlist")
        return redirect('core:details', slug=slug)
    Wishlist.objects.create(user=request.user, item=item)
    messages.success(request, "You have added an item to your wishlist")
    return redirect('core:details', slug=slug)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:cart")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:details", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:details", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:details", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:details", slug=slug)


def CategoryView(request, slug):
    instance = Item.objects.all()
    categories = Category.objects.all()

    if slug:
        category = get_object_or_404(Category, slug=slug)
        instance_list = instance.filter(category=category)
        paginator = Paginator(instance_list, 12)
        page = request.GET.get('page')
        instance = paginator.get_page(page)
        shoptop = ShoptopBanner.objects.order_by('-date')[:4]
        shopside = ShopbottomBanner.objects.order_by('-date')[:2]
        category_list = Category.objects.all()
    content = {
        'categories': categories,
        'instance': instance,
        'category': category,
        "shoptop": shoptop,
        "shopside": shopside,
        'category_list': category_list


    }
    return render(request, 'categoryview.html', content)


class ReturnView(TemplateView):
    template_name = 'returns.html'

    def get_context_data(self, **kwargs):
        context = super(AddressView, self).get_context_data(**kwargs)
        context.update({
            'category_list':  Category.objects.all()
        })
        return context


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")
