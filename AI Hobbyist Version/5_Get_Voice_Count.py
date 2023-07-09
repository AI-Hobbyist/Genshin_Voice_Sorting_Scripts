import os
import csv
import argparse
import tqdm as tq

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, help='已整理数据集目录', required=True)
parser.add_argument('--dest', type=str, help='目标路径', required=True)
args = parser.parse_args()

path = str(args.source)
dest = str(args.dest)

def count_files(path,csv_path):
    c_path = csv_path + '/' + '有效语音数量.csv'
    with open(c_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['角色', '语音数量'])
        for root, dirs, files in tq.tqdm(os.walk(path)):
            wav_files = [f for f in files if f.endswith('.wav')]
            writer.writerow([os.path.basename(root), len(wav_files)])

count_files(path,dest)