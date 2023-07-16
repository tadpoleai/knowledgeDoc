#! /usr/bin/env python
# coding=utf8
import time
from concurrent import futures
import grpc
import jeffery_pb2_grpc, jeffery_pb2
from WritingProcessor import WritingProcessor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
class TestService(jeffery_pb2_grpc.AIGCServicer):
    '''
    继承GrpcServiceServicer,实现CreateText方法
    '''
    def __init__(self):
        self.wp = WritingProcessor()
        pass
    def CreateText(self, request, context):
        
        if request.HasField("translation"):
            
            _, res = self.wp.translate(request.text, request.randomness, request.translation.direction)
                        
            return jeffery_pb2.CreateTextResponse(translation_answers = [res['dataList']],
                                                  copy_generation_answers={})
            pass
        elif request.HasField("copy_generation"):
            # multi_output = {"weibo": "this is weibo result",
            #                 "wechat": "this is wechat result"}
            
            
            _, res = self.wp.copywrite(request.text, request.randomness)
            
            
            return jeffery_pb2.CreateTextResponse(translation_answers = [],
                                        copy_generation_answers=res['dataList'])
            pass
        else:
            pass
        
def run():
    '''
    模拟服务启动
    :return:
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    jeffery_pb2_grpc.add_AIGCServicer_to_server(TestService(),server)
    server.add_insecure_port('[::]:50050')
    server.start()
    print("start service...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
if __name__ == '__main__':
    run()