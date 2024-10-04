from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()


def list_files(startpath):
    markdown_lines = []

    for root, dirs, files in os.walk(startpath):
        # 计算当前文件夹的相对路径
        relative_root = os.path.relpath(root, startpath)
        if relative_root == ".":
            relative_root = ""  # 根文件夹

        # 添加当前文件夹的标题
        markdown_lines.append(f"## {relative_root if relative_root else '根目录'}")

        for file in files:
            # 过滤掉 ".DS_Store" 文件
            if file == ".DS_Store":
                continue

            # 添加文件的Markdown格式
            file_path = os.path.join(relative_root, file)
            markdown_lines.append(f"- [{file}]({file_path})")

    return "\n".join(markdown_lines)


# 设置要遍历的文件夹路径
folder_path = os.getenv('ICLOUD') # 请替换为你的文件夹路径

# 获取文件列表的Markdown格式
markdown_output = list_files(folder_path)

# 输出到Markdown文件
with open("file_list.md", "w", encoding="utf-8") as md_file:
    md_file.write(markdown_output)

print("文件名已按Markdown格式输出到 file_list.md")