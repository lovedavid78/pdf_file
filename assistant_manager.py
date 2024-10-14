import openai
import gradio as gr
import sqlite3
from dotenv import load_dotenv
import os

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
    conn.commit()
    conn.close()

# 创建新的assistant
def create_assistant(name, instructions, model):
    try:
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model
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
        return f"创建���败: {str(e)}"

# 更新已有的assistant
def update_assistant(assistant_id, name, instructions, model):
    try:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            name=name,
            instructions=instructions,
            model=model
        )
        # 更新数据库
        conn = sqlite3.connect('assistants.db')
        c = conn.cursor()
        c.execute("UPDATE assistants SET name=?, instructions=?, model=? WHERE id=?",
                  (name, instructions, model, assistant_id))
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
    conn = sqlite3.connect('assistants.db')
    c = conn.cursor()
    c.execute("SELECT id, name, instructions, model FROM assistants")
    assistants = c.fetchall()
    conn.close()
    return assistants

# Gradio界面
def create_assistant_manager_interface():
    assistants = gr.State(get_assistants)

    with gr.Tab("创建Assistant"):
        name_input = gr.Textbox(label="Assistant名称")
        instructions_input = gr.Textbox(label="指令", lines=5)
        model_input = gr.Dropdown(["gpt-3.5-turbo", "gpt-4"], label="模型")
        create_button = gr.Button("创建Assistant")
        create_output = gr.Textbox(label="结果")
        
        create_button.click(
            create_assistant,
            inputs=[name_input, instructions_input, model_input],
            outputs=create_output
        )

    with gr.Tab("更新Assistant"):
        assistant_dropdown = gr.Dropdown(choices=list(assistants.value.keys()), label="选择Assistant")
        update_name_input = gr.Textbox(label="新名称")
        update_instructions_input = gr.Textbox(label="新指令", lines=5)
        update_model_input = gr.Dropdown(["gpt-3.5-turbo", "gpt-4"], label="新模型")
        update_button = gr.Button("更新Assistant")
        update_output = gr.Textbox(label="结果")
        
        def update_assistant_wrapper(assistant_name, name, instructions, model):
            assistant_id = assistants.value[assistant_name]
            return update_assistant(assistant_id, name, instructions, model)
        
        update_button.click(
            update_assistant_wrapper,
            inputs=[assistant_dropdown, update_name_input, update_instructions_input, update_model_input],
            outputs=update_output
        )

    # 添加新的标签页来列出所有assistants
    with gr.Tab("列出Assistants"):
        list_button = gr.Button("刷新Assistant列表")
        assistants_table = gr.Dataframe(
            headers=["ID", "名称", "指令", "模型"],
            label="Assistants列表"
        )

        def update_assistants_list():
            return get_all_assistants()

        list_button.click(
            update_assistants_list,
            outputs=assistants_table
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
