from django.urls import path
from .views import registro
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]