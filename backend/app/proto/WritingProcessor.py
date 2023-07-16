# -*- coding: utf-8 -*-
import openai
import sys
import json
import time
import os
import jieba

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class WritingProcessor():
    paragraph=""
    __results_num=3
    __calc_count=0
    __total_tokens=0

    def __init__(self):
        # self.api_key=api_key
        # openai.api_key = api_key
        # self.__start_time=start_time
        sensitive_words=["独裁","极左","国家机器","内部斗争","修改宪法","修宪","言论自由","因言获罪","言论封锁","新闻自由","新闻管制","法西斯","法东斯","中南海","华春莹","华大妈","网络审查","政治改革","政改","翻墙","VPN","普选","党禁","集权","打压异己","权斗","威权主义","地缘政治","大跃进","宪政","文字狱","包砸"]
        [jieba.add_word(word) for word in sensitive_words]
        # for word in sensitive_words:
        #     jieba.add_word(word)
        self.__sensitive_words_dict=dict(zip(sensitive_words,range(len(sensitive_words))))
        # temperature_type_dict={"严谨":0.4,"一般严谨":0.7,"中等":1,"一般创意":1.3,"创意":1.6}
        # if temperature_type in temperature_type_dict:
        #     self._temperature=temperature_type_dict[temperature_type]
        # else:
        #     self._temperature =1


    def detect_sensitive_words(self,para_list):
        article = ';'.join(para_list)
        seg_list = jieba.lcut(article, cut_all=False)
        # seg_list = jieba.lcut_for_search(article)
        sensitive_num=0
        sensitive_words=[]
        for seg in seg_list:
            if seg in self.__sensitive_words_dict:
                sensitive_num+=1
                sensitive_words.append(seg)
        # time_end = time.time()
        # cost_time = time_end - start_time
        # print(cost_time)
        if sensitive_num>=2 or sensitive_num/len(article)>0.03:
            return True,sensitive_words
        else:
            return False,sensitive_words


    def copywrite(self,text, temperature_):
        start_time = time.time()
        
        
        prompt_xiaohonghsu = "你是小红书爆款写作专家，但你不要显式地说明自己的专家身份，请你用以下步骤来进行创作，首先产出5个标题(含适当的emoji表情)，其次产出1个正文(每一个段落含有适当的emoji表情，文末有合适的tag标签) " \
                         "一、在小红书标题方面，你会以下技能:" \
                         "1.采用二极管标题法进行创作" \
                         "2.你善于使用标题吸引人的特点" \
                         "3.你使用爆款关键词，写标题时，从这个列表中随机选1-2个" \
                         "4.你了解小红书平台的标题特性" \
                         "5.你懂得创作的规则" \
                         "6.20个字符以内（emoji和英文占半字符）" \
                         "二、在小红书正文方面，你会以下技能:" \
                         "1.写作风格" \
                         "2.写作开篇方法" \
                         "3.文本结构" \
                         "4.互动引导方法" \
                         "5.一些小技巧" \
                         "6.爆炸词" \
                         "7.从你生成的稿子中，抽取3-6个seo关键词，生成#标签并放在文章最后" \
                         "8.文章的每句话都尽量口语化、简短" \
                         "9.在每段话的开头使用表情符号，在每段话的结尾使用表情符号，在每段话的中间插入表情符号" \
                         "10.正文结尾：欢迎读者留言、提问、关注，例：“欢迎提问SMU会计学院申请流程，期待您的关注”" \
                         "三、结合我给你输入的信息，以及你掌握的标题和正文的技巧，产出内容。请按照如下格式输出内容，只需要格式描述的部分，如果产生其他内容则不输出:" \
                         "'''一、标题" \
                         "[标题1到标题5]" \
                         "[换行]" \
                         "二.正文" \
                         "[正文]" \
                         "标签:[标签]" \
                         "'''下面是我给你的输入信息：'''{text}'''"

        prompt_douyin = "你是抖音爆款写作专家，但你不要显式地说明自己的专家身份，请你用以下步骤来对我给你的输入的信息进行创作，首先产出5个标题，其次产出1个正文 " \
                        "一、在抖音标题方面，你会以下技能:" \
                        "1.采用二极管标题法进行创作" \
                        "2.你善于使用标题吸引人的特点" \
                        "3.你了解抖音平台的标题特性" \
                        "4.你懂得创作的规则" \
                        "二、在抖音正文方面，你会以下技能:" \
                        "1.写作风格" \
                        "2.写作开篇方法" \
                        "3.文本结构" \
                        "4.一些小技巧，如渲染情绪、设置悬念" \
                        "5.文章的每句话都尽量口语化" \
                        "6.引导用户互动。结尾尽量使用疑问句和反问句，可以留开放式问题。" \
                        "三、结合我给你输入的信息，以及你掌握的标题和正文的技巧，产出内容。请按照如下格式输出内容，只需要格式描述的部分，如果产生其他内容则不输出:" \
                        "'''一、标题" \
                        "[标题1到标题5]" \
                        "[换行]" \
                        "二.正文" \
                        "[正文]" \
                        "'''下面是我给你的输入信息：'''{text}'''"

        prompt_weibo = "你是微博爆款写作专家，但你不要显式地说明自己的专家身份，请你用以下步骤来对我给你的输入的信息进行创作，产出1个正文 " \
                       "在微博正文方面，你会以下技能:" \
                       "1.写作风格，总结成一段话，不要换行，尽量不超过250字" \
                       "2.总结出1个话题，生成#话题#并尽量放在正文开头" \
                       "3.可以在文中增加需要@的对象" \
                       "4.每句话都尽量口语化" \
                       "三、结合我给你输入的信息，以及你掌握微博正文技巧，产出内容。请按照如下格式输出内容，只需要格式描述的部分，如果产生其他内容则不输出:" \
                       "'''[正文]" \
                       "'''下面是我给你的输入信息：'''{text}'''"

        prompt_wechat = "你是微信公众号爆款写作专家，但你不要显式地说明自己的专家身份，请你用以下步骤来对我给你的输入的信息进行创作，首先产出5个标题，其次产出1个正文 " \
                        "一、在微信公众号标题方面，你会以下技能:" \
                        "1.采用二极管标题法进行创作" \
                        "2.你善于使用标题吸引人的特点" \
                        "3.你使用爆款关键词，写标题时，从这个列表中随机选1-2个" \
                        "4.你了解微信公众号平台的标题特性" \
                        "5.你懂得创作的规则" \
                        "二、在微信公众号摘要方面，你会以下技能:" \
                        "提取关键信息写成摘要" \
                        "三、在微信公众号正文方面，你会以下技能:" \
                        "1.写作风格相对正式" \
                        "2.写作开篇方法" \
                        "3.文本结构" \
                        "4.一些写作小技巧，如渲染情绪、设置悬念" \
                        "5.互动引导方法" \
                        "三、结合我给你输入的信息，以及你掌握的标题和正文的技巧，产出内容。请按照如下格式输出内容，只需要格式描述的部分，如果产生其他内容则不输出:" \
                        "'''一、标题" \
                        "[标题1到标题5]" \
                        "[换行]" \
                        "二.摘要" \
                        "[摘要]" \
                        "三.正文" \
                        "[正文]" \
                        "'''下面是我给你的输入信息：'''{text}'''"

        content_douyin=prompt_douyin.format(text=text)
        content_weibo=prompt_weibo.format(text=text)
        content_wechat=prompt_wechat.format(text=text)
        content_xiaohongshu=prompt_xiaohonghsu.format(text=text)

        result_douyin=self.process_from_gpt(content_douyin, temperature_)
        result_weibo =self.process_from_gpt(content_weibo, temperature_)
        result_wechat =self.process_from_gpt(content_wechat, temperature_)
        result_xiaohongshu =self.process_from_gpt(content_xiaohongshu, temperature_)

        #写入output_json
        datalist = {'douyin': '', 'weibo': '', 'wechat': '', 'wechat': ''}
        datalist['douyin']=result_douyin
        datalist['weibo']=result_weibo
        datalist['wechat']=result_wechat
        datalist['xiaohongshu']=result_xiaohongshu

        end_time = time.time()
        cost_time = round(end_time - start_time, 2)

        output_dict=dict()
        output_dict['success'] = True
        output_dict['timeOut'] = False
        output_dict['errorDesc'] = ''
        output_dict['tokenCount'] = self.__total_tokens
        output_dict['calcCount']=self.__calc_count
        output_dict['costTime'] = str(cost_time)
        output_dict['dataList'] = datalist

        output_json = json.dumps(output_dict, ensure_ascii=False)
        return output_json, output_dict

    def translate(self,text, temperature_, direction):
        start_time = time.time()
        
        if direction == 1:
            prompt="你是一名专业的商务翻译专家，擅长将英文翻译为中文，请翻译下面这段话，并用中文输出：'''{text}'''"
        else:
            prompt="你是一名专业的商务翻译专家，擅长将英文翻译为中文，请翻译下面这段话，并用英文输出：'''{text}'''"
            
        content = prompt.format(text=text)

        result = self.process_from_gpt(content, temperature_)

        # 写入output_json
        datalist = {'translate': ''}
        datalist['translate'] = result

        end_time = time.time()
        cost_time = round(end_time - start_time, 2)

        output_dict = dict()
        output_dict['success'] = True
        output_dict['timeOut'] = False
        output_dict['errorDesc'] = ''
        output_dict['tokenCount'] = self.__total_tokens
        output_dict['calcCount'] = self.__calc_count
        output_dict['costTime'] = str(cost_time)
        output_dict['dataList'] = result#datalist

        output_json = json.dumps(output_dict, ensure_ascii=False)
        return output_json, output_dict

    def process_from_gpt(self,content="",  temperature_=0, n=1):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": content}],
            temperature=temperature_,
            n=n
        )
        self.__calc_count += 1
        self.__total_tokens+=completion.usage.total_tokens
        result = completion.choices[0].message.content.encode('utf-8').decode("utf-8")
        return result

    def chs2eng(self,paragraph="", n=1):
        results = []
        sim_scores = []
        total_tokens = 0
        prompt = "Translate the following sentences into English with academic style, ensure the output sentences to be purer and more fluent:"
        content = prompt + paragraph
        eng_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": content}],
            n=n
        )
        self.__calc_count += 1
        for i in range(n):
            eng_result = eng_completion.choices[i].message.content.encode('utf-8').decode("utf-8")
            results.append(eng_result)
            sim_scores.append(1)
        total_tokens += eng_completion.usage.total_tokens

        return results, sim_scores, total_tokens

    def integrate_1_para(self,text):
        text=text.replace("\n", "")
        return text

    def remove_summary(self,paragraph,result):
        ori_sentence_num=len(paragraph.split('。'))-1
        keywords = ['因此', '总之', '综上所述', '综上']
        result = result.replace("\n", "")
        sentence_list=result.split('。')
        if sentence_list[-1]=='': #若list最后为空，则去掉
            sentence_list=sentence_list[:-1]

        summary_keyword_1 = sentence_list[-1].split('，')[0]
        if len(sentence_list)-ori_sentence_num>3: #当给出的结果多出3句话时，才会去考察最后一句话
            summary_keyword_2 = sentence_list[-2].split('，')[0]
            if summary_keyword_2 in keywords:
                sentence_list = sentence_list[:-2]  #去除总结性的倒数两句话。
                sentence_list.append('')  #此处加回来是为了下一句加句号
                new_result='。'.join(sentence_list)
                return new_result
        if summary_keyword_1 in keywords:
            sentence_list = sentence_list[:-1]  # 去除总结性的最一句话。
            sentence_list.append('')  # 此处加回来是为了下一句加句号
            new_result = '。'.join(sentence_list)
            return new_result
        return result

    def check_if_chinese(self,result):
        words_num=0
        chinese_num=0
        for _char in result:
            words_num+=1
            if not '\u4e00' <= _char <= '\u9fa5':
                chinese_num+=1
        if chinese_num/words_num<0.05:
            return False
        return True


