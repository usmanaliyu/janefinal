from django.db.models.fields.related import ForeignKey
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField


FEATURE_CHOICES = (
    ('none', 'None'),
    ('featured_accessories', 'Featured Accessories'),
    ('featured_bags', 'Featured Bags'),
    ('featured_clothing', 'Featured Clothing'),
    ('featured_footwear', 'Featured Footwear'),


)


COLOR = (
    ('black', 'Black'),
    ('white', 'White'),
    ('red', 'Red'),
    ('pink', 'Pink'),
    ('green', 'Green'),
    ('purple', 'Purple'),
    ('brown', 'Brown'),




)


class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=250, blank=True)
    slug = models.SlugField(max_length=250)

    class Meta:
        unique_together = ['name', 'slug']
        ordering = ['name']
        verbose_name_plural = 'categories'

    def get_category_url(self):
        return reverse("core:categoryview", kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return self.name

    @property
    def get_category_count(self):
        return self.item_set.all().count()


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    new_arrival = models.BooleanField(default=False, blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE)
    color = models.CharField(
        choices=COLOR, max_length=1000, blank=True,  null=True)
    label = models.CharField(choices=FEATURE_CHOICES, max_length=1000)
    slug = models.SlugField()
    description = RichTextField(blank=True,  null=True)
    size_chart = models.ImageField(blank=True,  null=True)
    image = models.ImageField()
    image_1 = models.ImageField(blank=True,  null=True)
    image_2 = models.ImageField(blank=True,  null=True)
    image_3 = models.ImageField(blank=True,  null=True)
    image_4 = models.ImageField(blank=True,  null=True)
    tags = TaggableManager()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ['title', 'slug']

    def get_percentage(self):
        if self.discount_price:
            percent = self.discount_price - self.price
            return percent / 100

    @property
    def get_reviews_count(self):
        return self.reviews_set.all().count()

    @property
    def get_reviews(self):
        return self.reviews_set.all()


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    order_price = models.CharField(max_length=200, blank=True, null=True)
    order_final_price = models.CharField(max_length=200, blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_fee = models.FloatField(blank=False, null=True)

    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def get_order_total(self):
        total = self.get_total()
        if self.coupon:
            total -= self.coupon.amount
            return total
        return total

    def get_order_final_total(self):
        total = self.get_order_total()
        if self.shipping_fee:
            total += self.shipping_fee
            return total
        return total


def add_ref_code(sender, instance, created, *args, **kwargs):
    if created:
        instance.ref_code = instance.id
        instance.save()


post_save.connect(add_ref_code, sender=Order)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    address = models.TextField(blank=False, null=True)
    country = models.CharField(max_length=100, blank=False, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=False, null=True)
    state = models.CharField(max_length=255, blank=False, null=True)
    default = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=False, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    reference = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15, blank=False, null=True)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)


class Slider(models.Model):
    title = models.CharField(max_length=20, blank=True, null=True)
    text = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField()
    link = models.URLField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.title


class HomepageBanner(models.Model):
    image = models.ImageField()
    link = models.URLField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=100)
    description = models.CharField(blank=True, null=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image"


class About(models.Model):
    link = models.URLField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class HomesideBanner(models.Model):
    image = models.ImageField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image"


class ShoptopBanner(models.Model):
    image = models.ImageField()
    title = models.CharField(max_length=100, blank=True, null=True)
    text = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image"


class ShopbottomBanner(models.Model):
    image = models.ImageField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image"


class Reviews(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rating = models.IntegerField(blank=False, null=True)
    review = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Reviews'


class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    subject = models.CharField(max_length=30)
    message = models.TextField(max_length=300)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.author.username


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Newsletter(models.Model):
    email = models.EmailField(max_length=254)

    def __str__(self):
        return self.email


class Team(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class RecentlyViewed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
