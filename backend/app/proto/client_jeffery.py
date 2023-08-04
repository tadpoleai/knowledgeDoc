#! /usr/bin/env python
# coding=utf8
import grpc
# from gRPC_example import #! /usr/bin/env python
# coding=utf8
import grpc
import jeffery_pb2_grpc, jeffery_pb2
import time
test_sample = '''
研究表明,新加坡能够更好地抵御导致全球粮食不安全的因素主要基于以下几点,这些内容相当有趣且至关重要。
当前的全球粮食价格冲击对新加坡的影响世界各国政府为遏制新冠疫情蔓延采取了大规模限制和封锁措施,由此引发了2022年全球粮食价格飙升。俄乌冲突进一步加剧了粮食价格危机,粮食、能源和农业投入品供应链随之中断。气候变化引发的极端天气事件加剧了这些因素造成的负面影响。中国作为世界上最大的小麦生产国之一,正在应对有史以来最严重的干旱。此前,中方发言人表示,2021年罕见的暴雨使得部分小麦推迟了种植,因此中国2022年的冬小麦产量可能是有史以来最差的一批。
新冠疫情、气候变化和俄乌冲突对全球粮食价格的综合影响促使许多主要粮食出口国对农产品实施出口禁令,以保障国内粮食安全。例如,在2022年5月至7月期间,印度出台了小麦出口禁令,限制小麦出口,马来西亚限制家禽出口,印度尼西亚禁止棕榈油及其衍生物出口,并要求生产商在国内以固定价格销售一定份额的棕榈油产品。'''

def request_translation():
    '''
    模拟请求翻译
    '''
    conn=grpc.insecure_channel('localhost:50050')
    client = jeffery_pb2_grpc.AIGCStub(channel=conn)
    
    translation_data = jeffery_pb2.TranslationRequest(direction = 0)  # CHINESE_TO_ENGLISH
    request = jeffery_pb2.CreateTextRequest(text=test_sample, randomness=0,  translation = translation_data)
    
    respnse = client.CreateText(request)
    print("received:",respnse.translation_answers)

def request_writing():
    '''
    模拟请求文案书写
    '''
    conn=grpc.insecure_channel('localhost:50050')
    client = jeffery_pb2_grpc.AIGCStub(channel=conn)
    
    copygen_data = jeffery_pb2.CopyGenerationRequest(platforms = [0,1,2,3])  # CHINESE_TO_ENGLISH
    request = jeffery_pb2.CreateTextRequest(text=test_sample, randomness=0,  copy_generation = copygen_data)
    
    respnse = client.CreateText(request)
    print("received:",respnse.copy_generation_answers)  
    
if __name__ == '__main__':
    request_translation()
    time.sleep(0.5)
    request_writing()
    
    
