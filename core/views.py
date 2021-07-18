from django.contrib.auth.models import User
from rest_framework import authtoken, request
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from .serializers import ContactSerializer, NewsletterSerializer, ItemSerializer, OrderItemSerializer, OrderSerializer, AddressSerializer, PaymentSerializer, ReviewsSerializer, UserInfo, WishlistSerializer
from rest_framework.response import Response
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_405_METHOD_NOT_ALLOWED
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    Address, Coupon, CustomUser, Item,
    OrderItem,
    Order,
    Contact,
    Newsletter, Payment, RecentlyViewed, Reviews, Wishlist,

)
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
# PAYSTACK_PUBLIC_KEY = "pk_live_3b7b32232d4485c95cdc0c50f83acda3b6f523b1"
# PAYSTACK_SECRET_KEY = "sk_live_1c2a919aca68e2a4fb2369cd828972d801a29d80"

PAYSTACK_PUBLIC_KEY = "pk_test_6681e7fc29d2350d6f35f98ae14535747f541783"
PAYSTACK_SECRET_KEY = "sk_test_eb983647781b4cdca3ba3be945637e1585059f71"


class PaystackkeyView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(PAYSTACK_PUBLIC_KEY, status=HTTP_200_OK)


class UserEmailView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        token = Token.objects.get(user=user)
        userExist = CustomUser.objects.get(auth_token=token)
        if userExist:
            email = userExist.email
            return Response(email, status=HTTP_200_OK)


class UserDetailsView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        token = Token.objects.get(user=user)
        userExist = CustomUser.objects.get(auth_token=token)
        serializer = UserInfo(userExist).data
        return Response(serializer, status=HTTP_200_OK)


