from django.urls import path
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .import views
from django.conf.urls.static import static
from django.conf import settings
from myapp.python_script import *
schema_view = get_schema_view(
   openapi.Info(
      title="E commerce Recomendation system",
      default_version='r1',
      description="E commerce Recomendation System",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
   #  swagger
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   
   #  Api
    path('get_all_products/',views.get_all_products.as_view()),
    path('Registration/',views.CustomerRegistration.as_view()),
    path('VerifyEmail/',views.VerifyEmail.as_view()),
    path('Login/',views.Login.as_view()),
    path('UserLogout/',views.UserLogout.as_view()),
    path('ForgotPassword/',views.ForgotPassword.as_view()),
    path('SetNewPassword/',views.SetNewPassword.as_view()),
    path('AllBrands/',views.AllBrands.as_view()),
    path('AllSubcategories/',views.AllSubcategories.as_view()),
    path('AllCategories/',views.AllCategories.as_view()),
    path('PriceRange/',views.PriceRange.as_view()),
    path('AverageRating/',views.AverageRating.as_view()),
    path('purchase/',views.PurchaseProduct.as_view()),
    path('Recomendation/',views.ItemBasedRecommendationAPI.as_view()),
   
   #  methods
    path('get_content_based_recommendations/',views.get_content_based_recommendations,name='get_content_based_recommendations'),
    path('get_item_based_recommendations/',views.get_item_based_recommendations,name='get_item_based_recommendations'),
    path('register_all_products',views.register_all_products,name='register_all_products'),
    
   #  templates 
    path('index_page/',views.index_page,name="index_page"),
    path('signup_page/', views.signup_page, name='signup_page'),
    path('login_page/', views.login_user_page, name='login_page'),
    path('forgot_password_page/', views.forgot_password_page, name='forgot_password_page'),
    path('verify_email_page/', views.verify_email_page, name='verify_email_page'),
    path('set_new_password_page/',views.set_new_password_page,name='set_new_password_page'),
    path('home_page/',views.home_page,name='home_page'),
    path('logout_page/',views.user_logout,name='user_logout'),
    path('buy_product/',views.buy_product,name='buy_product'),
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)