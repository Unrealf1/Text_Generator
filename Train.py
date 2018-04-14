import re
import os
import argparse
import sys
import shutil

# COMMIT_COUNTER stands for amount of symbols we are ready to store in RAM
COMMIT_TRIGGER = 100000
# PRINT_TRIGGER stands for amount commits during one file to print, tht program is still working
PRINT_TRIGGER = 5


# This function inserts one pair of words(first, second) into the current data correctly
def insert_pair(first, second, current_data):
    if first == "aux" or second == "aux":
        return
    if (first, second) in current_data:
        current_data[(first, second)] += 1
    else:
        current_data[(first, second)] = 1


# This function inserts word(second because it is going after the word
# specified in filename) and its amount into current_data
def insert_pair_compress(second, value, current_data):
    if second in current_data:
        current_data[second] += int(value)
    else:
        current_data[second] = int(value)


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


# This is the analog of commit, but it's faster, because it works only with one file
def compress_commit(current_data, file_path):
    file = open(file_path, 'w')
    for I in current_data:
        file.write(I + ' ' + str(current_data[I]) + '\n')
    file.close()


# This function compresses data: after Train() there are many pairs stated in
# same file several times. So compress() unites them in one
def compress(model_path):
    fl_list = os.listdir(model_path)
    for fl_name in fl_list:
        fl = open(os.path.join(model_path, fl_name))
        current_data = dict()
        for line in fl:
            line = line.split()
            insert_pair_compress(line[0], line[1], current_data)
        compress_commit(current_data, os.path.join(model_path, fl_name))
        fl.close()
        


# This is the main function of the file. It reads all files and creates model
def train(model_path, input_paths, is_lower):
    if os.path.exists(model_path):
        print("Deleting old model...")
        if os.path.isfile(model_path):
            os.remove(model_path)

        elif os.path.isdir(model_path):
            shutil.rmtree(model_path)

    os.mkdir(model_path)
    current_data = dict()

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
                    insert_pair(prev, word, current_data)
                    prev = word
            if commit_counter >= COMMIT_TRIGGER:
                print_counter += 1
                commit_counter = 0
                commit(current_data, model_path)
                current_data = dict()
                if print_counter == PRINT_TRIGGER:
                    print_counter = 0
                    print(cur, ' work in progress...')
        input_file.close()
        commit(current_data, model_path)
        current_data = dict()
        if cur != sys.stdin:
            print("Trained " + cur)
    print("Train successful")
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

    args = parser.parse_args(input().split())

    if args.input_dir is None:
        train(args.model, sys.stdin, args.lc)
    else:
        files = os.listdir(args.input_dir)
        files = list(map(lambda x: os.path.join(args.input_dir, x), files))
        txt = filter(lambda x: x.endswith('.txt'), files)
        train(args.model, txt, args.lc)
