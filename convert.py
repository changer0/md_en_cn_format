import os
import re
import shutil
import sys

def process_markdown(text):
    # 用于匹配代码块的正则表达式
    code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
    # 用于匹配最外层中括号内容的正则表达式
    bracket_content_pattern = re.compile(r'\[(?:[^\[\]]+|\[(?:[^\[\]]+|\[.*?\])*\])*\]')
    # 用于匹配最外层小括号内容的正则表达式
    parenthesis_content_pattern = re.compile(r'\((?:[^\(\)]+|\((?:[^\(\)]+|\(.*?\))*\))*\)')

    # 保存处理后的文本块
    processed_blocks = []
    # 上次搜索结束的位置
    last_end = 0

    # 找到所有代码块
    for match in code_block_pattern.finditer(text):
        # 获取代码块前的文本
        block_before_code = text[last_end:match.start()]
        # 处理代码块前的文本
        processed_block = process_non_code_block(block_before_code, bracket_content_pattern, parenthesis_content_pattern)
        # 添加处理后的文本到结果列表
        processed_blocks.append(processed_block)
        # 添加代码块到结果列表（代码块不做处理）
        processed_blocks.append(match.group())
        # 更新上一次搜索结束的位置
        last_end = match.end()

    # 处理最后一个代码块后的文本
    remaining_text = text[last_end:]
    processed_block = process_non_code_block(remaining_text, bracket_content_pattern, parenthesis_content_pattern)
    processed_blocks.append(processed_block)

    # 将所有处理后的文本块合并
    return ''.join(processed_blocks)

def process_non_code_block(text, bracket_content_pattern, parenthesis_content_pattern):
    # 处理中括号内的内容，暂时替换为占位符
    bracket_placeholders = []
    def replace_bracket_with_placeholder(match):
        bracket_placeholders.append(match.group())
        return f'BRACKET_PLACEHOLDER_{len(bracket_placeholders) - 1}'

    text = bracket_content_pattern.sub(replace_bracket_with_placeholder, text)

    # 处理小括号内的内容，暂时替换为占位符
    parenthesis_placeholders = []
    def replace_parenthesis_with_placeholder(match):
        parenthesis_placeholders.append(match.group())
        return f'PARENTHESIS_PLACEHOLDER_{len(parenthesis_placeholders) - 1}'

    text = parenthesis_content_pattern.sub(replace_parenthesis_with_placeholder, text)

    # 在英文单词与中文之间添加空格
    text = re.sub(r'([a-zA-Z])([\u4e00-\u9fff])', r'\1 \2', text)
    text = re.sub(r'([\u4e00-\u9fff])([a-zA-Z])', r'\1 \2', text)

    # 还原中括号内的内容
    for i, placeholder in enumerate(bracket_placeholders):
        text = text.replace(f'BRACKET_PLACEHOLDER_{i}', placeholder)

    # 还原小括号内的内容
    for i, placeholder in enumerate(parenthesis_placeholders):
        text = text.replace(f'PARENTHESIS_PLACEHOLDER_{i}', placeholder)

    return text

def backup_file(file_path):
    # 备份原始文件
    backup_path = file_path + '.bak'
    shutil.copyfile(file_path, backup_path)

def process_file(file_path):
    # 读取原始文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        original_content = file.read()

    # 添加空格
    modified_content = process_markdown(original_content)

    # 检查是否需要备份
    with open(file_path, 'r', encoding='utf-8') as file:
        existing_content = file.read()
    if existing_content != modified_content:
        # 备份原始文件
        backup_file(file_path)

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
