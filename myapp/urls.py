from django.urls import path,include
from .import views

urlpatterns = [
    path("",views.Home,name="home"),
    path("login/",views.Login,name="login"),
    path("signup/",views.Signup,name="signup"),
    path('logout/', views.Logout, name='logout'),
    path('verify-otp/', views.VerifyOTP, name='verify_otp'),
]
