import json, os, argparse
from tqdm import tqdm
from pathlib import Path
from glob import glob
from shutil import move

parser = argparse.ArgumentParser()
parser.add_argument('-src','--source', type=str, help='待分类数据集目录', default="./Data/sorted")
parser.add_argument('-dst','--destination', type=str, help='目标目录', default="./Data/second_sorted")
parser.add_argument('-lang','--language', type=str, help='语言（可选CHS/EN/JP/KR）', required=True)
args = parser.parse_args()

source = str(args.source)
dest = str(args.destination)
language = str(args.language).upper()

index = Path("./Data/Sorted.json").read_text(encoding="utf-8")
lab_src = glob(f"{source}/**/*.lab",recursive=True)
data = json.loads(index)

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

for lab_file in tqdm(lab_src):
    try:
        src_dir = os.path.dirname(lab_file)
        lab_file_name = os.path.basename(lab_file)
        wav_file_name = lab_file_name.replace(".lab",".wav")
        dst_dir = data[lab_file_name]
        if not os.path.exists(f"{dest}/{path_by_lang}/{dst_dir}"):
            Path(f"{dest}/{path_by_lang}/{dst_dir}").mkdir(parents=True)
        move(f"{src_dir}/{lab_file_name}",f"{dest}/{path_by_lang}/{dst_dir}/{lab_file_name}")
        move(f"{src_dir}/{wav_file_name}",f"{dest}/{path_by_lang}/{dst_dir}/{wav_file_name}")
    except:
        pass