```
#!/bin/bash

# 设置变量
SCRIPT_PATH="/path/to/run.sh"
CONFIG_PATH="/path/to/config.py"
NEW_MODEL_NAME="SSTA_xx"

# 1. 创建run.sh脚本
cat > $SCRIPT_PATH << 'EOF'
#!/bin/bash
# 这里放入run.sh的内容
echo "This is the content of run.sh"
# 添加更多命令...
EOF

# 2. 修改config.py文件
sed -i "s/model_name = .*/model_name = '$NEW_MODEL_NAME'/" $CONFIG_PATH

# 3. 给run.sh添加执行权限
chmod +x $SCRIPT_PATH

echo "All operations completed successfully."

```




#!/bin/bash

# 创建一个示例文件
cat > sample.txt << EOF
1. This is the first line.
2. This line contains old text to replace.
3. We will delete this entire line.
4. This line has multiple occurrences of 'the'.
5. This is the fifth line.
6. We will insert new content after this line.
7. This line will be partially modified.
8. [START] This content is within brackets [END]
9. We will change the numbering of this line.
10. This is the last line of the original content.
EOF

echo "Original file contents:"
cat sample.txt
echo "------------------------------"

# 1. 基本替换：替换第一次出现的文本
sed 's/old text/new text/' sample.txt > result.txt

# 2. 全局替换：替换所有出现的文本
sed 's/the/THE/g' result.txt > temp.txt && mv temp.txt result.txt

# 3. 特定行替换：只在第2行进行替换
sed '2s/old/new/' result.txt > temp.txt && mv temp.txt result.txt

# 4. 删除整行：删除包含特定文本的行
sed '/delete this entire line/d' result.txt > temp.txt && mv temp.txt result.txt

# 5. 在特定行后插入新行
sed '/insert new content after this line/a\This is a newly inserted line.' result.txt > temp.txt && mv temp.txt result.txt

# 6. 在特定行前插入新行
sed '/This is the last line/i\This line is inserted before the last line.' result.txt > temp.txt && mv temp.txt result.txt

# 7. 部分行修改：只修改行的一部分
sed 's/partially modified/PARTIALLY CHANGED/' result.txt > temp.txt && mv temp.txt result.txt

# 8. 使用正则表达式：替换括号内的内容
sed 's/\[START\].*\[END\]/[START] New content within brackets [END]/' result.txt > temp.txt && mv temp.txt result.txt

# 9. 修改行号：将"9."改为"09."
sed 's/^9\./09./' result.txt > temp.txt && mv temp.txt result.txt

# 10. 在文件开头添加内容
sed '1i\This line is added at the beginning of the file.' result.txt > temp.txt && mv temp.txt result.txt

# 11. 在文件末尾添加内容
sed '$a\This line is added at the end of the file.' result.txt > temp.txt && mv temp.txt result.txt

# 12. 打印特定行范围
echo "Lines 3-5 of the modified file:"
sed -n '3,5p' result.txt

# 13. 多个命令组合：替换文本并删除下一行
sed -e 's/fifth/5th/' -e '/5th/N;/5th.*insert/d' result.txt > temp.txt && mv temp.txt result.txt

# 14. 使用地址范围：只在特定行范围内进行替换
sed '3,6s/This/That/' result.txt > temp.txt && mv temp.txt result.txt

# 15. 条件替换：只有当行包含某个模式时才进行替换
sed '/multiple/s/occurrences/instances/' result.txt > temp.txt && mv temp.txt result.txt

# 16. 使用&引用匹配的文本
sed 's/line [0-9]/&, numbered line/' result.txt > temp.txt && mv temp.txt result.txt

# 17. 使用转换命令：将小写转换为大写
sed 'y/abcdefghijklmnopqrstuvwxyz/ABCDEFGHIJKLMNOPQRSTUVWXYZ/' result.txt > temp.txt && mv temp.txt result.txt

echo "File contents after sed operations:"
cat result.txt
echo "------------------------------"

# 清理临时文件
rm sample.txt result.txt
