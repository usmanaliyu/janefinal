
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [

    path('account/reset/<uidb64>/<token>/',
         TemplateView.as_view(template_name="password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    path("paystack", include(('paystack.urls', 'paystack'), namespace='paystack')),
    path('blog/', include('blog.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/registration/', include('dj_rest_auth.registration.urls'))
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
