from rest_framework.views import exception_handler as drf_exception_handler 
import logging
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status
# 获取在配置⽂文件中定义的logger，⽤用来记录⽇日志 
logger = logging.getLogger('django')
def exception_handler(exc, context):
    """
    ⾃自定义异常处理理
    :param exc: 异常
    :param context: 抛出异常的上下⽂文(包含request和view对象) 
    :return: Response响应对象
    """
    # 调⽤用drf框架原⽣生的异常处理理⽅方法
    response = drf_exception_handler(exc, context)
    if response is None:
        view = context['view']
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            # 数据库异常
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器器内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
    return response