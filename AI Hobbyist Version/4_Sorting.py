import json, re, os, argparse
from tqdm import tqdm
from pathlib import Path
from glob import glob
from shutil import copy, move
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, help='未整理数据集目录', required=True)
parser.add_argument('--ver', type=str, help='版本', required=True)
parser.add_argument('--dest', type=str, help='目标路径', required=True)
parser.add_argument('--lang', type=str, help='语言（可选CHS/EN/JP/KR）', required=True)
parser.add_argument('--mode', type=str, help='模式(复制(cp)/移动(mv))', default="cp")
args = parser.parse_args()

source = str(args.source)
dest = str(args.dest)
language = str(args.lang).upper()
ver = str(args.ver)
mode = str(args.mode)
monster = 'monster'
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

def get_support_ver():
    indexs = glob('./Indexs/*')
    support_vers = []
    for vers in indexs:
        version = os.path.basename(vers)
        support_vers.append(version)
    versions = '|'.join(support_vers)
    return versions

def get_support_lang(version):
    if is_in(version, get_support_ver()):
        support_langs = []
        indexs = glob(f'./Indexs/{version}/*')
        for langs in indexs:
            lang_code = os.path.basename(langs).replace("_output.json","").replace(".json","")
            support_langs.append(lang_code)
        return support_langs
    else:
        print("不支持的版本")
        exit()
    
def get_path_by_lang(lang):
    langcodes = get_support_lang(ver)
    path = ['中文 - Chinese', '英语 - English',  '日语 - Japanese', '韩语 - Korean']
    try:
        i = langcodes.index(lang)
        dest_path = path[i]
        lang_code = lang
    except:
        print("不支持的语言")
        exit()
    return lang_code, dest_path

langcode, dest_lang = get_path_by_lang(language)

def ren_player(player,lang):
    langcodes = get_support_lang(ver)
    player_boy_names = ['空', 'Aether', '空', '아이테르']
    player_girl_names = ['荧', 'Lumine', '蛍', '루미네']
    p_name = player
    if p_name == "PlayerBoy" or p_name == "PlayerGirl":
        if p_name == "PlayerBoy":
            i = langcodes.index(lang)
            p_name = player_boy_names[i]
        if p_name == "PlayerGirl":
            i = langcodes.index(lang)
            p_name = player_girl_names[i]
    else:
        p_name = player
    return p_name

f = open(f'./Indexs/{ver}/{langcode}.json', encoding='utf8')
data = json.load(f)
for k in tqdm(data.keys()):
    try:
        text = data.get(k).get('voiceContent')
        char_name = data.get(k).get('talkName')
        avatar_name = data.get(k).get('avatarName')
        if char_name is not None:
            if char_name in renameDict:
                char_name = renameDict[char_name]
            if is_in(char_name, player) == True:
                char_name = ren_player(avatar_name,langcode)
        path = data.get(k).get('sourceFileName')
        path = path.replace(".wem",".wav")
        wav_source = source + '/' + path
        wav_file = os.path.basename(path)
        if char_name is not None:
            vo_dest_dir = f"{dest}/{dest_lang}/角色语音 - Character/{char_name}"
            bt_dest_dir = f"{dest}/{dest_lang}/战斗语音 - Battle/{char_name}"
            cv_dest_dir = f"{dest}/{dest_lang}/多人对话 - Conversation/{char_name}"
            mo_dest_dir = f"{dest}/{dest_lang}/怪物语音 - Monster/{char_name}"
            ot_dest_dir = f"{dest}/{dest_lang}/其它语音 - Others/{char_name}"
            vo_wav_path = f"{vo_dest_dir}/{wav_file}"
            bt_wav_path = f"{bt_dest_dir}/{wav_file}"
            cv_wav_path = f"{cv_dest_dir}/{wav_file}"
            mo_wav_path = f"{mo_dest_dir}/{wav_file}"
            ot_wav_path = f"{ot_dest_dir}/{wav_file}"
            if is_file(wav_source) == True:
                if is_in(path, battle) == True:
                    if not os.path.exists(bt_dest_dir):
                       Path(f"{bt_dest_dir}").mkdir(parents=True)
                    dest_path = bt_wav_path
                elif is_in(path, conv) == True:
                    if not os.path.exists(cv_dest_dir):
                       Path(f"{cv_dest_dir}").mkdir(parents=True)
                    dest_path = cv_wav_path
                elif is_in(path,monster) == True:
                    if not os.path.exists(mo_dest_dir):
                       Path(f"{mo_dest_dir}").mkdir(parents=True)
                    dest_path = mo_wav_path
                elif has_vaild_content(text) == False:
                    if not os.path.exists(ot_dest_dir):
                       Path(f"{ot_dest_dir}").mkdir(parents=True)
                    dest_path = ot_wav_path
                else:
                    if not os.path.exists(vo_dest_dir):
                       Path(f"{vo_dest_dir}").mkdir(parents=True)
                    dest_path = vo_wav_path
                if mode.upper()=='CP':
                    copy(wav_source,dest_path)
                elif mode.upper()=='MV':
                    move(wav_source,dest_path)
                else:
                    print("模式错误，请选择cp/mv")
                    exit()
    except:
        pass
f.close()