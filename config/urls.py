from django.contrib import admin
from django.urls import path
from base import views
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static 
from django.conf import settings
from captcha import urls as captcha_urls
from django.urls import include, path
 

urlpatterns = [
    path('admin/', admin.site.urls),

    # Introduce
    path('introduce/', views.IntroduceView.as_view()),
    path('detail/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('thanks/', views.ThanksView.as_view(), name='thanks'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('commercial/', views.CommercialView.as_view(), name='commercial'),
    path('captcha/', include(captcha_urls)),
 
    # Account
    path('login/', views.Login.as_view()),
    path('logout/', LogoutView.as_view()),
    path('signup/', views.SignUpView.as_view()),
    path('account/', views.AccountUpdateView.as_view()),
    path('profile/', views.ProfileUpdateView.as_view()),
 
    # Order
    path('orders/<str:pk>/', views.OrderDetailView.as_view()),
    path('orders/', views.OrderIndexView.as_view()),
 
    # Pay
    path('pay/checkout/', views.PayWithStripe.as_view()),
    path('pay/success/', views.PaySuccessView.as_view()),
    path('pay/cancel/', views.PayCancelView.as_view()),
 
    # Cart
    path('cart/remove/<str:pk>/', views.remove_from_cart),
    path('cart/add/', views.AddCartView.as_view()),
    path('cart/', views.CartListView.as_view()),  # カートページ
 
    # Items
    path('items/<str:pk>/', views.ItemDetailView.as_view()),
    path('categories/<str:pk>/', views.CategoryListView.as_view()),
    path('tags/<str:pk>/', views.TagListView.as_view()),
 
    path('', views.IndexListView.as_view()),  # トップページ
]

#開発環境
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''
#本番環境
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''