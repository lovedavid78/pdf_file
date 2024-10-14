# @文档 https://www.gradio.app/docs/
# @gradio python   API参考 https://www.gradio.app/docs/python-client
# @gradio API参考 https://www.gradio.app/docs
# @openai API参考 https://platform.openai.com/docs/api-reference/introduction
import openai
import gradio as gr
import sqlite3
from dotenv import load_dotenv
import os
import pandas as pd
import traceback
import requests
import json
import base64

print(openai.__version__)
# 加载环境变量
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 初始化数据库
def init_db():
    conn = sqlite3.connect('assistants.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assistants
                 (id TEXT PRIMARY KEY,
                  name TEXT,
                  instructions TEXT,
                  model TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS uploaded_files
                 (id TEXT PRIMARY KEY,
                  filename TEXT,
                  vector_store_id TEXT,
                  assistant_id TEXT)''')
    conn.commit()
    conn.close()

# 创建新的assistant
def create_assistant(name, instructions, model, vector_store_id):
    try:
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        # 保存到数据库
        conn = sqlite3.connect('assistants.db')
        c = conn.cursor()
        c.execute("INSERT INTO assistants VALUES (?, ?, ?, ?)",
                  (assistant.id, name, instructions, model))
        conn.commit()
        conn.close()
        return f"Assistant创建成功: {assistant.id}"
    except Exception as e:
        return f"创建失败: {str(e)}"

# 添加一个新函数来获取所有的 vector stores
def get_all_vector_stores():
    try:
        vector_stores = client.beta.vector_stores.list()
        # 过滤掉名称为 None 的 vector stores
        return [(vs.name, vs.id) for vs in vector_stores.data if vs.name is not None]
    except Exception as e:
        print(f"获取 vector stores 列表时出错: {str(e)}")
        return []

# 修改更新 assistant 的函数
def update_assistant(assistant_id, instructions, model, vector_store_id):
    try:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            instructions=instructions,
            model=model,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        # 更新数据库
        conn = sqlite3.connect('assistants.db')
        c = conn.cursor()
        c.execute("UPDATE assistants SET instructions=?, model=? WHERE id=?",
                  (instructions, model, assistant_id))
        conn.commit()
        conn.close()
        return f"Assistant更新成功: {assistant.id}"
    except Exception as e:
        return f"更新失败: {str(e)}"

# 获取所有assistants
def get_assistants():
    conn = sqlite3.connect('assistants.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM assistants")
    assistants = c.fetchall()
    conn.close()
    return {assistant[1]: assistant[0] for assistant in assistants}

# 添加新函数来获取所有assistants的详细信息
def get_all_assistants():
    api_assistants = client.beta.assistants.list()
    
    conn = sqlite3.connect('assistants.db')
    c = conn.cursor()
    c.execute("SELECT id, name, instructions, model FROM assistants")
    local_assistants = {row[0]: row for row in c.fetchall()}
    conn.close()
    
    assistants_info = []
    for assistant in api_assistants:
        local_info = local_assistants.get(assistant.id)
        if local_info:
            assistants_info.append((assistant.name, local_info[2], assistant.model, "已同步"))
        else:
            assistants_info.append((assistant.name, "点击更新获取指令", assistant.model, "需要更新"))
    
    return assistants_info

# 添加更新本地assistant信息的函数
def update_local_assistant(assistant_id):
    try:
        # 从API获取assistant信息
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        # 更新本地数据库
        conn = sqlite3.connect('assistants.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO assistants (id, name, instructions, model) VALUES (?, ?, ?, ?)",
                  (assistant.id, assistant.name, assistant.instructions, assistant.model))
        conn.commit()
        conn.close()
        
        return f"Assistant {assistant.name} 已更新到本地"
    except Exception as e:
        return f"更新失败: {str(e)}"

# 添加个新函数来获取可用的模型列表
def get_available_models():
    try:
        models = client.models.list()
        # 过滤出适合 Assistants 的模型
        assistant_models = [model.id for model in models if model.id.startswith(("gpt-3.5", "gpt-4"))]
        return assistant_models
    except Exception as e:
        print(f"获取模型列表时出错: {str(e)}")
        return ["gpt-3.5-turbo", "gpt-4"]  # 返回默认模型列表作为后备

# 修改 get_assistant_files 函数
def get_assistant_files(assistant_id):
    try:
        print(f"Attempting to get files for assistant: {assistant_id}")
        
        # 获取 assistant 详情
        assistant = client.beta.assistants.retrieve(assistant_id)
        print(f"Assistant details: {assistant}")
        
        # 检查是否有 file_search 工具
        file_search_tool = next((tool for tool in assistant.tools if tool.type == 'file_search'), None)
        
        if file_search_tool and assistant.tool_resources and assistant.tool_resources.file_search:
            vector_store_ids = assistant.tool_resources.file_search.vector_store_ids
            print(f"Vector store IDs: {vector_store_ids}")
            
            file_info = []
            for vector_store_id in vector_store_ids:
                # 这里需要根据 OpenAI 的 API 文档确定如何使用 vector_store_id 获取文件信息
                # 以下是一个示例，实际使用时可能需要调
                files = client.files.list(purpose="assistants", vector_store_id=vector_store_id)
                for file in files.data:
                    file_info.append({"id": file.id, "name": file.filename})
            
            print(f"File info: {file_info}")
            return file_info
        else:
            print("No file search tool or vector store IDs found for this assistant.")
            return []
    except Exception as e:
        print(f"获取assistant文件列表时出错: {str(e)}")
        print(f"错误类型: {type(e)}")
        print(traceback.format_exc())
        return []

# 新函数：获取assistant向量存储和文件列表
def get_assistant_vector_stores_and_files(assistant_id):
    try:
        print(f"Attempting to get vector stores and files for assistant: {assistant_id}")
        
        assistant = client.beta.assistants.retrieve(assistant_id)
        print(f"Assistant details: {assistant}")
        
        vector_stores_and_files = []
        if hasattr(assistant, 'tool_resources') and assistant.tool_resources:
            if hasattr(assistant.tool_resources, 'file_search') and assistant.tool_resources.file_search:
                vector_store_ids = assistant.tool_resources.file_search.vector_store_ids
                for vector_store_id in vector_store_ids:
                    try:
                        #  requests 库直接调用 OpenAI API
                        url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
                        headers = {
                            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                            "OpenAI-Beta": "assistants=v2"
                        }
                        response = requests.get(url, headers=headers)
                        response.raise_for_status()
                        
                        files = response.json()
                        print('files===',files)
                        file_info = []
                        for file in files['data']:
                            file_info.append({
                                "id": file['id'],
                                "name": file['filename'],
                                "created_at": file['created_at']
                            })
                        
                        vector_stores_and_files.append({
                            "vector_store_name": vector_store_id,  # 这里假设没有名称信息
                            "vector_store_id": vector_store_id,
                            "files": file_info
                        })
                    except Exception as e:
                        print(f"Error retrieving vector store {vector_store_id} or its files: {str(e)}")
        
        print(f"Vector stores and files: {vector_stores_and_files}")
        return vector_stores_and_files
    except Exception as e:
        print(f"获取assistant向量存储和文件列表时出错: {str(e)}")
        print(f"错误类型: {type(e)}")
        print(traceback.format_exc())
        return []

# 更新 load_assistant_info 函数
def load_assistant_info(assistant_name):
    if assistant_name is None:
        return "", "", "", []
    assistant_id = get_assistants().get(assistant_name)
    if assistant_id is None:
        return "", "", "", []
    assistant = client.beta.assistants.retrieve(assistant_id)
    vector_stores_and_files = get_assistant_vector_stores_and_files(assistant_id)
    return assistant.name, assistant.instructions, assistant.model, vector_stores_and_files

# 上传文件到 vector store
def upload_file_to_vector_store(file, assistant_id):
    try:
        assistant = client.beta.assistants.retrieve(assistant_id)
        vector_store_ids = assistant.tool_resources.file_search.vector_store_ids
        if not vector_store_ids:
            return "没有找到关联的 vector store。"

        vector_store_id = vector_store_ids[0]  # 假设只使用第一个 vector store

        # 首先创建一个文件
        with open(file.name, 'rb') as f:
            created_file = client.files.create(
                file=f,
                purpose='assistants'
            )

        # 然后将文件添加到 vector store
        uploaded_file = client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=created_file.id
        )

        # 获取上传的文件信息
        print('uploaded_file===', uploaded_file)
        file_id = uploaded_file.id
        file_vector_store_id = uploaded_file.vector_store_id
        file_name = file.name

        # 保存上传信息到数据库
        conn = sqlite3.connect('assistants.db')
        c = conn.cursor()
        c.execute("INSERT INTO uploaded_files (id, filename, vector_store_id, assistant_id) VALUES (?, ?, ?, ?)",
                  (file_id, file_name, file_vector_store_id, assistant_id))
        conn.commit()
        conn.close()

        return f"文件上传成功: ID={file_id}, 文件名={file_name}, Vector Store ID={file_vector_store_id}"
    except Exception as e:
        print(f"文件上传失败: {str(e)}")
        print(f"错误类型: {type(e)}")
        return f"文件上传失败: {str(e)}"

# 在 create_assistant_manager_interface 函数中更新相关部分
def create_assistant_manager_interface():
    assistants = gr.State(get_assistants())
    available_models = gr.State(get_available_models())
    vector_stores = gr.State(get_all_vector_stores())

    with gr.Tab("创建Assistant"):
        with gr.Row():
            with gr.Column(scale=2):
                name_input = gr.Textbox(label="Assistant名称")
                instructions_input = gr.Textbox(label="指令", lines=5)
                model_input = gr.Dropdown(label="模型", choices=lambda: available_models.value)
                vector_store_dropdown = gr.Dropdown(label="选择Vector Store", choices=lambda: [vs[0] for vs in vector_stores.value if vs[0]])
                create_button = gr.Button("创建Assistant")
            
            with gr.Column(scale=1):
                vector_store_name_input = gr.Textbox(label="新Vector Store名称")
                create_vector_store_button = gr.Button("创建Vector Store")
        
        create_button.click(
            create_assistant_with_info,
            inputs=[name_input, instructions_input, model_input, vector_store_dropdown],
            outputs=gr.Info()
        )
        
        create_vector_store_button.click(
            create_vector_store,
            inputs=[vector_store_name_input],
            outputs=[gr.Info(), vector_store_dropdown]
        )

    with gr.Tab("更新Assistant"):
        with gr.Row():
            assistant_dropdown = gr.Dropdown(label="选择助手", choices=lambda: list(assistants.value.keys()))
            update_model_input = gr.Dropdown(label="选择模型", choices=lambda: available_models.value)
            vector_store_dropdown = gr.Dropdown(label="选择存储", choices=lambda: vector_stores.value)
        update_instructions_input = gr.Textbox(label="新指令", lines=5)
        update_button = gr.Button("更新Assistant")
        vector_stores_and_files_list = gr.JSON(label="关联的向量存储和文件")

        assistant_dropdown.change(
            load_assistant_info,
            inputs=[assistant_dropdown],
            outputs=[update_instructions_input, update_model_input, vector_store_dropdown, vector_stores_and_files_list]
        )
        
        update_button.click(
            update_assistant_wrapper,
            inputs=[assistant_dropdown, update_instructions_input, update_model_input, vector_store_dropdown],
            outputs=gr.Info()
        )

    # 修改列出Assistants的标签页
    with gr.Tab("列出Assistants"):
        list_button = gr.Button("刷新Assistant列表")
        assistants_table = gr.Dataframe(
            headers=["名称", "指令", "模型", "状态"],
            label="Assistants列表"
        )
        update_local_button = gr.Button("更新选中的Assistant到本地")

        def update_assistants_list():
            return get_all_assistants()

        def update_selected_assistant(selected_data):
            if isinstance(selected_data, pd.DataFrame) and not selected_data.empty:
                assistant_name = selected_data.iloc[0]['名称']
                assistant_id = next((a.id for a in client.beta.assistants.list() if a.name == assistant_name), None)
                if assistant_id:
                    result = update_local_assistant(assistant_id)
                    return gr.Info(result)
                return gr.Info(f"无法找到名为 {assistant_name} 的Assistant")
            return gr.Info("请选择一个Assistant进行更新")

        list_button.click(
            update_assistants_list,
            outputs=assistants_table
        )
        update_local_button.click(
            update_selected_assistant,
            inputs=assistants_table,
        )

    with gr.Tab("上传文件到Assistant"):
        assistant_dropdown = gr.Dropdown(label="选择Assistant", choices=lambda: list(assistants.value.keys()))
        file_upload = gr.File(label="选择文件")
        upload_button = gr.Button("上传文件")

        def upload_file(assistant_name, file):
            if assistant_name is None or file is None:
                return gr.Info("请选择一个Assistant并选择一个文件。")
            assistant_id = assistants.value.get(assistant_name)
            if assistant_id is None:
                return gr.Info(f"无法找到名为 {assistant_name} 的Assistant")
            result = upload_file_to_vector_store(file, assistant_id)
            return gr.Info(result)

        upload_button.click(
            upload_file,
            inputs=[assistant_dropdown, file_upload],
        )

    return assistants

# 初始化数据库
init_db()

# 如果直接运行此文件，启动Gradio应用
if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.Markdown("## Assistant管理器")
        create_assistant_manager_interface()
    demo.launch()