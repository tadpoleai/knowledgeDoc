#! /usr/bin/env python
# coding=utf8
import grpc
# from gRPC_example import #! /usr/bin/env python
# coding=utf8
import grpc
import jeffery_pb2_grpc, jeffery_pb2
import time

def request_translation():
    '''
    模拟请求翻译
    '''
    conn=grpc.insecure_channel('localhost:50050')
    client = jeffery_pb2_grpc.AIGCStub(channel=conn)
    
    translation_data = jeffery_pb2.TranslationRequest(direction = 0)  # CHINESE_TO_ENGLISH
    request = jeffery_pb2.CreateTextRequest(text="我是一名人工智能助手，我需要你替我翻译这段文字", randomness=0,  translation = translation_data)
    
    respnse = client.CreateText(request)
    print("received:",respnse.translation_answers)

def request_writing():
    '''
    模拟请求文案书写
    '''
    conn=grpc.insecure_channel('localhost:50050')
    client = jeffery_pb2_grpc.AIGCStub(channel=conn)
    
    copygen_data = jeffery_pb2.CopyGenerationRequest(platforms = [0,1,2,3])  # CHINESE_TO_ENGLISH
    request = jeffery_pb2.CreateTextRequest(text="我是一名人工智能助手，我需要你写成我需要的文案类型", randomness=0,  copy_generation = copygen_data)
    
    respnse = client.CreateText(request)
    print("received:",respnse.copy_generation_answers)  
    
if __name__ == '__main__':
    request_translation()
    time.sleep(0.5)
    request_writing()
    
    
