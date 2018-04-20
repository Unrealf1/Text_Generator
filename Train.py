import re
import os
import argparse
import sys
import shutil
import collections

# COMMIT_COUNTER stands for amount of symbols we are ready to store in RAM
COMMIT_TRIGGER = 100000
# PRINT_TRIGGER stands for amount commits during one file to print that
# program is still working
PRINT_TRIGGER = 5


# This function checks if pair given is correct
def correct_pair(first, second):
    if first == "aux" or second == "aux":
        return False
    return True


# This function commits new word pairs from current_data to model on the disc
def commit(current_data, model_path):
    current_data_keys = sorted(current_data.keys())
    cur_file = None
    file = None
    for I in current_data_keys:
        if not cur_file == I[0]:
            cur_file = I[0]
            if file is not None:
                file.close()
            file = open(os.path.join(model_path, I[0] + ".w"), 'a')
        file.write(I[1] + ' ' + str(current_data[I]) + '\n')


# This is the analog of commit, but it's faster, because it works only with
# one file
def compress_commit(compress_data, file_path):
    file = open(file_path, 'w')
    for I in compress_data:
        file.write(I + ' ' + str(compress_data[I]) + '\n')
    file.close()


# This function compresses data: after Train() there are many pairs stated in
# same file several times. So compress() unites them in one
def compress(model_path):
    fl_list = os.listdir(model_path)
    for fl_name in fl_list:
        fl = open(os.path.join(model_path, fl_name))
        compress_data = collections.defaultdict(int)
        for line in fl:
            line = line.split()
            compress_data[line[0]] += int(line[1])
        compress_commit(compress_data, os.path.join(model_path, fl_name))
        fl.close()


# This is the main function of the file. It reads all files and creates model
def train(model_path, input_paths, is_lower, if_compress, if_delete):
    if os.path.exists(model_path):
        if os.path.isfile(model_path):
            print("Deleting file i place of model...")
            os.remove(model_path)
            os.mkdir(model_path)
        elif os.path.isdir(model_path):
            if if_delete:
                print("Deleting old model...")
                shutil.rmtree(model_path)
                os.mkdir(model_path)
            else:
                print("Found old model")
    else:
        os.mkdir(model_path)

    sys.stdout.flush()
    current_data = collections.defaultdict(int)

    if input_paths == sys.stdin:
        input_paths = [sys.stdin]
    path_cnt = 0
    for cur in input_paths:
        if cur == sys.stdin:
            input_file = cur
        else:
            path_cnt += 1
            input_file = open(cur, "r")
            print("[%d/%d] " % (path_cnt, len(input_paths)), end=" ")
            print("Processing " + cur, end=" ")
        sys.stdout.flush()
        commit_counter = 0
        print_counter = 0
        prev = None
        for line in input_file:
            commit_counter += len(line)
            if is_lower:
                line = line.lower()
            line = re.sub('\\d', ' ', line)
            line = re.sub('_', ' ', line)
            line = re.findall(r"[\w']+", line)
            for word in line:
                if prev is None:
                    prev = word
                else:
                    if correct_pair(prev, word):
                        current_data[(prev, word)] += 1
                    prev = word
            if commit_counter >= COMMIT_TRIGGER:
                print_counter += 1
                commit_counter = 0
                commit(current_data, model_path)
                current_data = collections.defaultdict(int)
                if print_counter == PRINT_TRIGGER:
                    print_counter = 0
                    print('.', end="")
                    sys.stdout.flush()
        input_file.close()
        commit(current_data, model_path)
        current_data = collections.defaultdict(int)
        if cur != sys.stdin:
            print(end="\r")
            print(" " * 100, end="\r")
            sys.stdout.flush()
    print("Train successful")
    if if_compress:
        print("Compressing data...")
        compress(model_path)
        print("Compressed successful")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", action="store",
                        help="model file path", required=True)
    parser.add_argument("-i", "--input_dir", action="store",
                        help="input directory path")
    parser.add_argument("--lc", action="store_true",
                        help="all text considered lower case")
    parser.add_argument("--nc", action="store_true",
                        help="do not compress data")
    parser.add_argument("--add", action="store_true",
                        help="do not delete old model")

    args = parser.parse_args(input().split())
    if args.input_dir is None:
        train(args.model, sys.stdin, args.lc, not args.nc, args.add)
    else:
        files = os.listdir(args.input_dir)
        files = list(map(lambda x: os.path.join(args.input_dir, x), files))
        txt = list(filter(lambda x: x.endswith('.txt'), files))
        train(args.model, txt, args.lc, not args.nc, not args.add)
