import os
import json
import argparse
from collections import defaultdict
from fnvhash import fnv1_64

class GenshinVoice(object):
    def __init__(self, git_path: str, lang: str):
        self.path = git_path
        self.lang = lang
        self.vo_lang = self.get_vo_lang()

    def main(self):
        # 变量申明
        readable_index = dict()

        # 解包素材加载
        lut_path = os.path.join(self.path, './BinOutput/Voice/Lut/Lut.json')
        textmap_path = os.path.join(self.path, f"./TextMap/TextMap{lang}.json")
        with open(lut_path, encoding="utf-8") as f:
            lut_dict = json.load(f)
        with open(textmap_path, encoding="utf-8") as f:
            textmap_dict = json.load(f)

        # 主要角色 ID 索引
        avatar_dict = self.create_avatar_index()

        # 语音分类解析
        for k, v in dict(lut_dict).items():
            if v['GameTrigger'] == 'Fetter':
                readable_index[str(k)] = {
                    "itemFileID": int(v['fileID']),
                    "voiceType": "Fetter",
                    "gameTriggerArgs": int(v['gameTriggerArgs'])
                }
        self.create_fetter_index(textmap_dict, avatar_dict, readable_index)


        return readable_index

    def create_fetter_index(self, textmap: dict, avatar: dict, data: dict):
        item_index = dict()
        fetter_index = defaultdict(list)

        fetters_config_path = os.path.join(
            self.path,
            './ExcelBinOutput/FettersExcelConfigData.json'
        )
        with open(fetters_config_path, encoding="utf-8") as f:
            fetters_config_list = json.load(f)

        # 根据 Lut.json 索引读取 Item Files，其中包含 sourceFileName
        for k, v in data.items():
            item_path = os.path.join(
                self.path,
                f"./BinOutput/Voice/Items/{v.get('itemFileID')}.json"
            )
            # 预防意外，判断 Item Files 是否存在
            if os.path.exists(item_path):
                with open(item_path, encoding="utf-8") as f:
                    item_dict = dict(json.load(f))
                
                args = v.get('gameTriggerArgs')
                for i in item_dict.values():
                    if i.get('gameTriggerArgs') == args:
                        item_index.update({
                            args: i.get('SourceNames', [])
                        })
            else:
                continue

        # 清洗 Item index 数据
        for i in item_index.values():
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
                # 索引 fetter_index
                fetter_index[i_args].append({
                    "avatarName": name,
                    "avatarNameText": name_local,
                    "avatarSwitch": switch,
                    "voiceContent": text
                })
            else:
                continue

        for k, v in fetter_index.items():
            # 当前 args 的 item list
            # 数据类型：列表「v；*_list」；字典「d；*_index」
            item_list = item_index.get(int(k))
            item_switch_list = [d.get('avatarName').lower() for d in item_list]
            fetter_switch_list = [d.get('avatarSwitch').lower() for d in v]

            for list_seq, fetter_switch in enumerate(fetter_switch_list):
                # 从 fetter 中拿 switch 到 item 中匹配相同的 switch
                seq = item_switch_list.index(fetter_switch)
                source_file_name = item_list[seq].get('sourceFileName')
                v[list_seq].update(sourceFileName=source_file_name)

        data.clear()
        for v in fetter_index.values():
            for i in v:
                vo_hash = self.fnvhash_string(i.get('sourceFileName'))
                data.update({
                    vo_hash: i
                })

        # Debug 用测试代码
        # output0_path = os.path.join(self.path, "output0.json")
        # with open(output0_path, "w", encoding="utf-8") as f:
        #     json.dump(data, f, ensure_ascii=False, indent=2)
        pass

    def create_avatar_index(self):
        index_dict = dict()

        avatar_config_path = os.path.join(
            self.path,
            './ExcelBinOutput/AvatarExcelConfigData.json'
        )
        with open(avatar_config_path, encoding="utf-8") as f:
            avatar_config_list = json.load(f)
        
        for i in avatar_config_list:
            # 分割游戏内头像名称，偷鸡角色名
            name = str(i.get('iconName')).split('_')[-1]
            # 通过角色名，读取每个角色的 voiceSwitch 名称
            single_avatar_conf_path = os.path.join(
                self.path,
                f"./BinOutput/Avatar/ConfigAvatar_{name}.json"
            )
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

    def get_vo_lang(self):
        lang_code = ['CHS', 'EN', 'JP', 'KR']
        vo_lang_name = ['Chinese', 'English(US)', 'Japanese', 'Korean']
        try:
            i = lang_code.index(self.lang)
            vo_lang = vo_lang_name[i]
        except:
            raise ValueError('language code has mistake')

        return vo_lang

    def fnvhash_string(self, string: str):
        hash_string = f"{self.vo_lang}\\{string}".lower()
        fnv_hash = format(
            fnv1_64(bytes(hash_string, "utf-8")),"016x"
        )
        return fnv_hash


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    path = 'your/animeGameData/local/path'
    lang = 'CHS'
    GenshinVoice(path, lang).main()
