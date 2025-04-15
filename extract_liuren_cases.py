import os
import re

OVERWRITE = True
# 定义输入和输出目录
input_file = os.path.join(os.path.dirname(__file__), 'books', '六壬存验-清-吴师青.txt')
output_dir = os.path.join(os.path.dirname(__file__), 'cases')

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 定义写入文件的函数
def write_to_file(file_path, content):
    """
    将内容写入文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
    """
    if os.path.exists(file_path) and not OVERWRITE:
        # 如果文件存在且不覆盖，则追加内容
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('\n------------------------------\n' + content)
    else:
        # 如果文件不存在或需要覆盖，则创建新文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

# 尝试不同的编码方式读取文件
encodings = ['utf-8-sig', 'utf-16', 'gb18030', 'gbk', 'big5']
content = None

for encoding in encodings:
    try:
        with open(input_file, 'r', encoding=encoding) as f:
            content = f.read()
            print(f"成功使用 {encoding} 编码读取文件")
            break
    except UnicodeDecodeError:
        print(f"使用 {encoding} 编码读取失败，尝试下一种编码")
        continue

if content is None:
    print("无法读取文件，请检查文件编码")
    exit(1)

# 提取所有课例
cases = []
case_content = ''
in_case = False
start_line = ''

# 更宽松的正则表达式，用于匹配课例开始
case_start_regex = r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])[年]?.*?月.*?([子丑寅卯辰巳午未申酉戌亥])将，([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])日([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])时'

# 逐行处理文本，识别课例
lines = content.split('\n')
i = 0
while i < len(lines):
    line = lines[i]
    
    # 检查是否是新课例的开始
    case_start_match = re.search(case_start_regex, line)
    
    if case_start_match:
        # 如果已经在处理一个课例，保存之前的课例
        if in_case and case_content.strip():
            cases.append({
                'content': case_content.strip(),
                'start_line': start_line
            })
        
        # 开始新的课例
        in_case = True
        case_content = line + '\n'
        start_line = line
    elif in_case:
        # 检查是否是课例结束
        # 如果当前行包含"断："或"断曰："，并且后面几行是空行或新课例开始，则结束当前课例
        if ('断：' in line or '断曰：' in line) and i + 1 < len(lines):
            case_content += line + '\n'
            
            # 向后查找几行，看是否有空行或新课例开始
            j = i + 1
            end_found = False
            while j < len(lines) and j < i + 10:
                if lines[j].strip() == '' or re.search(case_start_regex, lines[j]):
                    end_found = True
                    break
                case_content += lines[j] + '\n'
                j += 1
            
            if end_found:
                cases.append({
                    'content': case_content.strip(),
                    'start_line': start_line
                })
                in_case = False
                case_content = ''
                i = j - 1  # 跳过已处理的行
                i += 1
                continue
        
        # 如果当前行是空行，且下一行可能是新课例的开始，则结束当前课例
        if line.strip() == '' and i + 1 < len(lines) and re.search(case_start_regex, lines[i + 1]):
            cases.append({
                'content': case_content.strip(),
                'start_line': start_line
            })
            in_case = False
            case_content = ''
        else:
            case_content += line + '\n'
    
    i += 1

# 添加最后一个课例
if in_case and case_content.strip():
    cases.append({
        'content': case_content.strip(),
        'start_line': start_line
    })

print(f'共提取到 {len(cases)} 个课例')

# 处理每个课例，提取信息并分类
for index, case_item in enumerate(cases):
    case_text = case_item['content']
    start_line = case_item['start_line']
    
    # 提取日柱、时柱和月将信息
    info_match = re.search(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])日([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])时.*?([子丑寅卯辰巳午未申酉戌亥])将', start_line)
    
    if info_match:
        day_pillar = info_match.group(1)
        time_pillar = info_match.group(2)
        month_general = info_match.group(3)
        
        # 创建文件名
        file_name = f"{day_pillar}日{time_pillar[1]}时{month_general}将.txt"
        file_path = os.path.join(output_dir, file_name)
        
        # 使用函数写入文件
        write_to_file(file_path, case_text)
        
        print(f'课例 {index + 1} 已写入 {file_name}')
    else:
        # 尝试另一种匹配方式
        alt_match = re.search(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])日([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])时', start_line)
        
        if alt_match:
            day_pillar = alt_match.group(1)
            time_pillar = alt_match.group(2)
            
            # 尝试从开始行提取月将
            month_general_match = re.search(r'([子丑寅卯辰巳午未申酉戌亥])将', start_line)
            month_general = month_general_match.group(1) if month_general_match else '未知'
            
            # 创建文件名
            file_name = f"{day_pillar}日{time_pillar[1]}时{month_general}将.txt"
            file_path = os.path.join(output_dir, file_name)
            
            # 使用函数写入文件
            write_to_file(file_path, case_text)
            
            print(f'课例 {index + 1} 已写入 {file_name}')
        else:
            # 无法识别的课例写入unknown.txt
            unknown_path = os.path.join(output_dir, 'unknown.txt')
            
            # 使用函数写入文件
            write_to_file(unknown_path, case_text)
            
            print(f'课例 {index + 1} 无法识别，已写入 unknown.txt')

# 输出一些示例课例，帮助调试
if len(cases) > 0:
    print('\n示例课例:')
    print(cases[0]['start_line'])
    if len(cases) > 1:
        print(cases[1]['start_line'])

print('处理完成！')