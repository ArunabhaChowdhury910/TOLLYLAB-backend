from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
# from .views import GoogleLogin 

# class GoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
    
#     @csrf_exempt
#     def post(self, request, *args, **kwargs):
#         print(request.data)  # Add this line to inspect incoming OAuth data
#         return super().post(request, *args, **kwargs)

#     # def get(self, request, *args, **kwargs):
#     #     # Force clear the Sites Framework cache
#     #     Site.objects.clear_cache()
        
#     #     # Create a default Site object if one doesn't exist
#     #     if not Site.objects.exists():
#     #         Site.objects.create(domain='localhost:8000', name='localhost')
        
#     #     return super().get(request, *args, **kwargs)



urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=True)),  # Redirect root to /api/
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),  # Include the urls from the `api` app
    
    # path('accounts/', include('allauth.urls')), 
    # path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login')
    
    path('accounts/', include('allauth.urls')),  # Allauth routes for social logins
    path('dj-rest-auth/', include('dj_rest_auth.urls')),  # dj-rest-auth routes
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),  # Registration routes

    
    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('accounts/', include('allauth.urls')),
    # path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),

    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)