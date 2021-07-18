from django.urls import path, include
from . import views

app_name = "core"


urlpatterns = [
    path('list/', views.ListView.as_view(), name="list"),
    path('contact/', views.ContactView.as_view(), name="contact"),
    path('newsletter/', views.NewsletterView.as_view(), name="newsletter"),
    path('add-to-cart/', views.AddToCartView.as_view(), name="add-to-cart"),
    path('order-summary/', views.OrderDetailView.as_view(), name="order-summary"),
    path('order-item/delete/',
         views.OrderItemDeleteView.as_view(), name="order-item-delete"),
    path('order-item/update-quantity/', views.OrderQuantityupdateView.as_view(),
         name="order-item-update-quantity"),
    path('address-list/', views.AddressListView.as_view(), name="Address-list"),
    path('address/create/', views.AddressCreateView.as_view(), name="address-create"),
    path('product/<slug>/', views.ProductDetailsView.as_view(),
         name="product-details"),
    path('check-wishlist/', views.CheckWishlistView.as_view(),
         name="check-wishlist"),
    path('wishlist/', views.AddToWishListView.as_view(),
         name="wishlist"),
    path('review/', views.CreateReviewView.as_view(),
         name="review"),
    path('check-review/', views.CheckReviewsView.as_view(),
         name="check-review"),
    path('check-tags/', views.CheckTagsView.as_view(),
         name="check-tags"),
    path('add-coupon/', views.AddCouponView.as_view(),
         name="add-coupon"),
    path('paystackkey/', views.PaystackkeyView.as_view(), name='paystack'),
    path('user-email/', views.UserEmailView.as_view(), name='user-email'),
    path('fetch-saved/', views.FetchWishlistView.as_view(), name='fetch-saved'),
    path('delete-saved/', views.DeleteFromWishlistView.as_view(), name='delete-saved'),
    path('shipping-fee/', views.ShippingFeeVIew.as_view(), name='shipping-fee'),
    path('add-shipping-fee/', views.AddShippingFeeView.as_view(),
         name='add-shipping-fee'),
    path('payment-done/', views.PaymentCreateView.as_view(),
         name='payment-done'),
    path('ordered-items/', views.OrderedItemsView.as_view(),
         name='ordered-items'),
    path('delete-address/', views.DeleteAddressView.as_view(),
         name='delete-address'),
    path('get-order-details/', views.CheckOrderDetailsView.as_view(),
         name="get-order-details"),
    path('get-order-item-details/', views.CheckOrderItemDetailsView.as_view(),
         name="get-order-items-details"),
    path('get-user/', views.UserDetailsView.as_view(), name="get-user"),
    path('related-post/', views.RelatedPostView.as_view(), name="related-post"),
    path('default-address/', views.DefaultAddressListView.as_view(),
         name="default-address"),

    path('default-shipping-fee/',
         views.DefaultShippingFeeVIew.as_view(), name='shipping-fee'),
    path('add-default-shipping-fee/', views.AddDefaultShippingFeeView.as_view(),
         name='add-shipping-fee'),
    path('address/create/default/',
         views.AddressDefaultCreateView.as_view(), name="address-create"),
    path('payment-check/',
         views.PaymentCheckView.as_view(), name="payment-check"),
    path('shop/',
         views.ShopListView.as_view(), name="shop"),
    path('shop-search/',
         views.SearchView.as_view(), name="shop-search"),
   path('recent-viewed/',
         views.RecentView.as_view(), name="recent-viewed"),
         




































]
