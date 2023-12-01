from django.urls import path, include
from backend import views
from backend.views import CredentialViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'credential-viewset', CredentialViewSet, basename='credentials')

urlpatterns = [
    path('/', views.credentials),
    # path('/agents', views.agents),
    path('/credentials/', include(router.urls)),
    # path('/credentials', views.credentials), # rememeber that this is backend/credentials on the server
    path('/addCredential', views.addCredential),
    path('/protocols', views.protocols),
    path('/endpoints', views.endpoints),
    path('/tasks', views.tasks),
    path('/taskresults', views.credentials),
    path('/files', views.files),
    path('/logs', views.logs),
]
