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

index = Path("./file_index.json").read_text(encoding="utf-8")
lab_src = glob(f"{source}/**/*.lab")
data = json.loads(index)

for lab_file in tqdm(lab_src):
    try:
        src_dir = os.path.dirname(lab_file)
        lab_file_name = os.path.basename(lab_file)
        wav_file_name = lab_file_name.replace(".lab",".wav")
        speaker = data[lab_file_name]
        if not os.path.exists(f"{dest}/{speaker}"):
            Path(f"{dest}/{speaker}").mkdir(parents=True)
        move(f"{src_dir}/{lab_file_name}",f"{dest}/{speaker}/{lab_file_name}")
        move(f"{src_dir}/{wav_file_name}",f"{dest}/{speaker}/{wav_file_name}")
    except:
        tqdm.write(f"提示：无法找到文件名 {lab_file_name} 对应的说话人，如果最终数量不多，可无视")
        pass