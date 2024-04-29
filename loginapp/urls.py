from django.urls import path
from . import views
urlpatterns = [
    path('',views.homepage,name=""),
    path('register',views.register,name="register"),
    path('login',views.login,name="login"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('logout',views.user_logout,name="logout"),
    path('charts',views.charts,name="charts"),
    path('EmployeeFraud',views.EmployeeFraud,name="EmployeeFraud"),
    path('reasons',views.Reasons,name="reasons"),
    path('OneEmployee',views.OneEmployee,name="OneEmployee"),
    path('EmployeeDashboard',views.EmployeeDashboard,name="EmployeeDashboard"),
    path('FraudView',views.FraudView,name="FraudView")
]