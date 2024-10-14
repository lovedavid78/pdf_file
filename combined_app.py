import gradio as gr
from dotenv import load_dotenv
import os
from app import create_chat_interface, predict, load_history_from_db, validate_user
from user import create_user_management_interface
from assistant_manager import create_assistant_manager_interface
from db_init import init_all_dbs

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化所有数据库
init_all_dbs()

# 创建 Gradio 界面
with gr.Blocks(theme=gr.themes.Base()) as demo:
    gr.Markdown("## 冯律师法律服务团队专属GPT")

    with gr.Tab("聊天界面"):
        chat_interface, history_display, history_button, assistant_dropdown, username_state = create_chat_interface()
        
        demo.load(fn=lambda: load_history_from_db(gr.State().value), outputs=history_display)

    with gr.Tab("用户管理"):
        create_user_management_interface()

    with gr.Tab("Assistant管理"):
        create_assistant_manager_interface()

# 启动 Gradio 应用，添加用户认证功能
if __name__ == "__main__":
    demo.launch(auth=validate_user, auth_message="请登录以访问聊天界面")