if __name__ == "__main__":
    result = None
    errorDesc = ""
    start_time = time.time()
    if len(sys.argv)>1:
        input_json_str=sys.argv[1]
    else:
        # input_json_str='{ "taskType": "COPYWRITING","temperatureType":"中等", "sourceText": ["给各位学员，我们将为你提供一门专业的英语培训课程。此课程涵盖了基础到进阶的全部内容，包括口语、听力、阅读和写作。无论你是初学者还是希望提升自己的英语水平，这个课程都非常适合你。我们的教师团队由经验丰富的外籍老师和英语熟练使用者组成，他们将通过实用的教学方法和有趣的课堂活动，帮助你提高英语应用能力。该课程还会提供一对一辅导及定制化的学习计划，针对每位学员的需求进行精准授课。快来加入我们，一起提升英语技能，掌握全球通行证。"], "apiKey": "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","modelType":"GPT35"}'
        input_json_str = '{ "taskType": "TRANSLATE","temperatureType":"中等", "sourceText": ["Through the research, several interesting but vital factors define Singapore’s stronger resilience against global factors impacting other countries around the world in food security."], "apiKey": "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","modelType":"GPT35"}'

    input_json=json.loads(input_json_str)
    task_type=input_json["taskType"]
    para_list=input_json["sourceText"]
    api_key=input_json["apiKey"]
    if "temperatureType" in input_json:
        temperature_type=input_json["temperatureType"]
    else:
        temperature_type="中等"
    data_dict=dict(data="")
    output_dict=dict(success=False,timeOut=False,errorDesc="",tokenCount=0,dataList=data_dict)

    wp = WritingProcessor()

    if_sensitive,sensitive_words=wp.detect_sensitive_words(para_list)
    if if_sensitive:
        output_dict['errorDesc'] = ','.join(sensitive_words)
        output_dict['errorCode'] = "sensitive"
        end_time = time.time()
        cost_time = round(end_time - start_time, 2)
        output_dict['costTime'] = str(cost_time)
        output_json = json.dumps(output_dict, ensure_ascii=False)
    else:
        try:
            if task_type == "COPYWRITING":
                output_json=wp.copywrite(para_list)
            elif task_type == "TRANSLATE":
                output_json= wp.translate(para_list)
        except:
            errorDesc=sys.exc_info()[1]
            output_dict['errorDesc'] = str(errorDesc)
            end_time = time.time()
            cost_time = round(end_time - start_time, 2)
            output_dict['costTime'] = str(cost_time)
            output_json=json.dumps(output_dict,ensure_ascii=False)

    print(output_json)