import json
import os
import re
import argparse
import tqdm as tq
from shutil import copy, move
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, help='未整理数据集目录', required=True)
parser.add_argument('--index', type=str, help='索引路径', required=True)
parser.add_argument('--dest', type=str, help='目标路径', required=True)
parser.add_argument('--lang', type=str, help='语言（可选CHS/EN/JP/KR，默认为CHS）', default="CHS")
parser.add_argument('--mode', type=str, help='模式(复制(cp)/移动(mv))', default="cp")
args = parser.parse_args()

source = str(args.source)
dest = str(args.dest)
index = str(args.index)
lang = str(args.lang)
mode = str(args.mode)
filter = 'monster'
battle = 'battle|life'
conv = 'fetter'
player = '旅行者|旅人|Traveler|여행자'

renameDict = {
    '万叶': '枫原万叶',
    "#{REALNAME[ID(1)|HOSTONLY(true)]}": '流浪者',
    '影': '雷电将军',
    '「公子」': '达达利亚',
    '公子': '达达利亚',
    '散兵': '流浪者',
    '「散兵」': '流浪者',
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
def ren_player(player,lang):
    p_name = player
    if p_name == "PlayerBoy" or p_name == "PlayerGirl":
        if p_name == "PlayerBoy":
            if lang == "CHS":
                p_name = "空"
            if lang == "EN":
                p_name = "Aether"
            if lang == "JP":
                p_name = "空"
            if lang == "KR":
                p_name = "아이테르"
        if p_name == "PlayerGirl":
            if lang == "CHS":
                p_name = "荧"
            if lang == "EN":
                p_name = "Lumine"
            if lang == "JP":
                p_name = "蛍"
            if lang == "KR":
                p_name = "루미네"
    else:
        p_name = player
    return p_name
    
f = open(index, encoding='utf8')
data = json.load(f)
for k in tq.tqdm(data.keys()):
    try:
        text = data.get(k).get('voiceContent')
        char_name = data.get(k).get('talkName')
        avatar_name = data.get(k).get('avatarName')
        if char_name is not None:
            if char_name in renameDict:
                char_name = renameDict[char_name]
            if is_in(char_name, player) == True:
                char_name = ren_player(avatar_name,lang)p
        path = data.get(k).get('sourceFileName')
        path = path.replace(".wem",".wav")
        wav_source = source + '/' + path
        wav_file = os.path.basename(path)
        if has_vaild_content(text) == True and char_name is not None:
            vo_dest_dir = f"{dest}/角色语音 - Character/{char_name}"
            bt_dest_dir = f"{dest}/战斗语音 - Battle/{char_name}"
            cv_dest_dir = f"{dest}/多人对话 - Conversation/{char_name}"
            vo_wav_path = f"{vo_dest_dir}/{wav_file}"
            bt_wav_path = f"{bt_dest_dir}/{wav_file}"
            cv_wav_path = f"{cv_dest_dir}/{wav_file}"
            if is_in(path, filter) == False and is_file(wav_source) == True:
                if is_in(path, battle) == True:
                    if not os.path.exists(bt_dest_dir):
                       Path(f"{bt_dest_dir}").mkdir(parents=True)
                    dest_path = bt_wav_path
                elif is_in(path, conv) == True:
                    if not os.path.exists(cv_dest_dir):
                       Path(f"{cv_dest_dir}").mkdir(parents=True)
                    dest_path = cv_wav_path
                else:
                    if not os.path.exists(vo_dest_dir):
                       Path(f"{vo_dest_dir}").mkdir(parents=True)
                    dest_path = vo_wav_path
                if mode.capitalize()=='CP':
                    copy(wav_source,dest_path)
                elif mode.capitalize()=='MV':
                    move(wav_source,dest_path)
                else:
                    print("模式错误，请选择cp/mv")
                    exit()
    except:
        pass
f.close()