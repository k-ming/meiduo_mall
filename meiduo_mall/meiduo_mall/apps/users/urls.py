from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'userRegister/', views.UserRegistView.as_view(), name='userRegister'),
    url(r'userNameCount/(?P<username>\w{5,20})/$', views.UserNameCount.as_view(), name='userNameCount'),
    url(r'userMobileCount/(?P<mobile>1[3-9]\d{9})/$', views.UserMobileCount.as_view(), name='userMobileCount'),
    url(r'^authorizations/$', obtain_jwt_token),
]