class RelatedPostView(ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        slug = request.query_params.get('slug', None)
        print(slug)
        if slug is None:
            return Response({"message": "no related posts"}, status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        tags = item.tags.similar_objects()[:3]
        serializer = ItemSerializer(tags, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        return Response(status=HTTP_200_OK)


class FetchWishlistView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        saved = Wishlist.objects.filter(user=self.request.user)
        serializer = WishlistSerializer(saved, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class DeleteFromWishlistView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get("slug", None)
        wishlist = get_object_or_404(Wishlist, item__slug=slug)
        if wishlist:
            wishlist.delete()
        #      wish_qs = Wishlist.objects.filter(user=self.request.user, item=item)
        # if wish_qs.exists():
        #     wish_qs[0].delete()
            return Response(status=HTTP_200_OK)


class ListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemSerializer
    queryset = Item.objects.all().order_by('-pub_date')[:30]


class ShopListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemSerializer
    queryset = Item.objects.all().order_by('-pub_date')


class SearchView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemSerializer
    queryset = Item.objects.all().order_by('-pub_date')

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        if query is None:
            print(query)
            return Response({"message": "No item in search"}, status=HTTP_200_OK)
        items = Item.objects.all()
        queryset = items.filter(Q(title__icontains=query)
                                | Q(description__icontains=query))
        serializer = ItemSerializer(queryset, many=True).data
        return Response(serializer, status=HTTP_200_OK)


class ShopFilterView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemSerializer
    queryset = Item.objects.all().order_by('-pub_date')


class ProductDetailsView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    lookup_field = 'slug'


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order:
                return order
        except ObjectDoesNotExist:
            return Response({"message": "You don't have an active order"}, status=HTTP_400_BAD_REQUEST)

# class OrderDetailView(APIView):
#     serializer_class = OrderSerializer
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         if order is None:
#             return Response({"message": "You don't have an active order"}, status=HTTP_400_BAD_REQUEST)
#         return Response(order, status=HTTP_200_OK)


class OrderItemDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    queryset = OrderItem.objects.all()

    def post(self, request, *args, **kwargs):
        slug = request.data.get("slug", None)
        item = get_object_or_404(Item, slug=slug)
        order_item = get_object_or_404(
            OrderItem, item=item, user=self.request.user, ordered=False)
        order = get_object_or_404(Order, user=self.request.user, ordered=False)
        order.items.remove(order_item)
        order_item.delete()
        order.save()
        return Response(status=HTTP_200_OK)


class OrderQuantityupdateView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "invalid request"}, status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(
            user=self.request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=self.request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    return Response({"message": "This item quantity was updated"}, status=HTTP_200_OK)
                else:
                    order.items.remove(order_item)

                    return Response({"message": "This item quantity was updated"}, status=HTTP_200_OK)
            else:
                return Response({"message": "This item was not in your cart"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "slug is none"}, status=HTTP_400_BAD_REQUEST)
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
                return Response(status=HTTP_200_OK)
            else:
                order.items.add(order_item)
                return Response(status=HTTP_200_OK)
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            order.save()
            return Response(status=HTTP_200_OK)


class AddToWishListView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        item = get_object_or_404(Item, slug=slug)
        wish_qs = Wishlist.objects.filter(user=self.request.user, item=item)
        if wish_qs.exists():
            wish_qs[0].delete()
            return Response({"message": "You have removed an item to your wishlist"}, status=HTTP_400_BAD_REQUEST)
        Wishlist.objects.create(user=request.user, item=item)
        return Response({"message": "You have added an item to your wishlist"}, status=HTTP_200_OK)


class CheckWishlistView(APIView):
    def get(self, request, *args, **kwargs):
        slug = request.query_params.get('slug', None)
        item = get_object_or_404(Item, slug=slug)
        wish_qs = Wishlist.objects.filter(user=self.request.user, item=item)
        if wish_qs.exists():
            return Response({"message": "You have this in your wishlist"}, status=HTTP_200_OK)
        return Response({"message": "You don't have this item in your wishlist"}, status=HTTP_400_BAD_REQUEST)


class CheckOrderDetailsView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id', None)
        order = Order.objects.get(user=self.request.user, ordered=True, id=id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=HTTP_200_OK)


class CheckOrderItemDetailsView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id', None)
        order = Order.objects.get(user=self.request.user, ordered=True, id=id)
        order_items = order.items.all()
        print(order_items)
        serializer = OrderItemSerializer(order_items, many=True).data
        return Response(serializer, status=HTTP_200_OK)


class CheckReviewsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        slug = request.query_params.get('slug', None)
        item = get_object_or_404(Item, slug=slug)
        reviews_qs = Reviews.objects.filter(item=item)
        if reviews_qs.exists():
            serializer = ReviewsSerializer(reviews_qs, many=True)
            return Response(serializer.data)
        return Response({"message": "No review"}, status=HTTP_400_BAD_REQUEST)


class CheckTagsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        slug = request.query_params.get('slug', None)
        if slug is None:
            return Response({"message": "No tag"}, status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        tags = item.tags.similar_objects()[:3]
        serializer = ItemSerializer(tags, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class AddCouponView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        if code is None:
            return Response({"message": "No coupon added"}, status=HTTP_400_BAD_REQUEST)
        try:
            coupon = get_object_or_404(Coupon, code=code)
            order = Order.objects.get(user=request.user, ordered=False)
            if order.coupon:
                return Response({"message": "coupon already exist in this order"}, status=HTTP_400_BAD_REQUEST)
            order.coupon = coupon
            order.save()
            return Response({"message": "Coupon added"}, status=HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Coupon does not exist"},
                            status=HTTP_400_BAD_REQUEST)


class ShippingFeeVIew(APIView):
    def get(self, request, *args, **kwargs):
        state = request.query_params.get('region', None)
        country = request.query_params.get('country', None)
        shipping_fee = int(2000)
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.get_order_total() >= int(10000):
            shipping_fee = int(0)
            return Response({"shipping_fee": shipping_fee, "state": state}, status=HTTP_200_OK)
        else:
            if country == "Nigeria":
                if state == "Abuja Federal Capital Territory":
                    shipping_fee = int(0)
                    print(state)
                    return Response({"shipping_fee": shipping_fee, "state": state}, status=HTTP_200_OK)
                else:
                    print(state)
                    shipping_fee = int(2000)
                    return Response({"shipping_fee": shipping_fee, "state": state}, status=HTTP_200_OK)
            print(state)
            return Response(status=HTTP_200_OK)


class AddShippingFeeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        shipping = request.data.get('shippingFee', None)

        print(shipping)
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.shipping_fee:
            order.shipping_fee = float(shipping)
            order.order_price = order.get_order_total()
            order.order_final_price = order.get_order_final_total()
            order.save()
            return Response(status=HTTP_200_OK)
        order.order_price = order.get_order_total()
        order.order_final_price = order.get_order_final_total()
        order.shipping_fee = float(shipping)
        order.save()
        return Response(status=HTTP_200_OK)


class DeleteAddressView(APIView):
    def post(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        print(id)
        address = Address.objects.filter(id=id, user=self.request.user)
        if address.exists():
            address.delete()
            return Response(status=HTTP_200_OK)
        return Response(status=HTTP_200_OK)


class DefaultShippingFeeVIew(APIView):
    def get(self, request, *args, **kwargs):
        state = request.query_params.get('defaultState', None)
        country = request.query_params.get('defaultCountry', None)
        shipping_fee = int(2000)
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.get_order_total() >= int(10000):
            shipping_fee = int(0)
            return Response({"shipping_fee": shipping_fee, "state": state}, status=HTTP_200_OK)
        else:
            if country == "Nigeria":
                if state == "Abuja Federal Capital Territory":
                    shipping_fee = int(0)
                    print(state)
                    return Response({"shipping_fee": shipping_fee, "state": state}, status=HTTP_200_OK)
                else:
                    print(state)
                    shipping_fee = int(2000)
                    return Response({"shipping_fee": shipping_fee, "state": state}, status=HTTP_200_OK)
            print(state)
            return Response(status=HTTP_200_OK)


class AddDefaultShippingFeeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        shipping = request.data.get('shippingFee', None)

        print(shipping)
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.shipping_fee:
            order.shipping_fee = float(shipping)
            order.order_price = order.get_order_total()
            order.order_final_price = order.get_order_final_total()
            order.save()
            return Response(status=HTTP_200_OK)
        order.order_price = order.get_order_total()
        order.order_final_price = order.get_order_final_total()
        order.shipping_fee = float(shipping)
        order.save()
        return Response(status=HTTP_200_OK)


class CreateReviewView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        review = request.data.get('comment', None)
        rating = request.data.get('rating', None)
        item = get_object_or_404(Item, slug=slug)

        reviews = Reviews(
            user=self.request.user,
            item=item,
            review=review,
            rating=rating

        )
        reviews.save()
        return Response({"message": "You are amazing, review successful"}, status=HTTP_201_CREATED)


class NewsletterView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = NewsletterSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", None)
        existing = Newsletter.objects.filter(email=email).count()

        if existing == 0:
            news = Newsletter(
                email=email
            )
            news.save()
            return Response({"message": "You have signed up for the newsletter"}, status=HTTP_201_CREATED)
        else:
            return Response({"message": "You have already used this email"}, status=HTTP_400_BAD_REQUEST)


class ContactView(CreateAPIView):
    queryset = Contact
    serializer_class = ContactSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        serializer.save()
        user_data = serializer.data
        name = user_data['name']
        email = user_data['email']
        subject = user_data['subject']
        message = user_data['message']

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
        mail = EmailMessage(
            'We have a new Contact mail',
            template,
            "contact@janes-fashion.com",
            ['contact@janes-fashion.com']

        )
        mail.fail_silently = False
        mail.send()


class AddressCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone", None)
        country = request.data.get("country", None)
        state = request.data.get("shipState", None)
        address_text = request.data.get("address", None)
        zip = request.data.get("zip", None)
        default = request.data.get("defaultChecked", None)
        if default:
            for address in Address.objects.filter(user=self.request.user, default=True):
                address.default = False
                address.save()
            address = Address(
                user=self.request.user,
                phone=phone,
                country=country,
                state=state,
                address=address_text,
                zip=zip,
                default=True
            )
            address.save()
            order = Order.objects.get(user=request.user, ordered=False)
            order.shipping_address = address
            order.save()
            return Response(status=HTTP_200_OK)

        else:
            address = Address(
                user=self.request.user,
                phone=phone,
                country=country,
                state=state,
                zip=zip,
                default=False
            )
            address.save()
            order = Order.objects.get(user=request.user, ordered=False)
            order.address = address
            # order.save()
            return Response(status=HTTP_200_OK)


class AddressDefaultCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        addDefaultAddress = request.data.get("addDefaultAddress", None)
        address = get_object_or_404(Address, user=request.user, default=True)
        order = Order.objects.get(user=request.user, ordered=False)
        order.shipping_address = address
        order.save()
        return Response(status=HTTP_200_OK)


class PaymentCheckView(ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class PaymentCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        reference = request.data.get("ref", None)
        amount = request.data.get("amount", None)
        order = Order.objects.get(user=request.user, ordered=False)
        payment = Payment(
            user=self.request.user,
            reference=reference,
            amount=amount
        )
        payment.save()
        order.payment_reference = reference
        order.payment = payment
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()
        order.ordered = True
        order.save()
        return Response(status=HTTP_200_OK)


class AddressListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by("-date")


class DefaultAddressListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, default=True)


class OrderedItemsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, ordered=True).order_by("-ordered_date")


class RecentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        slug = request.data.get("slug", None)
        if slug is None:
            return Response(status=HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        viewed = RecentlyViewed.objects.filter(
            user=self.request.user, item=item)
        if viewed.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        RecentlyViewed.objects.create(user=self.request.user, item=item)
        return Response({"message": "You have added an item to your wishlist"}, status=HTTP_200_OK)
