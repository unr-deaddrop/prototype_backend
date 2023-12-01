from django.urls import path
from backend import views

urlpatterns = [
    path('/', views.credentials),
    # path('/', views.agents),
    path('/credentials', views.credentials), # rememeber that this is backend/credentials on the server
    path('/addCredential', views.addCredential)
]
