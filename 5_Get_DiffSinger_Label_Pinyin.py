import json
import re
import os
import argparse
import tqdm as tq
from pathlib import Path
from pypinyin import lazy_pinyin, load_phrases_dict

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, help='未整理数据集目录', required=True)
parser.add_argument('--index', type=str, help='索引路径', required=True)
parser.add_argument('--dest', type=str, help='目标路径', required=True)
args = parser.parse_args()

source = str(args.source)
dest = str(args.dest)
index = str(args.index)
filter = 'fetter|battle|life|monster'

personalized_dict = {
    '嗯': [['en']],
    '八重': [['ba'], ['chong']],
    '重云': [['chong'], ['yun']]
}

renameDict = {
    '万叶': '枫原万叶',
    "#{REALNAME[ID(1)|HOSTONLY(true)]}": '流浪者',
    '影': '雷电将军',
    '公子': '达达利亚',
    '散兵': '流浪者',
    '幽夜菲谢尔': '菲谢尔',
    '绿色的家伙': '温迪',
}

load_phrases_dict(personalized_dict)

def is_in(full_path, regx):
    if re.findall(regx, full_path):
        return True
    else:
        return False

def is_file(full_path):
    if os.path.exists(full_path):
        return True
    else:
        return  False

f = open(index, encoding='utf8')
data = json.load(f)
for k in tq.tqdm(data.keys()):
    try:
        text = data.get(k).get('voiceContent')
        pinyin = " ".join(lazy_pinyin(text, errors='ignore'))
        char_name = data.get(k).get('talkName')
        avatar_name = data.get(k).get('avatarName')
        if char_name is not None:
            if char_name in renameDict:
                char_name = renameDict[char_name]
            if char_name == "旅行者" :
                char_name = avatar_name
        path = data.get(k).get('sourceFileName')
        path = path.replace(".wem",".wav")
        wav_source = source + '/' + path
        wav_file = os.path.basename(path)
        if pinyin is not None and char_name is not None:
            dest_dir = dest + '/' + char_name
            lab_path = dest_dir + '/' + wav_file
            lab_path = lab_path.replace(".wav",".lab")
            if pinyin is not None and is_in(path, filter) == False and is_file(wav_source) == True:
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                Path(lab_path).write_text(pinyin, encoding='utf-8')
    except:
        pass
f.close()
