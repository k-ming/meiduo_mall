import random
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
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
        # 1、生成验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 2、创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # logger.info(redis_conn)
        # 3、把验证码存储到reids数据库
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # 4、利用容联云通讯发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 5、响应
        return Response({'message': 'ok'})