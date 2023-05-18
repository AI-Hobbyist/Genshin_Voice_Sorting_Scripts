import os
import json
from collections import defaultdict

def index_main(git_path: str, lang: str):
    # 变量申明
    readable_index = dict()

    # 解包素材加载
    lut_path = os.path.join(git_path, './BinOutput/Voice/Lut/Lut.json')
    textmap_path = os.path.join(git_path, f"./TextMap/TextMap{lang}.json")
    with open(lut_path, encoding="utf-8") as f:
        lut_dict = json.load(f)
    with open(textmap_path, encoding="utf-8") as f:
        textmap_dict = json.load(f)

    # 主要角色 ID 索引
    avatar_dict = create_avatar_index(git_path)

    # 语音分类解析
    for k, v in dict(lut_dict).items():
        if v['GameTrigger'] == 'Fetter':
            readable_index[str(k)] = {
                "itemFileID": int(v['fileID']),
                "voiceType": "Fetter",
                "gameTriggerArgs": int(v['gameTriggerArgs'])
            }
    create_fetters_index(git_path, textmap_dict, avatar_dict, readable_index)
    

    return readable_index

def create_fetters_index(git_path: str, textmap: dict, avatar: dict, data: dict):
    index_data = dict()
    fetters_index = defaultdict(list)

    fetters_config_path = os.path.join(git_path, './ExcelBinOutput/FettersExcelConfigData.json')
    with open(fetters_config_path, encoding="utf-8") as f:
        fetters_config_list = json.load(f)

    # 根据 Lut.json 索引读取 Item Files，其中包含 sourceFileName
    for k, v in data.items():
        item_path = os.path.join(git_path, f"./BinOutput/Voice/Items/{v.get('itemFileID')}.json")
        # 预防意外，判断 Item Files 是否存在
        if os.path.exists(item_path):
            with open(item_path, encoding="utf-8") as f:
                item_dict = dict(json.load(f))
            
            args = v.get('gameTriggerArgs')
            for i in item_dict.values():
                if i.get('gameTriggerArgs') == args:
                    index_data.update({
                        args: i.get('SourceNames', [])
                    })
        else:
            continue
    
    # 清洗 Item index 数据
    for i in index_data.values():
        for d in i:
            if 'emotion' in d:
                del d['emotion']
            if 'rate' in d:
                del d['rate']

    # 读取 fetter config 文件
    for i in fetters_config_list:
        if i.get('voiceFile'):
            i_args = i.get('voiceFile')
            name_id = i.get('avatarId')

            name = avatar[name_id]['avatarName'] if name_id else None
            switch = avatar[name_id]['voiceSwitch'] if name_id else None
            name_local = textmap.get(
                str(avatar[name_id]['avatarNameTextMapHash'])
            ) if name_id else None
            text_textmaphash = i.get('voiceFileTextTextMapHash')
            text = textmap.get(str(text_textmaphash))
            # 索引 fetters_index
            fetters_index[i_args].append({
                "avatarName": name,
                "avatarNameText": name_local,
                "avatarSwitch": switch,
                "voiceContent": text
            })
        else:
            continue
    
    for k, v in fetters_index.items():
        # 当前 args 的 item list
        # 数据类型：列表「v；*_list」；字典「d；*_index」
        item_list = index_data.get(int(k))
        item_switch_list = [d.get('avatarName').lower() for d in item_list]
        fetter_switch_list = [d.get('avatarSwitch').lower() for d in v]
        for list_seq, fetter_switch in enumerate(fetter_switch_list):
            seq = item_switch_list.index(fetter_switch)
            source_file_name = item_list[seq].get('sourceFileName')
            v[list_seq].update(sourceFileName=source_file_name)

    # Debug 用测试代码
    # output0_path = os.path.join(git_path, "output0.json")
    # with open(output0_path, "w", encoding="utf-8") as f:
    #     json.dump(index_data, f, ensure_ascii=False, indent=2)

    # output1_path = os.path.join(git_path, "output1.json")
    # with open(output1_path, "w", encoding="utf-8") as f:
    #     json.dump(fetters_index, f, ensure_ascii=False, indent=2)

    pass

def create_avatar_index(git_path: str):
    index_dict = dict()

    avatar_config_path = os.path.join(git_path, './ExcelBinOutput/AvatarExcelConfigData.json')
    with open(avatar_config_path, encoding="utf-8") as f:
        avatar_config_list = json.load(f)
    
    for i in avatar_config_list:
        # 分割游戏内头像名称，偷鸡角色名
        name = str(i.get('iconName')).split('_')[-1]
        # 通过角色名，读取每个角色的 voiceSwitch 名称
        single_avatar_conf_path = os.path.join(git_path, f"./BinOutput/Avatar/ConfigAvatar_{name}.json")
        with open(single_avatar_conf_path, encoding="utf-8") as f:
            single_avatar_conf = dict(json.load(f))
        # 下行可能引起 KeyError
        voice_switch = single_avatar_conf["audio"]["voiceSwitch"]["text"]

        name_textmaphash = i.get('nameTextMapHash')
        id = i.get('id')
        index_dict.update({
            id: {
                "avatarName": name,
                "avatarNameTextMapHash": name_textmaphash,
                "voiceSwitch": voice_switch
            }
        })
    return index_dict

if __name__ == '__main__':
    path = 'your/animeGameData/local/path'
    lang = 'CHS'
    index_main(path, lang)
    pass
