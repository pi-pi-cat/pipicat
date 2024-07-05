import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pyautogui

# 步骤1: 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # 启动时最大化窗口

# 步骤2: 设置ChromeDriver路径
service = Service("/path/to/chromedriver")  # 替换为您的ChromeDriver路径

# 步骤3: 初始化WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# 步骤4: 打开网页
driver.get("https://www.example.com")  # 替换为您要访问的网站

# 步骤5: 等待页面加载
time.sleep(5)  # 等待5秒,确保页面完全加载

# 步骤6: 找到输入框并输入数据
try:
    input_field = driver.find_element(By.NAME, "q")  # 替换"q"为实际的输入框名称
    input_field.send_keys("Your search query")
    input_field.send_keys(Keys.RETURN)
except Exception as e:
    print(f"无法找到或操作输入框: {e}")

# 步骤7: 等待搜索结果加载
time.sleep(3)

# 步骤8: 点击按钮 (如果需要)
try:
    button = driver.find_element(By.ID, "button_id")  # 替换"button_id"为实际的按钮ID
    button.click()
except Exception as e:
    print(f"无法找到或点击按钮: {e}")

# 步骤9: 移动窗口到指定位置
pyautogui.moveTo(100, 100)  # 移动鼠标到屏幕坐标(100, 100)
pyautogui.mouseDown()
pyautogui.moveTo(300, 300, duration=1)  # 将窗口拖动到(300, 300)
pyautogui.mouseUp()

# 步骤10: 调整窗口大小
driver.set_window_size(800, 600)

# 步骤11: 保持浏览器窗口打开
input("按Enter键退出...")

# 步骤12: 关闭浏览器
driver.quit()
