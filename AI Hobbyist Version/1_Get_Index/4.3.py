import os
import json
import argparse
from pathlib import Path
from collections import defaultdict
from fnvhash import fnv1_64

class GenshinVoice(object):
    def __init__(self, git_path: str, output_path: str, lang: str):
        self.path = git_path
        self.output_path = output_path
        self.lang = lang
        self.vo_lang = self.get_vo_lang()
        self.textmap = dict(self.input_json(
            f"./TextMap/TextMap{self.lang}.json"
        ))
        self.vo_item = self.get_item_dict_sort()

    def main(self):
        # 变量申明
        (fetter_index,
         dialog_index,
         reminder_index,
         card_index) = ({}, {}, {}, {})

        # 解包素材加载
        lut_dict = dict(self.input_json(
            './BinOutput/Voice/Lut/Lut.json'
        ))
        # 主要角色 ID 索引
        avatar_dict = self.create_avatar_index()
        npc_dict = self.create_npc_index(avatar_dict)

        # 语音分类解析
        for k, v in dict(lut_dict).items():
            if v.get('DDGNNKAFNFF'):
                self.lut_type_sorting(k, v, 'Fetter', fetter_index)
                self.lut_type_sorting(k, v, 'Dialog', dialog_index)
                self.lut_type_sorting(k, v, 'DungeonReminder', reminder_index)
                self.lut_type_sorting(k, v, 'Card', card_index)

        self.create_fetter_index(avatar_dict, fetter_index)
        self.create_dialog_index(npc_dict, dialog_index)
        self.create_reminder_index(npc_dict, reminder_index)
        self.create_card_index(avatar_dict, card_index)

        # python 3.9+ feature
        master_index = fetter_index | dialog_index | reminder_index | card_index

        print(f"Index num: {len(master_index.keys())}")
        self.output_json(os.path.join(
            self.output_path, f"{self.lang}.json"
            ), master_index)

        return

    def create_fetter_index(self, avatar: dict, data: dict):
        _item_index = dict()
        _fetter_index = defaultdict(list)

        self.lut_index_item(data, _item_index)

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
                _fetter_index[i_args].append({
                    "avatarName": name,
                    "talkName": name_local,
                    "avatarSwitch": switch,
                    "voiceContent": text
                })
            else:
                continue

        # 把 fetter 和 item 中的 sourceName 进行匹配
        for k, v in _fetter_index.items():
            # 当前 args 的 item list
            # 数据类型：列表「v；*_list」；字典「d；*_index」
            item_list = _item_index.get(int(k))
            item_switch_list = [d.get('avatarName').lower() for d in item_list]
            fetter_switch_list = [d.get('avatarSwitch').lower() for d in v]

            for list_seq, fetter_switch in enumerate(fetter_switch_list):
                # 从 fetter 中拿 switch 到 item 中匹配相同的 switch
                # if fetter_switch in item_switch_list:
                seq = item_switch_list.index(fetter_switch)
                source_file_name = item_list[seq].get('sourceFileName')
                v[list_seq].update(sourceFileName=source_file_name)

        # 生成 fnv164 hash 索引
        data.clear()
        for v in _fetter_index.values():
            for i in v:
                vo_hash = self.fnvhash_string(i.get('sourceFileName'))
                data.update({
                    vo_hash: i
                })

    def create_dialog_index(self, npc: dict, data: dict):
        _item_index, _dialog_index = {}, {}

        self.lut_index_item(data, _item_index)
        dialog_config_list = self.input_json(
            './ExcelBinOutput/DialogExcelConfigData.json'
        )

        for i in dialog_config_list:
            if i.get('GFLDJMJKIKE'):
                i_args = i.get('GFLDJMJKIKE')
                i_npc_id = i.get('talkRole').get('id', [])
                i_text_hash = i.get('talkContentTextMapHash')

                _dialog_index.update({
                    i_args: {
                        "talkNpcID": i_npc_id,
                        "voiceContentTextMapHash": i_text_hash
                    }
                })
        self.get_quest_voice(_dialog_index)
        self.get_quest_voice_add(_dialog_index)

        data.clear()
        for k, v in _item_index.items():
            # Dialog 中存在内容索引，并且 item 中不为空
            if _dialog_index.get(k) and len(v) > 0:
                # 存在双主角语音，此处需要用列表循环
                vo_source = [it.get('sourceFileName') for it in v]
                vo_switch = [it.get('avatarName').lower() for it in v]
                for seq, vo in enumerate(vo_source):
                    # 计算 voice 文件索引 hash
                    vo_hash = self.fnvhash_string(vo)
                    # 查找 talkNpc 索引
                    talk_namehash = _dialog_index[k].get("talkNameHash")
                    if not talk_namehash:
                        talk_id = _dialog_index[k].get('talkNpcID')
                        talk_name = npc.get(talk_id, {})
                    else:
                        talk_name = {
                            "talkName": self.textmap.get(str(talk_namehash))
                        }
                    vo_text = self.textmap.get(str(
                        _dialog_index[k].get('voiceContentTextMapHash')
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
                    if len(vo_switch) > 1 :
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

    def create_reminder_index(self, npc: dict, data: dict):
        _item_index, _reminder_index = {}, {}

        self.lut_index_item(data, _item_index)
        reminder_config_list = self.input_json(
            './ExcelBinOutput/ReminderExcelConfigData.json'
        )

        for d in reminder_config_list:
            if d.get('id'):
                _args = d.get('id')
                _speaker = self.textmap.get(str(d.get('speakerTextMapHash')))
                _content = self.textmap.get(str(d.get('contentTextMapHash')))
                _reminder_index.update({
                    _args: {
                        "talkName": _speaker,
                        "voiceContent": _content
                    }
                })
            else:
                continue
        
        # 重新构建 npc 索引，因为 reminder 不包含 npc_id 无法直接调用
        _npc_dict = {}
        for v in npc.values():
            if v.get('avatarName'):
                _npc_dict.update({
                    v.get('talkName'): v.get('avatarName')
                })

        data.clear()
        for k, v in _item_index.items():
            if _reminder_index.get(k) and len(v) > 0:
                # 存在双主角语音，此处需要用列表循环
                vo_source = [it.get('sourceFileName') for it in v]
                vo_switch = [it.get('avatarName').lower() for it in v]
                for seq, vo in enumerate(vo_source):
                    vo_hash = self.fnvhash_string(vo)
                    vo_name = _reminder_index[k].get('talkName')
                    vo_text = _reminder_index[k].get('voiceContent')
                    data.update({
                        vo_hash:{
                            "sourceFileName": vo,
                            "voiceContent": vo_text,
                            "talkName": vo_name
                        }
                    })
                    if vo_name in _npc_dict:
                        data[vo_hash].update({
                            "avatarName": _npc_dict[vo_name]
                        })
                    # 如果存在 vo_switch 字段，一般是双主角语音
                    if len(vo_switch) > 1 :
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

    def create_card_index(self, avatar: dict, data: dict):
        _item_index, _card_index = {}, {}

        self.lut_index_item(data, _item_index)
        card_config_list = self.input_json(
            './ExcelBinOutput/GCGTalkDetailExcelConfigData.json'
        )
        card_tutorial_list = self.input_json(
            './ExcelBinOutput/GCGTutorialTextExcelConfigData.json'
        )

        # 读取 card config 文件
        for i in card_config_list:
            if i.get('PDNENGPCKKL'):
                voice_id = i.get('PDNENGPCKKL')
                avatar_id = list(i.get('JKPKBLJAMAG'))[0]
                # 过滤掉非主要角色的语音
                if avatar_id not in avatar:
                    continue
                avatar_name = avatar[avatar_id]['avatarName']
                local_name = avatar[avatar_id]['avatarNameText']
                text_textmaphash = list(i.get('IHLOECKCMGE'))[0]
                text = self.textmap.get(str(text_textmaphash))
                # 索引 card_index
                _card_index.update({
                    voice_id: {
                        "avatarName": avatar_name,
                        "talkName": local_name,
                        "voiceContent": text
                    }
                })
            else:
                continue

        # 七圣召唤新手教程语音
        for i in card_tutorial_list:
            if i.get('MMAKMNKEICJ'):
                voice_id = i.get('MMAKMNKEICJ')
                text_textmaphash = i.get('NNBJGAAFKBG')
                text = self.textmap.get(str(text_textmaphash))

                # 此处添加校验，检查是否为预料内的说话人
                speaker_check = str(
                    _item_index[voice_id][0]['sourceFileName']
                ).split('_')
                if speaker_check[-2] == 'diona':
                    avatar_id = 10000039
                elif speaker_check[-4] == 'shinobu':
                    avatar_id = 10000065
                elif speaker_check[-4] == 'itto':
                    avatar_id = 10000057
                else:
                    raise IndexError(f"Please Check Voice ID: {voice_id}")

                avatar_name = avatar[avatar_id]['avatarName']
                local_name = avatar[avatar_id]['avatarNameText']

                _card_index.update({
                    voice_id: {
                        "avatarName": avatar_name,
                        "talkName": local_name,
                        "voiceContent": text,
                    }
                })

        data.clear()
        for k, v in _item_index.items():
            if k in _card_index:
                vo_source = [it.get('sourceFileName') for it in v][0]
                vo_hash = self.fnvhash_string(vo_source)
                data.update({
                    vo_hash: _card_index[k]
                })
                data[vo_hash].update({
                    "sourceFileName": vo_source
                })
            else:
                continue

    def create_avatar_index(self):
        index_dict = {}

        avatar_config_list = self.input_json(
            './ExcelBinOutput/AvatarExcelConfigData.json'
        )

        for i in avatar_config_list:
            # 4.2 补丁（很生硬）
            name_to_switch = {
                "PlayerBoy": "Switch_hero",
                "PlayerGirl": "Switch_heroine",
                "Feiyan": "Switch_Yanfei",
                "Shougun": "Switch_raidenShogun",
                "Sara": "Switch_kujouSara",
                "Tohma": "Switch_Thoma",
                "Yae": "Switch_YaeMiko",
                "Alhatham": "Switch_Alhaitham",
                "Baizhuer": "Switch_Baizhu",
                "Momoka": "Switch_Kirara",
                "Liney": "Switch_Lyney",
                "Linette": "Switch_Lynette",
                "Heizo": "Switch_Heizou"
            }
            # 分割游戏内头像名称，偷鸡角色名
            name = str(i.get('iconName')).split('_')[-1]
            if name in name_to_switch.keys():
                voice_switch = name_to_switch[name]
            else:
                voice_switch = f"Switch_{name}"

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
        index_dict = {}

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

    def get_item_dict_in(self, path: str):
        """
        专门用于读取 {item}.json 的 input_json 方法变种\n
        直接把 BinOutpt/Voice/Items 目录下所有文件加载进来
        """
        with open(path, encoding="utf-8") as f:
            item_dict = dict(json.load(f))
        # 返回结果申明
        result_dict = {}
        for v in item_dict.values():
            # 如果语音索引 id 不存在，就跳过
            if v.get('GameTrigger'):
                vo_id = v.get('gameTriggerArgs')
                vo_type = v.get('GameTrigger')
                vo_source = v.get('SourceNames')

            elif v.get('BFKCDJLLGNJ'):
                vo_id = v.get('FMHLBONJKPJ')
                vo_type = v.get('BFKCDJLLGNJ')
                vo_source = v.get('OFEEIPOMNKD')

            elif v.get('BEHKGKMMAPD'):
                vo_id = v.get('FFDHLEAFBLM')
                vo_type = v.get('BEHKGKMMAPD')
                vo_source = v.get('EIKJKDICKMJ')

            if vo_id == None or vo_source == None:
                continue
            # SoureName 中无效键值对清洗
            for d in vo_source:
                if 'emotion' in d:
                    del d['emotion']
                if 'rate' in d:
                    del d['rate']
                if 'HBDMHPLJGBG' in d:
                    del d['HBDMHPLJGBG'] ; del d['GCAGMFHFFML']
                    d['sourceFileName'] = d.get('CBGLAJNLFCB')
                    d['avatarName'] = d.get('GJMDHCLJGHH')
                    del d['CBGLAJNLFCB'] ; del d['GJMDHCLJGHH']
                if 'NNBGHAJLJLA' in d:
                    del d['NNBGHAJLJLA'] ; del d['EJNOJBCBJPP']
                    d['sourceFileName'] = d.get('HLGOMILNFNK')
                    d['avatarName'] = d.get('KAGFOFEDGIA')
                    del d['HLGOMILNFNK'] ; del d['KAGFOFEDGIA']      
            # 如果不存在重名键，直接 update
            if vo_id not in result_dict:
                result_dict.update({
                    vo_id: {
                        vo_type: vo_source
                    }
                })
                continue
            # 如果有重名键就 update 值
            result_dict[vo_id].update({
                vo_type: vo_source
            })
        return result_dict

    def get_item_dict_sort(self):
        """
        索引出全部 item.json 的 voice id 和 source name
        """
        voice_item = {}
        # 创建 {item}.json 的路径列表
        item_dir = os.path.join(self.path, './BinOutput/Voice/Items')
        item_path_list = []
        for file in os.listdir(item_dir):
            if file.endswith('.json'):
                item_path_list.append(os.path.join(item_dir, file))
        # BinOutput/Voice/ 目录下的散装文件
        item_dir_issue = f"{self.path}/BinOutput/Voice"
        for file in os.listdir(item_dir_issue):
            if file.endswith('.json'):
                item_path_list.append(f"{self.path}/BinOutput/Voice/{file}")

        for i in item_path_list:
            result = self.get_item_dict_in(i)
            for _id, _item in result.items():
                # 结果中不存在当前 voice item id，直接 update
                if _id not in voice_item:
                    voice_item.update({
                        _id: _item
                    })
                    continue

                # 不知道键名，需要 for loop 取值
                for _type in _item.keys():
                    if voice_item[_id].get(_type):
                        # 此处从列表中取值，追加到输出列表中
                        for j in _item[_type]:
                            voice_item[_id][_type].append(j)
                    else:
                        voice_item[_id].update(_item)

        return voice_item

    def get_quest_voice(self, dialog_data: dict):
        """
        由于 /ExcelBinOutput/DialogExcelConfigData.json 缺少部分新版本语音\n
        此方法读取所有任务数据，分析带有语音和文本的条目
        """
        quest_dir = f"{self.path}/BinOutput/CodexQuest"
        quests_path = []
        for file in os.listdir(quest_dir):
            if file.endswith('.json'):
                quests_path.append(f"{quest_dir}/{file}")
        
        for path in quests_path:
            with open(path, encoding="utf-8") as f:
                quest = dict(json.load(f))

            subquests = quest.get("subQuests")
            if subquests is None:
                continue
            for sub in subquests:
                if not sub.get("items"):
                    continue
                dialogs = sub["items"]
                for i in dialogs:
                    if not i.get("dialogs"):
                        continue
                    speaker = i.get("speakerText")
                    speaker_namehash = speaker.get("textId")
                    voice = i.get("dialogs")
                    vo_args = voice[0]["soundId"]
                    vo_texthash = voice[0]["text"]["textId"]

                    dialog_data.update({
                        vo_args: {
                            "talkNameHash": speaker_namehash,
                            "voiceContentTextMapHash": vo_texthash
                    }})

    def get_quest_voice_add(self, dialog_data: dict):
        """
        由于缺少新版本【活动】语音，此方法为读取 dialog 类型语音 id 及其文本的方法。
        【原神 4.3】版本新增
        """
        quest_dir = f"{self.path}/BinOutput/Talk/Quest"
        quests_path = []
        for file in os.listdir(quest_dir):
            if file.endswith('.json'):
                quests_path.append(f"{quest_dir}/{file}")

        for path in quests_path:
            with open(path, encoding="utf-8") as f:
                quest = dict(json.load(f))

            if quest.get("talkId") is None:
                continue
            dialog_list = quest.get("dialogList")
            if dialog_list is None:
                continue
            for dialog in dialog_list:
                vo_args = dialog.get("id")
                vo_texthash = dialog.get("talkContentTextMapHash")
                talk_role = dialog.get("talkRole").get("id")

                dialog_data.update({
                        vo_args: {
                            "talkNpcID": talk_role,
                            "voiceContentTextMapHash": vo_texthash
                    }})

    def lut_type_sorting(self, lut_k, lut_v, type: str, sort_index: dict):
        """用于在 main 循环里，根据语音 type str 分类解析到对应的字典中"""

        # 4.2 更新
        type_dict = {
            4: 'Dialog',
            6: 'DungeonReminder',
            8: 'AnimatorEvent',
            10: 'Fetter',
            14: 'JoinTeam',
            16: 'Card'
        }
        type_id = int(lut_v.get('DDGNNKAFNFF'))

        # key name: GameTrigger
        if type_dict[type_id] == type:
            if not lut_v.get('AHBLPBNEGFI'):
                return
            sort_index[str(lut_k)] = {
                "itemFileID": int(lut_v['fileID']),
                "voiceType": str(type),
                "gameTriggerArgs": int(lut_v['AHBLPBNEGFI'])
            }

    def lut_index_item(self, lut_part: dict, item_part: dict):
        """
        根据输入的 Lut.json 索引到对应的 vo_item，其中包含了 sourceFileName 字段；\n
        此方法用于已经在 main 中完成的 type 分类拣选的 Lut 字典；
        - lut_part 需要进行索引的已分类 Lut 字典；
        - item_part 索引结果输出字典，此变量应该是一个空字典
        """

        for v in lut_part.values():
            vo_id = v.get('gameTriggerArgs')
            vo_type = v.get('voiceType')
            if vo_id in self.vo_item:
                if vo_type in self.vo_item[vo_id]:
                    item_part.update({
                        vo_id: self.vo_item[vo_id][vo_type]
                    })
                    del self.vo_item[vo_id][vo_type]
            else:
                continue

    def input_json(self, relative_path: str):
        """
        用于读取 json 文件
        - relative_path 是 git repo 目录下文件的相对路径
        """
        absolute_path = os.path.join(self.path, relative_path)
        with open(absolute_path, encoding="utf-8") as f:
                json_decode = json.load(f)
        return json_decode

    def output_json(self, absolute_path: str, output_dict: dict):
        """
        用于输出 json 文件
        - absolute_path 是输出 json 的绝对路径
        - output_dict 是要导出的字典
        """
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

    GenshinVoice(args.source, args.dest, args.lang).main()
