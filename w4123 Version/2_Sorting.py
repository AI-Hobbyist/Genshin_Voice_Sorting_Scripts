import json
import os
import re
import argparse
import tqdm as tq
from shutil import copy

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, help='未整理数据集目录', required=True)
parser.add_argument('--index', type=str, help='索引路径', required=True)
parser.add_argument('--dest', type=str, help='目标路径', required=True)
parser.add_argument('--lang', type=str, help='语言(可选CHS/JP/EN/KR，默认CHS)', default='CHS')
args = parser.parse_args()

source = str(args.source)
dest = str(args.dest)
index = str(args.index)
lang = str(args.lang)
filter = 'fetter|battle|life|monster'

renameDict = {
    '万叶': '枫原万叶',
    "#{REALNAME[ID(1)|HOSTONLY(true)]}": '流浪者',
    '影': '雷电将军',
    '公子': '达达利亚',
    '散兵': '流浪者',
    '幽夜菲谢尔': '菲谢尔',
    '绿色的家伙': '温迪',
}

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

def has_vaild_content(text):
    pattern = r'[a-zA-Z0-9\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]+'
    if re.search(pattern, text):
        return True
    else:
        return False
    
f = open(index, encoding='utf8')
data = json.load(f)
for k in tq.tqdm(data.keys()):
    try:
        text = data.get(k).get('text')
        char_name = data.get(k).get('npcName')
        path = data.get(k).get('fileName')
        o_lang = data.get(k).get('language')
        if o_lang != lang:
            continue
        path = path.replace(".wem",".wav")
        wav_source = source + '/' + path
        wav_file = os.path.basename(path)
        if has_vaild_content(text) == True and char_name is not None:
            dest_dir = dest + '/' + char_name
            wav_path = dest_dir + '/' + wav_file
            if is_in(path, filter) == False and is_file(wav_source) == True:
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                copy(wav_source, wav_path)
    except:
        pass
f.close()