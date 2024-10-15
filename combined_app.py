import gradio as gr
from dotenv import load_dotenv
import os
from app import create_chat_interface, predict, load_history_from_db, validate_user
from assistant_manager import create_assistant_manager_interface, get_assistants, get_available_models, get_all_vector_stores
from db_init import init_all_dbs

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化所有数据库
init_all_dbs()

# 创建 Gradio 界面
with gr.Blocks(theme=gr.themes.Base()) as demo:
    gr.Markdown("## 冯律师法律服务团队专属GPT")

    with gr.Tab("聊天界面"):
        chat_interface, history_display, history_button, assistant_dropdown, username_state, token_usage = create_chat_interface()
        
        def set_username(request: gr.Request):
            username = request.username
            return username
        
        demo.load(fn=set_username, inputs=None, outputs=username_state)
        demo.load(fn=lambda username: load_history_from_db(username), inputs=username_state, outputs=history_display)

    with gr.Tab("Assistant管理"):
        assistants = gr.State(get_assistants())
        available_models = gr.State(get_available_models())
        vector_stores = gr.State(get_all_vector_stores())

        with gr.Tab("创建Assistant"):
            with gr.Row():
                with gr.Column(scale=2):
                    name_input = gr.Textbox(label="Assistant名称")
                    instructions_input = gr.Textbox(label="指令", lines=5)
                    model_input = gr.Dropdown(label="模型", choices=get_available_models())
                    vector_store_dropdown = gr.Dropdown(label="选择Vector Store", choices=[vs[0] for vs in get_all_vector_stores() if vs[0]])
                    create_button = gr.Button("创建Assistant")
                
                with gr.Column(scale=1):
                    vector_store_name_input = gr.Textbox(label="新Vector Store名称")
                    create_vector_store_button = gr.Button("创建Vector Store")
        
        # ... 其他标签页的代码 ...

        create_assistant_manager_interface()

# 启动 Gradio 应用，添加用户认证功能
if __name__ == "__main__":
    demo.launch(auth=validate_user, auth_message="请登录以访问聊天界面")
