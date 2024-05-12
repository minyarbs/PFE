from django.urls import path
from . import views
urlpatterns = [
    path('',views.homepage,name=""),
    path('home',views.homepage,name="home"),
    path('register',views.register,name="register"),
    path('login',views.login,name="login"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('logout',views.user_logout,name="logout"),
    path('charts',views.charts,name="charts"),
    path('EmployeeFraud',views.EmployeeFraud,name="EmployeeFraud"),
    path('reasons',views.Reasons,name="reasons"),
    path('OneEmployee',views.OneEmployee,name="OneEmployee"),
    path('EmployeeDashboard',views.EmployeeDashboard,name="EmployeeDashboard"),
    path('FraudView',views.FraudView,name="FraudView"),
    path('AccountInfo',views.AccountInfo,name="AccountInfo"),
    path('AboutCompany',views.AboutCompany,name="AboutCompany"),
    path('AboutITserv',views.AboutITServ,name="AboutITserv"),
    path('update_fraud_status/', views.update_fraud_status, name='update_fraud_status'),
    path('<int:employeeId>/2015-<int:selected_month>-<int:day>', views.events_by_date, name='events_by_date'),
]