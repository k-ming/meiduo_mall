import random
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
from rest_framework import status
import logging
logger = logging.getLogger('django')


# Create your views here.

class SMSCodeView(APIView):
    ''' 短信验证码 '''
    def get(self, request, mobile):
        """
        :param request:
        :param mobile:
        :return:
        """
        # 1、创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # logger.info(redis_conn)
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({'message':'发送验证码过于频繁'}, status=status.HTTP_400_BAD_REQUEST)
        # 2、生成验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 2.1 生成reids管道，提升性能
        pl = redis_conn.pipeline()
        # 3、把验证码存储到reids数据库
        pl.setex('sms_%s' % mobile, 300, sms_code)
        # 3.1、存储已发手机号标记
        pl.setex('send_flag_%s' % mobile, 60, 1)
        # 3.2 执行redis管道
        pl.execute()
        # 4、利用容联云通讯发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 5、响应
        return Response({'message': 'ok'})