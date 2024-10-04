import openai
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
import datetime
import os
from docx import Document
import PyPDF2

# 加载 .env 文件中的环境变量
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
username_state = gr.State()
MAX_TOKENS = 32000  # GPT-4 的最大 token 限制
MAX_FILE_CONTENT_TOKENS = 8000  # 限制文件内容的 token 数量


# 读取 CSV 文件中的用户信息
def load_users(file_path='users.csv'):
    df = pd.read_csv(file_path, encoding='utf-8')
    df['username'] = df['username'].astype(str)
    df['password'] = df['password'].astype(str)
    return df


# 用户验证函数，并将用户名存储到 State
def validate_user(username, password, df):
    user_row = df.loc[df['username'].str.strip() == username.strip()]
    if not user_row.empty and user_row.iloc[0]['password'].strip() == password.strip():
        username_state.value = username  # 存储用户名到 State
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
                reader = PyPDF2.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    file_content += reader.pages[page_num].extract_text()

        elif file_extension == 'doc':
            # 处理 doc 文件 (使用 python-docx 处理 doc 格式)
            import pypandoc
            file_content = pypandoc.convert_file(file.name, 'docx')

        return file_content

    return ""


# 将对话历史保存到csv文件中，文件不存在则创建
def save_history_to_file(username, role, content):
    if username:
        filename = f"{username}_history.csv"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间并格式化

        # 使用 pandas 保存记录
        new_entry = pd.DataFrame([[timestamp, role, content]], columns=["Timestamp", "Role", "Content"])

        if not os.path.exists(filename):
            new_entry.to_csv(filename, index=False, encoding='utf-8')
        else:
            new_entry.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8')
    else:
        print("Error: username is empty in save_history_to_file")


# 从csv文件中读取历史对话
def load_history_from_file(username):
    if username:
        filename = f"{username}_history.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            history = "\n".join([f"{row['Timestamp']} - {row['Role']}: {row['Content']}" for _, row in df.iterrows()])
            return history
    return "无历史对话。"


# 调用 OpenAI 模型进行聊天对话
def predict(message, history, file=None):
    username = username_state.value

    # 如果有上传文件，读取文件内容并附加到消息中
    if file:
        file_content = process_file(file)  # 获取文件内容
        file_input.clear()  # 清空文件输入
        user_message = f"文档内容: {file_content}\n\n{message}"
    else:
        user_message = message

    save_history_to_file(username, "用户", user_message)

    # 确保历史记录格式为包含 'role' 和 'content' 的字典
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

    save_history_to_file(username, "模型", partial_message)


# 验证用户登录
def custom_auth(username, password):
    return validate_user(username, password, load_users())


# 创建 Gradio 界面
with gr.Blocks(fill_height=True, theme=gr.themes.Base()) as demo:
    gr.Markdown("## 冯律师法律服务团队专属GPT")

    # 显示历史对话
    history_display = gr.Textbox(label="历史对话", interactive=False)
    chat_bot = gr.Chatbot(type='messages', line_breaks=True, show_label=False)

    # 创建文件上传组件并设置高度
    file_input = gr.File(label="上传文件",height=100,)

    chat_interface = gr.ChatInterface(
        fn=predict,
        chatbot=chat_bot,
        additional_inputs=file_input,  # 添加文件上传输入
        type='messages',
        fill_height=True,
    )

    # 按钮点击后显示历史对话
    history_button = gr.Button("显示历史对话")

    history_button.click(fn=lambda: load_history_from_file(username_state.value), outputs=history_display)

# 启动 Gradio 应用，添加用户认证功能
# demo.launch(auth=custom_auth)
demo.launch()







