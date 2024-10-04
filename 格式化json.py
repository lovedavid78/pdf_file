import requests
import json
import pandas as pd

# 从指定链接获取 JSON 数据
url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'  # 这是一个示例链接，你可以替换为你实际需要的链接
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 解析 JSON 数据
    json_data = response.json()

    # 将 JSON 数据转换为 DataFrame 表格
    # 针对 JSON 结构，选择需要转换为表格的部分
    # 例如，假设你需要将 'versions' 列表转换为表格
    if 'versions' in json_data:
        df = pd.DataFrame(json_data['versions'])
        print(df)  # 打印表格

        # 保存为 CSV 或 Excel 文件
        df.to_csv("output.csv", index=False)
        #df.to_excel("output.xlsx", index=False)
    else:
        print("无法找到 'versions' 数据。")
else:
    print(f"请求失败，状态码: {response.status_code}")