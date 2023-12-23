import os
import re
import shutil
import sys

def add_space_between_english_and_chinese(text):
    # 匹配英文单词、数字、或连续的英文标识与中文之间的位置，但不包括在方括号中的内容
    pattern = re.compile(r'(?<=[a-zA-Z0-9\-\_\/\]\)])\s*(?=[\u4e00-\u9fa5])|(?<=[\u4e00-\u9fa5])\s*(?=[a-zA-Z0-9\-\_\/\[])')

    # 忽略代码块和方括号中的内容
    in_code_block = False
    lines = text.split('\n')
    for i in range(len(lines)):
        line = lines[i]
        if '```' in line:
            in_code_block = not in_code_block
        if in_code_block:
            continue
        lines[i] = pattern.sub(' ', line)

    return '\n'.join(lines)

def process_file(file_path):
    # 读取原始文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        original_content = file.read()

    # 添加空格
    modified_content = add_space_between_english_and_chinese(original_content)

    # 检查是否需要备份
    with open(file_path, 'r', encoding='utf-8') as file:
        existing_content = file.read()
    if existing_content != modified_content:
        # 备份原始文件
        backup_path = file_path + '.bak'
        shutil.copyfile(file_path, backup_path)

        # 将修改后的内容写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        # 输出日志
        print(f"已修改文件: {file_path}")
    else:
        print(f"未修改文件: {file_path}")

def process_directory(directory_path):
    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                process_file(file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("请提供目录或文件路径作为参数。")
        sys.exit(1)

    target_path = sys.argv[1]

    if os.path.isdir(target_path):
        process_directory(target_path)
    elif os.path.isfile(target_path) and target_path.endswith('.md'):
        process_file(target_path)
    else:
        print("无效的目录或文件路径，请输入有效的目录或Markdown文件。")
