# @文档 https://www.gradio.app/docs/
# @gradio python   API参考 https://www.gradio.app/docs/python-client
# @gradio API参考 https://www.gradio.app/docs
# @openai API参考 https://platform.openai.com/docs/api-reference/introduction

import openai
import gradio as gr
from dotenv import load_dotenv
import datetime
import os
from docx import Document
import pypdf
import sqlite3
from assistant_manager import get_assistants
import tiktoken


# 加载 .env 文件中的环境变量
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MAX_TOKENS = 32000  # GPT-4 的最大 token 限制
MAX_FILE_CONTENT_TOKENS = 8000  # 限制文件内容的 token 数量

# 修改用户验证函数
def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    if result:
        print(f"Debug: User validated: {username}")
        return True
    print("Debug: User validation failed")
    return False

# 处理文件上传
def process_file(file):
    if file:
        file_extension = file.name.split('.')[-1].lower()
        file_content = ""

        if file_extension == 'txt':
            # 处理 txt 文件
            with open(file.name, 'r', encoding='utf-8') as f:
                file_content = f.read()

        elif file_extension == 'docx':
            # 处理 docx 文件
            doc = Document(file.name)
            file_content = "\n".join([para.text for para in doc.paragraphs])

        elif file_extension == 'pdf':
            # 理 pdf 文件
            with open(file.name, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    file_content += reader.pages[page_num].extract_text()

        elif file_extension == 'doc':
            # 处理 doc 文件 (使用 python-docx 处理 doc 格式)
            import pypandoc
            file_content = pypandoc.convert_file(file.name, 'docx')

        return file_content

    return ""

# 将对话历史保存到数据库中
def save_history_to_db(username, role, content):
    if username:
        conn = sqlite3.connect('chat_history.db')
        c = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO chat_history (username, timestamp, role, content) VALUES (?, ?, ?, ?)",
                  (username, timestamp, role, content))
        conn.commit()
        conn.close()
    else:
        print("Error: username is empty in save_history_to_db")

# 从数据库中读取历史对话
def load_history_from_db(username):
    if username and username != "未登录":
        conn = sqlite3.connect('chat_history.db')
        c = conn.cursor()
        c.execute("SELECT timestamp, role, content FROM chat_history WHERE username=? ORDER BY timestamp", (username,))
        rows = c.fetchall()
        conn.close()
        if rows:
            history = "\n".join([f"{row[0]} - {row[1]}: {row[2]}" for row in rows])
            return history
    return "无历史对话。"

# 调用 OpenAI 模型进行聊天对话
def predict(message, history, assistant_name, file=None, username=None):
    print(f"Debug: predict function called with username: {username}")
    if not username:
        return "错误：用户名为空，请确保您已正确登录。"

    # 获取助手ID
    assistants = get_assistants()
    assistant_id = assistants.get(assistant_name)
    if not assistant_id:
        return f"错误：找不到名为 '{assistant_name}' 的助手。"

    # 处理文件上传
    if file:
        file_content = process_file(file)
        user_message = f"文档内容: {file_content}\n\n{message}"
    else:
        user_message = message

    save_history_to_db(username, "用户", user_message)

    # 修改这里的历处理逻辑
    history_openai_format = []
    for h in history:
        if isinstance(h, dict) and "role" in h and "content" in h:
            history_openai_format.append({"role": h["role"], "content": h["content"]})
        elif isinstance(h, list) and len(h) == 2:
            history_openai_format.append({"role": "user" if h[0] else "assistant", "content": h[1]})

    history_openai_format.append({"role": "user", "content": user_message})

    # 使用选定的助手创建新的线程和消息
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    # 运行助手
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # 等待运行完成
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        # 获取助手的回复
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_message = next((m for m in messages if m.role == "assistant"), None)

        if assistant_message:
            response_content = assistant_message.content[0].text.value
            save_history_to_db(username, "模型", response_content)
            
            # 计算 token 使用量
            input_tokens = num_tokens_from_string(user_message, "cl100k_base")
            output_tokens = num_tokens_from_string(response_content, "cl100k_base")
            total_tokens = input_tokens + output_tokens
            
            # 更新用户的总 token 使用量
            update_user_token_usage(username, total_tokens)
            
            return response_content, total_tokens
        else:
            return "助手没有生成回复。", 0
    except Exception as e:
        return f"发生错误：{str(e)}", 0

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def update_user_token_usage(username, tokens):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET total_tokens = total_tokens + ? WHERE username = ?", (tokens, username))
    conn.commit()
    conn.close()

# 创建 Gradio 界面
def create_chat_interface():
    assistants = get_assistants()
    assistant_choices = list(assistants.keys())
    
    with gr.Blocks() as chat_interface:
        with gr.Row():
            with gr.Column(scale=1, min_width=100):
                with gr.Accordion("历史对话", open=False):
                    history_display = gr.Textbox(label="历史对话", interactive=False, lines=20)
                    history_button = gr.Button("刷新历史对话")
                with gr.Accordion("上传文件", open=True):
                    file_upload = gr.File(label="上传文件", elem_id="file_upload")
                with gr.Accordion("选择助手", open=True):
                    assistant_dropdown = gr.Dropdown(choices=assistant_choices, label="选择助手", value=assistant_choices[0] if assistant_choices else None)
            with gr.Column(scale=3, min_width=400):
                token_usage = gr.Number(label="本次会话 Token 使用量", value=0)
                chatbot = gr.Chatbot(height=400, type="messages")
                msg = gr.Textbox(label="输入消息")
                send_btn = gr.Button("发送")
        
        username_state = gr.State("")
    
    def user(user_message, history, assistant_name, file, username):
        return "", history + [{"role": "user", "content": user_message}], 0
    
    def bot(history, assistant_name, file, username, current_usage):
        user_message = history[-1]["content"]
        bot_message, tokens = predict(user_message, history[:-1], assistant_name, file, username)
        history.append({"role": "assistant", "content": bot_message})
        return history, current_usage + tokens
    
    msg.submit(user, [msg, chatbot, assistant_dropdown, file_upload, username_state], [msg, chatbot, token_usage]).then(
        bot, [chatbot, assistant_dropdown, file_upload, username_state, token_usage], [chatbot, token_usage]
    )
    send_btn.click(user, [msg, chatbot, assistant_dropdown, file_upload, username_state], [msg, chatbot, token_usage]).then(
        bot, [chatbot, assistant_dropdown, file_upload, username_state, token_usage], [chatbot, token_usage]
    )
    
    def update_history():
        username = username_state.value
        return load_history_from_db(username)
    
    history_button.click(fn=update_history, outputs=history_display)
    return chat_interface, history_display, history_button, assistant_dropdown, username_state, token_usage

# 主程序部分
if __name__ == "__main__":
    with gr.Blocks() as demo:
        chat_interface, history_display, history_button, assistant_dropdown, username_state, token_usage = create_chat_interface()
        
        def set_username(request: gr.Request):
            username = request.username
            return username
        
        demo.load(fn=set_username, inputs=None, outputs=username_state)
        demo.load(fn=lambda username: load_history_from_db(username), inputs=username_state, outputs=history_display)
    
    demo.launch(auth=validate_user, auth_message="请登录以访问聊天界面")
