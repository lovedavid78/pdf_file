import gradio as gr
from dotenv import load_dotenv
import os
from app import create_chat_interface, predict, load_history_from_db, init_db as init_app_db
from user import create_user_management_interface, init_db as init_user_db, validate_user
from assistant_manager import create_assistant_manager_interface, init_db as init_assistant_db

# 加载 .env 文件中的环境变量
load_dotenv()
username_state = gr.State()

# 用户认证函数
def custom_auth(username, password):
    return validate_user(username, password)

# 初始化所有数据库
init_app_db()
init_user_db()
init_assistant_db()

# 创建 Gradio 界面
with gr.Blocks(theme=gr.themes.Base()) as demo:
    gr.Markdown("## 冯律师法律服务团队专属GPT")

    with gr.Tab("聊天界面"):
        history_display, chat_interface, history_button = create_chat_interface()
        history_button.click(fn=lambda: load_history_from_db(username_state.value), outputs=history_display)

    with gr.Tab("用户管理"):
        create_user_management_interface()

    with gr.Tab("Assistant管理"):
        create_assistant_manager_interface()

    # 重写 predict 函数以包含 username
    def predict_with_username(message, history, file=None):
        return predict(message, history, file, username_state.value)

    chat_interface.fn = predict_with_username

# 启动 Gradio 应用，添加用户认证功能
if __name__ == "__main__":
    demo.launch(auth=custom_auth)
