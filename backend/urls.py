from django.urls import path
from backend import views

urlpatterns = [
    path('/', views.credentials),
    # path('/agents', views.agents),
    path('/credentials', views.credentials), # rememeber that this is backend/credentials on the server
    path('/addCredential', views.addCredential),
    path('/protocols', views.protocols),
    path('/endpoints', views.endpoints),
    path('/tasks', views.tasks),
    path('/taskresults', views.credentials),
    path('/files', views.files),
    path('/logs', views.logs),
]
