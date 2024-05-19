import re, os, argparse
from tqdm import tqdm
from pathlib import Path
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('-src','--source', type=str, help='数据集目录', default="./Data/second_sorted")
parser.add_argument('-lang','--language', type=str, help='语言（可选CHS/EN/JP/KR）', required=True)
args = parser.parse_args()

source = str(args.source)
language = str(args.language)
tags = r'[<>]'

labfiles = glob(f"{source}/**/*.lab",recursive=True)
    
def check_content(text, regx):
    if re.search(regx, text):
        return True
    else:
        return False
    
def tag_content(text):
    res = re.findall(r'(<.*?>)', text)
    string = '、'.join(res)
    return string

def get_path_by_lang(lang):
    langcodes = ["CHS","EN","JP","KR"]
    path = ['中文 - Chinese', '英语 - English',  '日语 - Japanese', '韩语 - Korean']
    try:
        i = langcodes.index(lang)
        dest_path = path[i]
    except:
        print("不支持的语言")
        exit()
    return dest_path

path_by_lang = get_path_by_lang(language);

for file in tqdm(labfiles):
    try:
        lab_content = Path(file).read_text(encoding='utf-8')
        spk = os.path.basename(os.path.dirname(file))
        lab_file_name = os.path.basename(file)
        wav_file_name = lab_file_name.replace(".lab",".wav")
        src = f"{source}/{path_by_lang}/{spk}"
        if check_content(lab_content,tags):
            labels = re.sub(r'<.*?>', '', lab_content)
            lab_path = f"{src}/{lab_file_name}"
            Path(lab_path).write_text(labels,encoding='utf-8')
            tqdm.write(f"已清除标注文件 {src}/{lab_file_name} 中的html标签：{tag_content(lab_content)}\n-----------")
    except:
        pass