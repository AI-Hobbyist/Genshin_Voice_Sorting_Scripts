import os
import csv
from pydub import AudioSegment
from tqdm import tqdm
import argparse
import datetime

def get_wav_info(path):
    wav_files = []
    total_duration = 0
    lab_files = []
    for root, dirs, files in os.walk(path):
        folder =  os.path.basename(root)
        for file in tqdm(files,leave=False,desc=f"正在统计目录 [{folder}] 的数据时长",unit=" files"):
            if file.endswith('.wav'):
                wav_files.append(os.path.join(root, file))
                total_duration += AudioSegment.from_file(os.path.join(root, file)).duration_seconds
            elif file.endswith('.lab'):
                lab_files.append(os.path.join(root, file))
    total_duration = str(datetime.timedelta(milliseconds=round(total_duration * 1000)))
    return wav_files, total_duration, len(wav_files), len(lab_files)

def write_csv(path, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['角色名', '总时长(时:分:秒.毫秒)', '音频数量', '标注数量'])
        for root, dirs, files in os.walk(path):
            for dir in tqdm(dirs,position=1,dynamic_ncols=True,leave=False,desc=f"当前统计进度"):
                wav_files, total_duration, wav_count, lab_count = get_wav_info(os.path.join(root, dir))
                writer.writerow([dir, total_duration, wav_count, lab_count])
                tqdm.write(f"说话人：{dir} | 音频时长：{total_duration} | 音频数量：{wav_count} | 标注数量：{lab_count}\n-------------------------------------------")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='统计指定目录下所有的文件夹中的wav数量，wav总时长，lab标注数量，并写入csv表格')
    parser.add_argument('-src','--input_path', type=str, help='源目录')
    parser.add_argument('-dst','--output_path', type=str, help='csv输出目录')
    args = parser.parse_args()
    write_csv(args.input_path, args.output_path)