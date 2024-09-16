from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('upload/', views.upload_pricelist, name='upload_pricelist'),
    path('processed_data/', views.processed_data, name='processed_data'),
    path('save_pricelist/', views.save_pricelist, name='save_pricelist'),
    path('pricelist_saved/', views.pricelist_saved, name='pricelist_saved'),
    path('error/', views.error, name='error'),
    path('new-list/', views.create_list, name='new_list'),
    path('list/<int:list_id>/', views.list_detail, name='list_detail'), 
    path('lists/', views.list_overview, name='list_overview'),
    path('pricelists/', views.pricelists_list, name='pricelists_list'),
    path('pricelist/<int:pricelist_id>/', views.pricelist_detail, name='pricelist_detail'),



]
