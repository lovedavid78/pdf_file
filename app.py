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


def test_user_authentication():
    init_db()
    add_user("test_user", "test_password")
    assert validate_user("test_user", "test_password") == True
    assert validate_user("fake_user", "fake_password") == False

# 加载 .env 文件中的环境变量
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
username_state = gr.State()
MAX_TOKENS = 32000  # GPT-4 的最大 token 限制
MAX_FILE_CONTENT_TOKENS = 8000  # 限制文件内容的 token 数量


# 初始化数据库
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  timestamp TEXT,
                  role TEXT,
                  content TEXT)''')
    conn.commit()
    conn.close()

# 添加用户
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# 用户验证函数，并将用户名存储到 State
def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    if result:
        username_state.value = username
        return True
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
            # 处理 pdf 文件
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
        conn = sqlite3.connect('users.db')
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
    if username:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT timestamp, role, content FROM chat_history WHERE username=? ORDER BY timestamp", (username,))
        rows = c.fetchall()
        conn.close()
        if rows:
            history = "\n".join([f"{row[0]} - {row[1]}: {row[2]}" for row in rows])
            return history
    return "无历史对话。"

# 调用 OpenAI 模型进行聊天对话
def predict(message, history, file=None, username=None):
    if username is None:
        username = username_state.value

    # 处理文件上传
    if file:
        file_content = process_file(file)
        user_message = f"文档内容: {file_content}\n\n{message}"
    else:
        user_message = message

    save_history_to_db(username, "用户", user_message)

    # OpenAI API调用部分保持不变
    history_openai_format = [{"role": h["role"], "content": h["content"]} for h in history]
    history_openai_format.append({"role": "user", "content": user_message})

    # 调用OpenAI API
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=history_openai_format,
        temperature=1.0,
        stream=True
    )

    partial_message = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            partial_message += chunk.choices[0].delta.content
            yield partial_message

    save_history_to_db(username, "模型", partial_message)
    return partial_message

# 验证用户登录
def custom_auth(username, password):
    return validate_user(username, password)

# 在主程序开始时初始化数据库
init_db()

# 创建 Gradio 界面
def create_chat_interface():
    history_display = gr.Textbox(label="历史对话", interactive=False)
    chat_interface = gr.ChatInterface(
        fn=predict,
        additional_inputs=[gr.File(label="上传文件")],
        title="聊天界面",
    )
    history_button = gr.Button("显示历史对话")
    return history_display, chat_interface, history_button

# 启动 Gradio 应用，添加用户认证功能
# demo.launch(auth=custom_auth)

# 如果你想在单独运行app.py时启动应用，可以添加以下代码：
if __name__ == "__main__":
    with gr.Blocks() as demo:
        history_display, chat_interface, history_button = create_chat_interface()
        history_button.click(fn=lambda: load_history_from_db(username_state.value), outputs=history_display)
    demo.launch(auth=custom_auth)
