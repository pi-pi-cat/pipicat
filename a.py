import os
import re
import requests
from bs4 import BeautifulSoup
from lxml import html
from urllib.parse import urljoin


# 设置前缀目录
prefix_dir = "/Users/yxf/Documents/test"


# 函数用于下载文件
def download_file(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Downloaded: {save_path}")
    else:
        print(f"Failed to download: {url}")


for filename in os.listdir(prefix_dir):
    if filename.endswith(".whl"):
        # 从文件名中提取名称和版本号
        match = re.match(r"([\w-]+)-([\d\.]+)-.+\.whl", filename)
        if match:
            name, version = match.groups()
            name = name.replace("_", "-")

            try:
                # 构建PyPI网页URL
                pypi_url = f"https://pypi.org/project/{name}/{version}/#files"

                # 从PyPI网页中解析源代码下载链接
                response = requests.get(pypi_url)
                tree = html.fromstring(response.content)
                source_link = tree.xpath('//*[@id="files"]/div[1]/div[2]/a[1]/@href')
                if source_link:
                    source_url = source_link[0]
                    # 下载源代码
                    source_dir = os.path.join(prefix_dir, "conda", name, "source")
                    os.makedirs(source_dir, exist_ok=True)
                    source_filename = os.path.basename(source_url)
                    source_path = os.path.join(source_dir, source_filename)
                    download_file(source_url, source_path)
                    print(f"下载源代码 {name} 成功")
            except Exception as e:
                pass

            try:
                # 下载meta.yaml
                recipe_dir = os.path.join(prefix_dir, "conda", name, "conda.recipe")
                os.makedirs(recipe_dir, exist_ok=True)
                feedstock_url = f"https://raw.githubusercontent.com/conda-forge/{name}-feedstock/main/recipe/meta.yaml"
                recipe_path = os.path.join(recipe_dir, "meta.yaml")
                download_file(feedstock_url, recipe_path)
                print(f"下载meta.yaml {name} 成功")
            except Exception as e:
                pass
