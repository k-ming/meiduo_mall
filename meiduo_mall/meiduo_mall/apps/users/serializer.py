from rest_framework import serializers
from .models import User
import re
from django_redis import get_redis_connection
import logging

logger = logging.getLogger('django')
from rest_framework_jwt.settings import api_settings


class UserSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(label='验证码', write_only=True)
    password2 = serializers.CharField(label='密码2', write_only=True)
    allow = serializers.BooleanField(label='协议', write_only=True)
    token = serializers.CharField(label='登录token状态', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'sms_code', 'allow', 'password', 'password2', 'token')

        # 重新修改字段属性
        extra_kwargs = {  # 修改字段选项
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {  # 自定义校验出错后的错误信息提示
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 校验手机号格式
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式有误！')
        return value

    # 校验协议是否同意
    def validate_allow(self, value):
        if value != True:
            raise serializers.ValidationError('请先同意协议！')
        return value

    def validate(self, attrs):
        # 建立redis链接
        redis_conn = get_redis_connection('verify_codes')
        # 先获取手机号
        mobile = attrs.get('mobile')
        # 获取reids中的验证并decode
        redis_code = redis_conn.get('sms_%s' % mobile)
        if not redis_code or redis_code.decode() != attrs.get('sms_code'):
            raise serializers.ValidationError('验证码失效或错误！')

        # 检查2次输入的密码是否一致
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError("两次输入的密码不一致！")

        return attrs

    # 重写create方法，去除不必要存入数据可的字段
    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        password = validated_data.pop('password')  # 移除并取出密码
        user = User.objects.create(**validated_data)
        user.set_password(password)

        # 注册用户成功的同时生成jwt token 返回给前端
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)

        user.save()
        return user
