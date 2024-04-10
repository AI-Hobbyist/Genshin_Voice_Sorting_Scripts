import re, os, argparse
from tqdm import tqdm
from pathlib import Path
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('-src','--source', type=str, help='数据集目录', required=True)
args = parser.parse_args()

source = str(args.source)
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

for file in tqdm(labfiles):
    try:
        lab_content = Path(file).read_text(encoding='utf-8')
        spk = os.path.basename(os.path.dirname(file))
        lab_file_name = os.path.basename(file)
        wav_file_name = lab_file_name.replace(".lab",".wav")
        src = f"{source}/{spk}"
        if check_content(lab_content,tags):
            labels = re.sub(r'<.*?>', '', lab_content)
            lab_path = f"{src}/{lab_file_name}"
            Path(lab_path).write_text(labels,encoding='utf-8')
            tqdm.write(f"已清除标注文件 {src}/{lab_file_name} 中的html标签：{tag_content(lab_content)}\n-----------")
    except:
        pass