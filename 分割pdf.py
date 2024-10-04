from pypdf import PdfReader, PdfWriter
import math
import os


def split_pdf(input_pdf, mode="parts", value=1, output_pdf_prefix=None):
    """
    分割PDF文件并存放在以原文件名命名的文件夹中

    参数:
    input_pdf: 输入的PDF文件路径
    mode: 分割模式，"parts"表示按份数分割，"pages"表示按每份的页数分割
    value: 对于"parts"模式，表示分割成多少份；对于"pages"模式，表示每份多少页
    output_pdf_prefix: 输出文件的前缀，默认为PDF文件名
    """

    # 提取文件名（不含扩展名）
    base_filename = os.path.splitext(os.path.basename(input_pdf))[0]

    # 创建一个以文件名为名字的输出目录
    output_dir = os.path.join(os.path.dirname(input_pdf), base_filename)

    # 如果输出目录不存在，创建该目录
    os.makedirs(output_dir, exist_ok=True)

    # 如果没有提供前缀，使用文件名作为前缀
    if output_pdf_prefix is None:
        output_pdf_prefix = base_filename

    # 打开PDF文件
    reader = PdfReader(input_pdf)

    # 获取PDF文件的总页数
    total_pages = len(reader.pages)

    if mode == "parts":
        # 按份数分割
        num_parts = value
        pages_per_part = math.ceil(total_pages / num_parts)
    elif mode == "pages":
        # 按页数分割
        pages_per_part = value
        num_parts = math.ceil(total_pages / pages_per_part)
    else:
        raise ValueError("mode参数必须是 'parts' 或 'pages'")

    for part in range(num_parts):
        writer = PdfWriter()

        # 计算当前份的开始页和结束页
        start_page = part * pages_per_part + 1
        end_page = min((part + 1) * pages_per_part, total_pages)

        # 添加该范围内的页到写入器
        for page_num in range(start_page, end_page + 1):
            writer.add_page(reader.pages[page_num - 1])

        # 创建输出文件路径
        output_filename = os.path.join(output_dir, f"{output_pdf_prefix}_part_{part + 1}.pdf")

        # 保存为新的 PDF 文件
        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)

        print(f"保存: {output_filename}, 页码范围: {start_page} - {end_page}")


def get_user_input():
    # 提示用户输入 PDF 文件路径
    input_pdf = input("请输入要分割的PDF文件路径: ")

    # 检查文件是否存在
    if not os.path.isfile(input_pdf):
        print("文件路径无效，请检查文件路径。")
        return

    # 让用户选择分割模式
    mode = input("请输入分割模式（'parts' 表示按份数分割, 'pages' 表示按每份页数分割）: ").strip().lower()

    if mode not in ["parts", "pages"]:
        print("无效的分割模式，请输入 'parts' 或 'pages'。")
        return

    # 根据模式提示用户输入对应的值
    if mode == "parts":
        value = int(input("请输入要分割的份数: "))
    elif mode == "pages":
        value = int(input("请输入每份的页数: "))

    # 调用分割 PDF 的函数
    split_pdf(input_pdf, mode=mode, value=value)


# 启动程序
if __name__ == "__main__":
    get_user_input()