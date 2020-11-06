from django.urls import path, include
from . import views

app_name = "core"


urlpatterns = [

    path('', views.HomeView.as_view(), name="home"),
    path('shop/', views.ShopView.as_view(), name="shop"),
    path('about-us/', views.AboutView.as_view(), name="about"),
    path('product/<slug>', views.DetailView.as_view(), name="details"),
    path('cart/', views.CartView.as_view(), name="cart"),
    path('checkout/', views.CheckoutView.as_view(), name="checkout"),
    path('faq/', views.FaqView.as_view(), name="faq"),
    path('contact/', views.ContactView.as_view(), name="contact"),
    path('contact/success/', views.ContactSuccessView.as_view(),
         name="contact-success"),

    path('login/', views.LoginView.as_view(), name="login"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('forgot-password/', views.ForgotView.as_view(), name="forgot"),
    path('payment/success/', views.ConfirmView.as_view(), name="pay"),
    path('payment/receipt/', views.PaystackView.as_view(), name="payment"),
    path('dashboard/', views.DashboardView.as_view(), name="dashboard"),
    path('dashboard/orders/', views.OrderView.as_view(), name="order"),

    path('dashboard/address/',
         views.AddressView.as_view(), name="address"),
    path('wishlist/<slug>/', views.wishlist, name="wishlist"),
    path('wishlist/home/<slug>/', views.wishlist_home, name="wishlist-home"),
    path('add_to_cart/<slug>', views.add_to_cart, name='add-to-cart'),
    #    path('pricing/', views.PricingView.as_view(), name="pricing" ),
    path('remove-from-cart/<slug>/',
         views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/',  views.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),

    # path('newsletter/', views.newsletter, name="newsletter"),
    path('dashboard/order/<pk>',
         views.OrderDetailView.as_view(), name='ordered-detail'),
    path('wishlist/product/<slug>/',
         views.wishlist_product, name='wishlist-product'),
    path('category/<slug>/',
         views.CategoryView, name='categoryview'),
    path('returns/', views.ReturnView.as_view(), name='returns'),
    path('add-coupon/', views.AddCouponView.as_view(), name='add-coupon'),
    path('email/', views.EmailView.as_view(), name='email'),
























]
