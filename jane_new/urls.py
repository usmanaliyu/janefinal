
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('jet/dashboard/', include('jet.dashboard.urls',
                                   'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    path("paystack", include(('paystack.urls', 'paystack'), namespace='paystack')),
    path('', include('blog.urls'))
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.handler404"

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns
