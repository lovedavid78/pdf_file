from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# 设置 WebDriver 的路径
driver_path = '/path/to/chromedriver'
driver = webdriver.Chrome('chrome-mac-arm64/')

# 打开目标网站的登录页面
driver.get('https://www.taobao.com')

# 查找用户名和密码输入框，填写登录信息
username_input = driver.find_element_by_name('username')
password_input = driver.find_element_by_name('password')

username_input.send_keys('your_username')
password_input.send_keys('your_password')

# 提交表单登录
password_input.send_keys(Keys.RETURN)

# 等待页面加载完成
time.sleep(5)

# 抓取登录后页面的数据
dashboard_url = 'https://example.com/dashboard'
driver.get(dashboard_url)

# 抓取页面内容
page_content = driver.page_source
print(page_content)

# 关闭浏览器
driver.quit()