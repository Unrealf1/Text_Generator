import re
import os
import argparse
import sys
import shutil

MAX_INPUT_SIZE = 20000

def insert_pair(first, second, cursor):
    if first == "aux" or second == "aux":
        return
    if (first, second) in cursor:
        cursor[(first, second)] += 1
    else:
        cursor[(first, second)] = 1

        
def insert_pair_compress(second, value, cursor):
    if (second) in cursor:
        cursor[(second)] += int(value)
    else:
        cursor[(second)] = int(value)

def commit(cursor, model_path):
    cursor_keys = sorted(cursor.keys())
    cur_file = None
    file = None
    for I in cursor_keys:        
        if not cur_file == I[0]:
            cur_file = I[0]
            if not file is None:
                file.close()
            file = open(os.path.join(model_path, I[0] + ".w"), 'a')
        file.write(I[1] + ' ' + str(cursor[I]) + '\n')
    cursor = dict()


def compress_commit(cursor, file_path):
    file = open(file_path, 'w')
    for I in cursor:
        file.write(I + ' ' + str(cursor[I]) + '\n')
    cursor = dict()
        
def compress(model_path):
    fl_list = os.listdir(model_path)
    for fl_name in fl_list:
        fl = open(os.path.join(model_path, fl_name))
        cursor = dict()
        for line in fl:
            line = line.split()
            insert_pair_compress(line[0], line[1], cursor)
        compress_commit(cursor, os.path.join(model_path, fl_name))
            

def train(model_path, input_paths, is_lower):
    if os.path.exists(model_path):
        if os.path.isfile(model_path):
            os.remove(model_path)

        elif os.path.isdir(model_path):
            shutil.rmtree(model_path)

    os.mkdir(model_path)   
    cursor = dict()

    if input_paths == sys.stdin:
        input_paths = [sys.stdin]
    for cur in input_paths:
        if cur == sys.stdin:
            input_file = cur
        else:
            input_file = open(cur, "r")
        commit_counter = 0
        print_counter = 0
        prev = None
        for line in input_file:
            commit_counter += len(line)	
            if is_lower:
                line = line.lower()
            line = re.sub('\d', ' ', line)
            line = re.sub('_', ' ', line)
            line = re.findall(r"[\w']+", line)
            for word in line:
                if prev is None:
                    prev = word
                else:
                    insert_pair(prev, word, cursor)
                    prev = word
            if commit_counter >= MAX_INPUT_SIZE:
                print_counter += 1
                commit_counter = 0
                commit(cursor, model_path)
                cursor = dict()
                if print_counter == 10:
                    print_counter = 0
                    print(cur, ' work in progress...')
        commit(cursor, model_path)
        cursor = dict()
        if cur != sys.stdin:
            print("Trained " + cur)
    print("Train successful")
    print("Compressing data...")
    compress(model_path)
    print("Compressed successful")

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", action="store",
                    help="model file path", required="true")
parser.add_argument("-i", "--input_dir", action="store",
                    help="input directory path")
parser.add_argument("--lc", action="store_true",
                    help="all text concidered lower case")

args = parser.parse_args(input().split())

if args.input_dir is None:
    train(args.model, sys.stdin, args.lc)
else:
    files = os.listdir(args.input_dir)
    files = list(map(lambda x:os.path.join(args.input_dir, x), files))
    txt = filter(lambda x: x.endswith('.txt'), files)
    train(args.model, txt, args.lc)
    
