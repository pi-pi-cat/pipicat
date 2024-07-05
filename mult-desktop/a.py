import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pyautogui
import math


def get_desktop_size():
    """获取桌面大小"""
    return pyautogui.size()


def calculate_layout(desktop_width, desktop_height, num_browsers):
    """计算浏览器窗口的布局"""
    # 计算行数和列数
    num_cols = math.ceil(math.sqrt(num_browsers))
    num_rows = math.ceil(num_browsers / num_cols)

    # 计算每个窗口的大小
    window_width = desktop_width // num_cols
    window_height = desktop_height // num_rows

    # 计算每个窗口的位置
    configs = []
    for i in range(num_browsers):
        row = i // num_cols
        col = i % num_cols
        x = col * window_width
        y = row * window_height
        configs.append({"position": (x, y), "size": (window_width, window_height)})

    return configs


def open_browser(url, position, size):
    """打开浏览器并设置位置和大小"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service("./chromedriver.exe")  # 替换为您的ChromeDriver路径
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    time.sleep(2)  # 等待页面加载
    driver.set_window_position(position[0], position[1])
    driver.set_window_size(size[0], size[1])
    return driver


def main(num_browsers, desktop_size=None):
    if desktop_size is None:
        desktop_size = get_desktop_size()

    desktop_width, desktop_height = desktop_size
    configs = calculate_layout(desktop_width, desktop_height, num_browsers)

    drivers = []
    for i, config in enumerate(configs):
        url = f"https://www.baidu.com"  # 每个浏览器打开不同的URL
        driver = open_browser(url, config["position"], config["size"])
        drivers.append(driver)


if __name__ == "__main__":
    # 示例用法
    num_browsers = 12  # 指定要打开的浏览器数量
    # desktop_size = (1920, 1080)  # 可选：指定桌面大小，如果不指定则自动获取
    main(
        num_browsers
    )  # 如果要指定桌面大小，可以这样调用：main(num_browsers, desktop_size)
