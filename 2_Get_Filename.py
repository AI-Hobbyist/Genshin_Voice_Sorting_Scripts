import json
import glob
import argparse
import os
import tqdm as tq
from shutil import move

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, help='未整理数据集目录', required=True)
parser.add_argument('--index', type=str, help='索引路径', required=True)
parser.add_argument('--dest', type=str, help='目标路径', required=True)
args = parser.parse_args()

source = str(args.source)
index = str(args.index)
dest = str(args.dest)

files = glob.glob(os.path.join(source, "*.wav"))
f = open(index, encoding='utf-8')
data = json.load(f)
for wav in tq.tqdm(files):
    file = str(wav).replace(".wav", "")
    file_hash = os.path.basename(file)
    try:
        path = data.get(file_hash).get('sourceFileName')
        wav_path = source + "/" + os.path.dirname(path)
        dest_file = dest + '/' + path
        dest_file = dest_file.replace(".wem",".wav")
        dis_dir = os.path.dirname(dest_file)
        if not os.path.exists(dis_dir):
            os.makedirs(dis_dir)
        move(wav, dest_file)
    except Exception as e:
        pass