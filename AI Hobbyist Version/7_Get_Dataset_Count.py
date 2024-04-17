import os, csv, wave, argparse
from tqdm import tqdm
from glob import glob

parser = argparse.ArgumentParser(description='统计指定目录下所有的文件夹中的wav数量，wav总时长，lab标注数量，并写入csv表格')
parser.add_argument('-src','--input_path', type=str, help='源目录')
parser.add_argument('-dst','--output_path', type=str, help='csv输出目录')
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
    "无需处理语音": [],
    "战斗语音": [],
    "怪物语音": [],
    "其它语音": [],
    "带变量语音": [],
    "多人对话": [],
    "总语音数量": [],
    "总标注数量": [],
    "总语音时长": []  # 新增总语音时长列
}

# 遍历数据集文件夹
for dirs in tqdm(src,desc = "总进度", dynamic_ncols = True, leave = True):
    spk = os.path.basename(dirs)
    wavs,labs,durs = get_numbers(dirs)
    stats["说话人"].append(os.path.basename(dirs))
    stats["无需处理语音"].append(f"{wavs} | {labs} | {dur(durs)}")
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
    stats["战斗语音"].append(f"{b_wavs} | {b_labs} | {dur(b_durs)}")
    stats["怪物语音"].append(f"{m_wavs} | {m_labs} | {dur(m_durs)}")
    stats["其它语音"].append(f"{o_wavs} | {o_labs} | {dur(o_durs)}")
    stats["带变量语音"].append(f"{p_wavs} | {p_labs} | {dur(p_durs)}")
    stats["多人对话"].append(f"{c_wavs} | {c_labs} | {dur(c_durs)}")
    stats["总语音数量"].append(t_wavs)
    stats["总标注数量"].append(t_labs)
    stats["总语音时长"].append(dur(int(t_durs)))
    
# 写入CSV文件
csv_file = args.output_path
with open(csv_file, "w", newline="",encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=stats.keys())
    writer.writeheader()
    for i in range(len(stats["说话人"])):
        writer.writerow({key: stats[key][i] for key in stats.keys()})

print(f"已生成CSV文件：{csv_file}")
