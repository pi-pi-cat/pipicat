import cv2
import numpy as np
import matplotlib.pyplot as plt

def preprocess_region(image, region, operations=None):
    # 您原有的 preprocess_region 函数代码保持不变
    # ...

def detect_and_segment_lines(processed_image, min_line_height=5, min_line_gap=5):
    # 确保图像是二值化的
    if len(processed_image.shape) == 3:
        processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(processed_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 计算水平投影
    h_proj = np.sum(binary, axis=1)
    
    # 找到行的起始和结束位置
    h, w = binary.shape
    line_positions = []
    start = None
    
    for i in range(h):
        if h_proj[i] > 0 and start is None:
            start = i
        elif h_proj[i] == 0 and start is not None:
            if i - start >= min_line_height:
                line_positions.append((start, i))
            start = None
        elif i == h - 1 and start is not None:
            line_positions.append((start, i))
    
    # 合并太近的行
    merged_line_positions = []
    for i, (start, end) in enumerate(line_positions):
        if i == 0 or start - merged_line_positions[-1][1] >= min_line_gap:
            merged_line_positions.append((start, end))
        else:
            merged_line_positions[-1] = (merged_line_positions[-1][0], end)
    
    # 分割行
    line_images = []
    for start, end in merged_line_positions:
        line_image = processed_image[start:end, :]
        line_images.append(line_image)
    
    return line_images, merged_line_positions

def visualize_lines(image, line_positions):
    visual_image = image.copy()
    if len(visual_image.shape) == 2:
        visual_image = cv2.cvtColor(visual_image, cv2.COLOR_GRAY2BGR)
    
    for start, end in line_positions:
        cv2.line(visual_image, (0, start), (image.shape[1], start), (0, 255, 0), 2)
        cv2.line(visual_image, (0, end), (image.shape[1], end), (0, 0, 255), 2)
    
    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(visual_image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

# 主程序
image = cv2.imread('2.png')

# 定义要提取的区域 (x, y, width, height)
region = (600, 100, 300, 500)

# 定义预处理操作
operations = ['grayscale', 'binary', 'denoise', 'sharpen', "super_resolution"]

# 处理图像
processed_roi = preprocess_region(image, region, operations)

# 显示预处理后的图像
plt.figure(figsize=(10, 10))
plt.imshow(processed_roi, cmap='gray')
plt.title("Preprocessed Image")
plt.axis('off')
plt.show()

# 检测和分割行
line_images, line_positions = detect_and_segment_lines(processed_roi, min_line_height=10, min_line_gap=5)

print(f"检测到 {len(line_images)} 行")

# 可视化检测结果
visualize_lines(processed_roi, line_positions)

# 显示分割后的每一行
for i, line_image in enumerate(line_images):
    plt.figure(figsize=(10, 2))
    plt.imshow(line_image, cmap='gray')
    plt.title(f"Line {i+1}")
    plt.axis('off')
    plt.show()

# 保存处理后的整个区域图像
cv2.imwrite('processed_region.jpg', processed_roi)

# 保存每一行的图像
for i, line_image in enumerate(line_images):
    cv2.imwrite(f'line_{i+1}.jpg', line_image)

# 打印水平投影
plt.figure(figsize=(10, 5))
plt.plot(np.sum(processed_roi, axis=1))
plt.title("Horizontal Projection")
plt.xlabel("Row")
plt.ylabel("Pixel Sum")
plt.show()