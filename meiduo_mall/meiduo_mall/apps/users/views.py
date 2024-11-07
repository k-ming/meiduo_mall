from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .serializer import UserSerializer
from rest_framework.views import APIView
from .models import User
from logging import getLogger
logger = getLogger('django')
# Create your views here.

class UserRegistView(CreateAPIView):
    serializer_class = UserSerializer

# 判断用户是否重复
class UserNameCount(APIView):
    def get(self, request, username=None):
        count = User.objects.filter(username=username).count()
        data = {
            'count': count,
            'username': username
        }
        return Response(data)

# 判断手机号是否重复
class UserMobileCount(APIView):
    def get(self, request, mobile=None):
        # logger.info(mobile)
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'count': count,
            'mobile': mobile
        }
        return Response(data)