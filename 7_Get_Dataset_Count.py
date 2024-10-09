import os, csv, wave, argparse
from tqdm import tqdm
from glob import glob

parser = argparse.ArgumentParser(description='统计指定目录下所有的文件夹中的wav数量，wav总时长，lab标注数量，并写入csv表格')
parser.add_argument('-src','--input_path', type=str, default="./Data/second_sorted")
parser.add_argument('-dst','--output_path', type=str, help='csv输出目录', required=True)
args = parser.parse_args()

# 数据集文件夹路径
dataset_folder = args.input_path
src = glob(f"{dataset_folder}/*")

def calculate_total_duration(file_dir):
    total_duration = 0
    wav_files = file_dir
    for wav_path in tqdm(wav_files,desc="正在计算时长",leave = False,position = 1):
        with wave.open(wav_path, 'rb') as f:
            frames = f.getnframes()
            frame_rate = f.getframerate()
            duration = frames / float(frame_rate)
            total_duration += duration
    return total_duration

def dur(sec):
    hours, remainder = divmod(sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{int(milliseconds):03d}"

def get_numbers(path):
    wav_path = glob(f"{path}/*.wav")
    wav_dur = calculate_total_duration(wav_path)
    wav_num = len(glob(f"{path}/*.wav"))
    lab_num = len(glob(f"{path}/*.lab"))
    return wav_num,lab_num,wav_dur

# 初始化统计字典
stats = {
    "说话人": [],
    "无需处理语音数量": [],
    "无需处理标注数量": [],
    "无需处理语音时长": [],
    "总语音数量": [],
    "总标注数量": [],
    "总语音时长": [],
    "|": [],
    "战斗语音数量": [],
    "战斗语音标注数量": [],
    "战斗语音总时长": [],
    "怪物语音数量": [],
    "怪物语音标注数量": [],
    "怪物语音总时长": [],
    "其它语音数量": [],
    "其它语音标注数量": [],
    "其它语音总时长": [],
    "带变量语音数量": [],
    "带变量语音标注数量": [],
    "带变量语音总时长": [],
    "多人对话语音数量": [],
    "多人对话语音标注数量": [],
    "多人对话语音总时长": []
}

stats_total = {
    
}

# 遍历数据集文件夹
for dirs in tqdm(src,desc = "总进度", dynamic_ncols = True, leave = True):
    spk = os.path.basename(dirs)
    wavs,labs,durs = get_numbers(dirs)
    stats["说话人"].append(os.path.basename(dirs))
    b_audio = f"{dirs}/战斗语音 - Battle"
    m_audio = f"{dirs}/怪物语音 - Monster"
    o_audio = f"{dirs}/其它语音 - Others"
    p_audio = f"{dirs}/带变量语音 - Placeholder"
    c_audio = f"{dirs}/多人对话 - Conversation"
    if os.path.exists(b_audio):
        b_wavs,b_labs,b_durs = get_numbers(b_audio)
    else:
        b_wavs = b_labs = b_durs = 0 
    if os.path.exists(m_audio):
        m_wavs,m_labs,m_durs = get_numbers(m_audio)
    else:
        m_wavs = m_labs = m_durs = 0
    if os.path.exists(o_audio):
        o_wavs,o_labs,o_durs = get_numbers(o_audio)
    else:
        o_wavs = o_labs = o_durs = 0
    if os.path.exists(p_audio):
        p_wavs,p_labs,p_durs = get_numbers(p_audio)
    else:
        p_wavs = p_labs = p_durs = 0
    if os.path.exists(c_audio):
        c_wavs,c_labs,c_durs = get_numbers(c_audio)
    else:
        c_wavs = c_labs = c_durs = 0
    t_wavs = wavs + b_wavs + m_wavs + o_wavs + p_wavs + c_wavs
    t_labs = labs + b_labs + m_labs + o_labs + p_labs + c_labs
    t_durs = durs + b_durs + m_durs + o_durs + p_durs + c_durs

    stats["无需处理语音数量"].append(wavs)
    stats["无需处理标注数量"].append(labs)
    stats["无需处理语音时长"].append(dur(durs))
    stats["总语音数量"].append(t_wavs)
    stats["总标注数量"].append(t_labs)
    stats["总语音时长"].append(dur(t_durs))   
    stats["|"].append(f"|")
    stats["战斗语音数量"].append(b_wavs)
    stats["战斗语音标注数量"].append(b_labs)
    stats["战斗语音总时长"].append(dur(b_durs))
    stats["怪物语音数量"].append(m_wavs)
    stats["怪物语音标注数量"].append(m_labs)
    stats["怪物语音总时长"].append(dur(m_durs))
    stats["其它语音数量"].append(o_wavs)
    stats["其它语音标注数量"].append(o_labs)
    stats["其它语音总时长"].append(dur(o_durs))
    stats["带变量语音数量"].append(p_wavs)
    stats["带变量语音标注数量"].append(p_labs)
    stats["带变量语音总时长"].append(dur(p_durs))
    stats["多人对话语音数量"].append(c_wavs)
    stats["多人对话语音标注数量"].append(c_labs)
    stats["多人对话语音总时长"].append(dur(c_durs))
    
# 写入CSV文件
csv_file = args.output_path
with open(csv_file, "w", newline="",encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=stats.keys())
    writer.writeheader()
    for i in range(len(stats["说话人"])):
        writer.writerow({key: stats[key][i] for key in stats.keys()})

print(f"已生成CSV文件：{csv_file}")
