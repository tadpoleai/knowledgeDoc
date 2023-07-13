# 基于Markdown文件的检索和问答

markdown能够较好的保留问答的层级和图表内容，对于完整的文档来说是很重要的特性
对于一般的simiiarity检索不能对标题和内容都有很好的效果，hybrid search能够有效缓解这类问题

## 创建虚拟环境

1. Create a virtual environment with python 3.9(best practice)
2. `pip install -r requirements.txt`
3. 替换.env中相关的环境变量,OPENAI_API_KEY,WEAVIATE_URL,WEAVIATE_API_KEY
4. 如果是在vscode中调试，可以在.vscode/launch.json中修改对应的参数，然后在vscode中进行两个步骤的调试

### 在console中使用
1. python main.py -t ingest -c "your_md_directory" to ingest data
2. python mian.py -t query -c "your_question" to ask a question

如果使用vscode可以在调试时，在launch.json中增加这两个参数
"args" : ["-t", "ingest", "-c", "your data directory"]
"args" : ["-t", "query", "-c", "your question"]

如果在终端中使用
```bash
python main.py -t ingest -c "./docs"
python main.py -t query -c "执行成本中心费用分摊分配后余额不平怎么处理"
```