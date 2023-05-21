import os
import json
import argparse
from collections import defaultdict
from fnvhash import fnv1_64

class GenshinVoice(object):
    def __init__(self, git_path: str, lang: str, dest: str):
        self.path = git_path
        self.lang = lang
        self.dest = dest + '/'
        self.vo_lang = self.get_vo_lang()
        self.textmap = dict(self.input_json(
            f"./TextMap/TextMap{self.lang}.json"
        ))

    def main(self):
        # 变量申明
        fetter_index = dict()
        dialog_index = dict()

        # 解包素材加载
        lut_dict = dict(self.input_json(
            './BinOutput/Voice/Lut/Lut.json'
        ))

        # 主要角色 ID 索引
        avatar_dict = self.create_avatar_index()
        npc_dict = self.create_npc_index(avatar_dict)

        # 语音分类解析
        for k, v in dict(lut_dict).items():
            if v.get('gameTriggerArgs'):
                self.lut_type_sorting(k, v, 'Fetter', fetter_index)
                self.lut_type_sorting(k, v, 'Dialog', dialog_index)

        self.create_fetter_index(avatar_dict, fetter_index)
        self.create_dialog_index(npc_dict, dialog_index)
        # python 3.9+ feature
        master_index = fetter_index | dialog_index

        print(f"Index num: {len(master_index.keys())}")
        self.output_json(self.dest + self.vo_lang + ".json", master_index)

        return

    def create_fetter_index(self, avatar: dict, data: dict):
        item_index = dict()
        fetter_index = defaultdict(list)

        self.from_lut_index_item(data, item_index)

        fetters_config_list = self.input_json(
            './ExcelBinOutput/FettersExcelConfigData.json'
        )

        # 读取 fetter config 文件
        for i in fetters_config_list:
            if i.get('voiceFile'):
                i_args = i.get('voiceFile')
                name_id = i.get('avatarId')

                name = avatar[name_id]['avatarName'] if name_id else None
                switch = avatar[name_id]['voiceSwitch'] if name_id else None
                name_local = (
                    avatar[name_id]['avatarNameText']
                    if name_id else None
                )
                text_textmaphash = i.get('voiceFileTextTextMapHash')
                text = self.textmap.get(str(text_textmaphash))
                # 索引 fetter_index
                fetter_index[i_args].append({
                    "avatarName": name,
                    "talkName": name_local,
                    "avatarSwitch": switch,
                    "voiceContent": text
                })
            else:
                continue

        # 把 fetter 和 item 中的 sourceName 进行匹配
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

        # 生成 fnv164 hash 索引
        data.clear()
        for v in fetter_index.values():
            for i in v:
                vo_hash = self.fnvhash_string(i.get('sourceFileName'))
                data.update({
                    vo_hash: i
                })

        # self.output_json("[debug]fetterIndex.json", data) # Debug

    def create_dialog_index(self, npc: dict, data: dict):
        item_index = dict()
        dialog_index = dict()

        self.from_lut_index_item(data, item_index)
        dialog_config_list = self.input_json(
            './ExcelBinOutput/DialogExcelConfigData.json'
        )

        for i in dialog_config_list:
            if i.get('GFLDJMJKIKE'):
                i_args = i.get('GFLDJMJKIKE')
                i_npc_id = i.get('talkRole').get('id', [])
                i_text_hash = i.get('talkContentTextMapHash')

                dialog_index.update({
                    i_args: {
                        "talkNpcID": i_npc_id,
                        "voiceContentTextMapHash": i_text_hash
                    }
                })

        data.clear()
        for k, v in item_index.items():
            # Dialog 中存在内容索引，并且 item 中不为空
            if dialog_index.get(k) and len(v) > 0:
                # 存在双主角语音，此处需要用列表循环
                vo_source = [it.get('sourceFileName') for it in v]
                vo_switch = [it.get('avatarName').lower() for it in v]
                for seq, vo in enumerate(vo_source):
                    # 计算 voice 文件索引 hash
                    vo_hash = self.fnvhash_string(vo)
                    # 查找 talkNpc 索引
                    talk_id = dialog_index[k].get('talkNpcID', [])
                    
                    talk_name = npc.get(talk_id, {})
                    vo_text = self.textmap.get(str(
                        dialog_index[k].get('voiceContentTextMapHash')
                    ))
                    # 如果语音文本为空，跳过这条语音
                    if not vo_text:
                        continue

                    data.update({
                        vo_hash:{
                            "voiceContent": vo_text,
                            "sourceFileName": vo
                        }
                    })
                    data[vo_hash].update(talk_name)
                    # 如果存在 vo_switch 字段，一般是双主角语音，
                    # 而且在 dialog_index 中不存在 npc_id。需在此处另外索引
                    # 这里把变量写死可能导致预料外的错误，但暂时没想到更好的解决方法
                    if len(vo_switch) > 0 :
                        char_switch = vo_switch[seq]
                        if char_switch == 'switch_hero':
                            char_name = 'PlayerBoy'
                        elif char_switch == 'switch_heroine':
                            char_name = 'PlayerGirl'
                        else:
                            continue
                        char_talk_name = self.textmap.get(str('1533656818'))
                        data[vo_hash].update({
                            "talkName": char_talk_name,
                            "avatarName": char_name
                        })
            else:
                continue

    def create_avatar_index(self):
        index_dict = dict()

        avatar_config_list = self.input_json(
            './ExcelBinOutput/AvatarExcelConfigData.json'
        )

        for i in avatar_config_list:
            # 分割游戏内头像名称，偷鸡角色名
            name = str(i.get('iconName')).split('_')[-1]
            # 通过角色名，读取每个角色的 voiceSwitch 名称
            single_avatar_conf = self.input_json(
                f"./BinOutput/Avatar/ConfigAvatar_{name}.json"
            )
            # 下行可能引起 KeyError
            voice_switch = single_avatar_conf["audio"]["voiceSwitch"]["text"]

            id = i.get('id')
            name_textmaphash = i.get('nameTextMapHash')
            name_text = self.textmap.get(str(name_textmaphash))
            index_dict.update({
                id: {
                    "avatarName": name,
                    "avatarNameText": name_text,
                    "voiceSwitch": voice_switch
                }
            })
        return index_dict

    def create_npc_index(self, avatar_index: dict):
        index_dict = dict()

        # 为了避免频繁遍历字典，把字典的 key 提取为 avatar_id_list，
        # 把我们需要匹配的关键字提取为 avatar_name_list，
        # 而后再根据所需元素在列表中的索引位置，直接访问到其在字典中的所属 key。
        avatar_id_list = [i for i in avatar_index.keys()]
        avatar_name_list = [
            i['avatarNameText']
            for i in avatar_index.values()
        ]

        npc_config_list = self.input_json(
            './ExcelBinOutput/NpcExcelConfigData.json'
        )

        for i in npc_config_list:
            npc_id = str(i.get('id'))
            npc_name = self.textmap.get(
                str(i.get('nameTextMapHash'))
            )
            index_dict.update({
                npc_id: {
                    "talkName": npc_name
                }
            })
            # 如果此 npc 是一个主要角色，打上一个 avatarName 标签
            if npc_name in avatar_name_list:
                # 主要角色的 id 需要根据元素在 avatar_name_list 中的索引位置，
                # 到先前生成的 avatar_id_list 中的对应索引位置访问
                avatar_id = avatar_id_list[
                    avatar_name_list.index(npc_name)
                ]
                avatar_name = avatar_index[avatar_id]['avatarName']
                index_dict[npc_id].update({
                    "avatarName": avatar_name
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

    def get_item_dict(self, id: str):
        """专门用于读取 {item}.json 的 input_json 方法变种"""
        item_path = os.path.join(
            self.path, f"./BinOutput/Voice/Items/{id}.json"
        )
        # 应该判断 Item Files 是否存在
        if os.path.exists(item_path):
            with open(item_path, encoding="utf-8") as f:
                item_dict = dict(json.load(f))
        else:
            item_dict = None
        return item_dict

    def lut_type_sorting(self, lut_k, lut_v, type: str, sort_index: dict):
        """用于在 main 循环里，根据语音 type str 分类解析到对应的字典中"""

        if lut_v['GameTrigger'] == type:
            sort_index[str(lut_k)] = {
                "itemFileID": int(lut_v['fileID']),
                "voiceType": str(type),
                "gameTriggerArgs": int(lut_v['gameTriggerArgs'])
            }

    def from_lut_index_item(self, lut_part: dict, item_part: dict):
        """
        根据输入的 Lut.json 索引到对应的 {item}.json，其中包含了 sourceFileName 字段；\n
        此方法用于已经在 main 中完成的 type 分类拣选的 Lut 字典；
        - lut_part 需要进行索引的已分类 Lut 字典；
        - item_part 索引结果输出字典，此变量应该是一个空字典
        """
        # 根据 Lut.json 索引读取 Item Files，其中包含 sourceFileName
        for k, v in lut_part.items():
            item_dict = self.get_item_dict(v.get('itemFileID'))

            if item_dict is not None:
                args = v.get('gameTriggerArgs')
                for i in item_dict.values():
                    if i.get('gameTriggerArgs') == args:
                        item_part.update({
                            args: i.get('SourceNames', [])
                        })
            else:
                continue

        # 清洗 Item index 数据
        for i in item_part.values():
            for d in i:
                if 'emotion' in d:
                    del d['emotion']
                if 'rate' in d:
                    del d['rate']

        return item_part

    def input_json(self, relative_path: str):
        """
        用于读取 json 文件
        - relative_path 是 git repo 目录下文件的相对路径
        """
        absolute_path = os.path.join(self.path, relative_path)
        with open(absolute_path, encoding="utf-8") as f:
                json_decode = json.load(f)
        return json_decode

    def output_json(self, relative_path: str, output_dict: dict):
        """
        用于输出 json 文件
        - relative_path 是 git repo 目录下文件的相对路径
        - output_dict 是要导出的字典
        """
        absolute_path = os.path.join(self.path, relative_path)
        with open(absolute_path, "w", encoding="utf-8") as f:
            json.dump(output_dict, f, ensure_ascii=False, indent=2)

    def fnvhash_string(self, string: str):
        hash_string = f"{self.vo_lang}\\{string}".lower()
        fnv_hash = format(
            fnv1_64(bytes(hash_string, "utf-8")),"016x"
        )
        return fnv_hash


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, help='Dim 的原神数据文件路径', required=True)
    parser.add_argument('--dest', type=str, help='目标路径，可选，默认为数据文件夹根目录', default='./')
    parser.add_argument('--lang', type=str, help='语言，可选 CHS/EN/JP/KR，默认为 CHS', default='CHS')
    args = parser.parse_args()
    path = str(args.source)
    lang = str(args.lang)
    dest = str(args.dest)
    GenshinVoice(path, lang, dest).main()
