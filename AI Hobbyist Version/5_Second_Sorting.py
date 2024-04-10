import json, os, argparse
from tqdm import tqdm
from pathlib import Path
from glob import glob
from shutil import move

parser = argparse.ArgumentParser()
parser.add_argument('-src','--source', type=str, help='待分类数据集目录', required=True)
parser.add_argument('-dst','--destination', type=str, help='目标目录', required=True)
args = parser.parse_args()

source = str(args.source)
dest = str(args.destination)

index = Path("./Data/Sorted.json").read_text(encoding="utf-8")
lab_src = glob(f"{source}/**/*.lab",recursive=True)
data = json.loads(index)

for lab_file in tqdm(lab_src):
    try:
        src_dir = os.path.dirname(lab_file)
        lab_file_name = os.path.basename(lab_file)
        wav_file_name = lab_file_name.replace(".lab",".wav")
        dst_dir = data[lab_file_name]
        if not os.path.exists(f"{dest}/{dst_dir}"):
            Path(f"{dest}/{dst_dir}").mkdir(parents=True)
        move(f"{src_dir}/{lab_file_name}",f"{dest}/{dst_dir}/{lab_file_name}")
        move(f"{src_dir}/{wav_file_name}",f"{dest}/{dst_dir}/{wav_file_name}")
    except:
        pass