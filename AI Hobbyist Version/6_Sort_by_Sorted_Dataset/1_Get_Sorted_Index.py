import os
import json
import argparse
from tqdm import tqdm
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('-src','--source', type=str, help='数据集目录', required=True)
args = parser.parse_args()

source = str(args.source)

def generate_directory_index(directory_path):
    index = {}
    lab_src = glob(f"{directory_path}/**/*.lab")
    for labfilename in tqdm(lab_src):
        lab_file = os.path.basename(labfilename)
        index[lab_file] = os.path.basename(os.path.dirname(labfilename))
    return index

json_index = generate_directory_index(source)

with open("file_index.json", "w", encoding="utf-8") as json_file:
    json.dump(json_index, json_file, ensure_ascii=False, indent=4, )

print("JSON索引已生成并保存到file_index.json文件中。")