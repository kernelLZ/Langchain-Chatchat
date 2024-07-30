import json
import logging
import requests

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_user_input(prompt: str) -> str:
    """获取用户输入的查询数据的query"""
    return input(prompt)

def send_request(query: str, knowledge_base_name: str):
    base_url = "http://127.0.0.1:7861"  # 假设这是你的API地址
    url = f"{base_url}/chat/kb_chat"
    payload = {
        'query': query,
        'mode': 'local_kb',  # 确保模式是 'local_kb'，与 kb_chat 函数的参数匹配
        'kb_name': knowledge_base_name,
        'history': [],
        'prompt_name': "default",
        'stream': False  # 如果需要流式输出可以设置为 True
    }

    logger.debug(f"Sending request to {url} with payload: {payload}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查响应状态码是否为200
        
        content_type = response.headers.get('Content-Type', '')
        logger.debug(f"Response Content-Type: {content_type}")
        logger.debug(f"Response Text: {response.text}")

        if 'application/json' in content_type:
            data = response.json()
            logger.debug(f"Received JSON response: {data}")
            
            # 检查JSON结构
            if "choices" in data and isinstance(data["choices"], list):
                choice = data["choices"][0]
                if "message" in choice and isinstance(choice["message"], dict):
                    message = choice["message"]
                    if "content" in message:
                        # 清理content字段中的字符串，去除多余的引号和换行符
                        content_str = message["content"].strip().replace('"', "'").replace('\n', '')
                        # 尝试解析content字段中的JSON字符串
                        try:
                            content_json = json.loads(content_str)
                            logger.debug(f"Extracted content: {content_json}")
                            print(content_json)
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding JSON from content: {e}")
                            print(f"Error decoding JSON from content: {e}")
                    else:
                        logger.error("Missing 'content' in message")
                        print("Missing 'content' in message")
                else:
                    logger.error("Unexpected structure in choices or missing message")
                    print("Unexpected structure in choices or missing message")
            else:
                logger.error("Unexpected JSON structure")
                print("Unexpected JSON structure")
        else:
            # 处理非JSON响应
            raw_text = response.text.strip()
            print(raw_text)

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        print(f"请求发生错误: {e}")

if __name__ == "__main__":
    current_kb = None

    while True:
        if current_kb is None:
            query_type = get_user_input("请问您是要查指标还是查数据表？（输入'指标'或'数据表'，输入'退出'以结束程序）: ")
            if query_type.lower() == '退出':
                print("程序结束。")
                break

            if query_type == '指标':
                current_kb = '指标知识库'
            elif query_type == '数据表':
                current_kb = 'test'
            else:
                print("输入无效，请输入'指标'或'数据表'")
                continue

        query = get_user_input("请输入您想要查找的数据: ")
        if query.lower() == '切换至指标':
            current_kb = '指标知识库'
            print("已切换到指标知识库。")
            continue
        elif query.lower() == '切换至数据表':
            current_kb = 'test'
            print("已切换到数据表知识库。")
            continue

        send_request(query, current_kb)