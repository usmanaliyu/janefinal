from django.db.models import fields
from rest_framework import serializers
from .models import Contact, Coupon, Newsletter, CustomUser, Item, Order, OrderItem, Address, Payment, Reviews, Wishlist
from dj_rest_auth.registration.serializers import RegisterSerializer
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("reference",
                  "user",
                  "amount",
                  "timestamp")


class ReviewsSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Reviews
        fields = (
            "user",
            "item",
            "review",
            "rating",
            'time',
            'user_details'

        )

    def get_user_details(self, obj):
        return UserInfo(obj.user).data


class ItemSerializer(serializers.ModelSerializer):
    category = StringSerializer()
    percentage = serializers.SerializerMethodField()
    tags = TagListSerializerField()
    # reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ("id",
                  "title",
                  "price",
                  "category",
                  "new_arrival",
                  "discount_price",
                  "label",
                  'slug',
                  "image",
                  "image_1",
                  "image_2",
                  "image_3",
                  "image_4",
                  "description",
                  "color",
                  "percentage",
                  "tags",
                  #   "reviews_count"

                  )

    def get_percentage(self, obj):
        return obj.get_percentage()

    # def get_reviews_count(self, obj):
    #     return obj.get_reviews_count()


class OrderItemSerializer(serializers.ModelSerializer):
    item = StringSerializer()
    item_obj = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'item',
            'item_obj',
            'quantity',
            "final_price"

        )

    def get_item_obj(self, obj):
        return ItemSerializer(obj.item).data

    def get_final_price(self, obj):
        return obj.get_final_price()


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    get_order_total = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "order_items",
            "total",
            "ref_code",
            "shipping_fee",
            "get_order_total",
            "coupon",
            "get_order_final_total",
            "order_price",
            "order_final_price",
            "ordered_date"

        )

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()

    def get_order_total(self, obj):
        return obj.get_order_total()

    def get_order_final_total(self, obj):
        return obj.get_order_final_total()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            "id",
            "code",
            "amount"
        )


class WishlistSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = "__all__"

    def get_item(self, obj):
        return ItemSerializer(obj.item).data


class UserInfo(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            "email",

        )


class UserRegistration(RegisterSerializer):
    first_name = serializers.CharField(max_length=200)
    last_name = serializers.CharField(max_length=200)

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username",
                  "email", "password", "check_password")

    def save(self, request):
        user = super().save(request)
        user.first_name = self.data.get('first_name')
        user.last_name = self.data.get('last_name')
        user.save()
        return user


class AddressSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = (
            'id',
            'user',
            'address',
            'country',
            'zip',
            'phone',
            'state',
            "user_details"
        )

    def get_user_details(self, obj):
        return UserInfo(obj.user).data
