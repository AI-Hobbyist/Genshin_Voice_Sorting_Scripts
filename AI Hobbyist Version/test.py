import json, re, os, argparse
from tqdm import tqdm
from pathlib import Path
from glob import glob

ver = '4.1'
language = 'JP'
player = "PlayerGirl"

def is_in(full_path, regx):
    if re.findall(regx, full_path):
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

langcode, dset_lang = get_path_by_lang(language)

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


print(f"lang code: {langcode}\npath: {dset_lang}\nplayer name: {ren_player(player,language)}")