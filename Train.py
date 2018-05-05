import re
import os
import argparse
import sys
import shutil
import collections


# value of commit trgger, if not given from user
DEFAULT_COMMIT_TRIGGER = 10000000


# This function checks if pair given is correct
def correct_pair(first, second):
    # first - first word in pair;
    # second - second word in pair
    return not (first == "aux" or second == "aux"
                or first == "prn" or second == "prn")


# This function commits new word pairs from current_data to model on the disc
def commit(current_data, model_path):
    # current_data is a dict of pairs of words and their number
    # model_path is a path to model, given by user
    current_data_keys = sorted(current_data.keys())
    cur_file = None
    file = None
    for word_pair in current_data_keys:
        if not cur_file == word_pair[0]:
            cur_file = word_pair[0]
            if file is not None:
                file.close()
            file = open(os.path.join(model_path, word_pair[0] + ".w"), 'a')
        file.write(word_pair[1] + ' ' + str(current_data[word_pair]) + '\n')


# This is the analog of commit, but it's faster, because it works only with
# one file
def compress_commit(compress_data, file_path):
    # compress_data is a dict of words and their number
    # file_path is a path to file(word name + '.w') we are going to write in
    file = open(file_path, 'w')
    for word in compress_data:
        file.write(word + ' ' + str(compress_data[word]) + '\n')
    file.close()


# This function compresses data: after Train() there are many pairs stated in
# same file several times. So compress() unites them in one
def compress(model_path, words_changed):
    # model_path is a path to model, given by user
    # unique_words is set of words changed during this session


    word_cnt = 0
    print("Have %d files to compress" % len(words_changed))
    for word in words_changed:
        word_cnt += 1
        fl_name = word + '.w'

        to_print = "[%d%%] " % (word_cnt * 100 // len(words_changed)) + fl_name
        sys.stdout.flush()
        print("\r" + to_print, end=" ")

        fl = open(os.path.join(model_path, fl_name))
        compress_data = collections.defaultdict(int)
        for line in fl:
            line = line.split()
            compress_data[line[0]] += int(line[1])
        compress_commit(compress_data, os.path.join(model_path, fl_name))
        fl.close()
        print(" "*len(to_print), end=" ")
    print()


# This function change line, so Train can correctly work with it
def line_processing(list_line, is_lower):
    # list_line is a list of one string, function is going to change
    # is_lower is used to determine if all words have to be lowercase or not
    if is_lower:
        list_line[0] = list_line[0].lower()
    list_line[0] = re.sub('\\d', ' ', list_line[0])
    list_line[0] = re.sub('_', ' ', list_line[0])
    list_line[0] = re.findall(r"[\w']+", list_line[0])


# This function reads file and commits changes to the model
def read_file(input_file, is_lower, model_path, triggers, unique_words):
    # model_path is a path to model, given by user
    # input_file is a file function is going to read
    # is_lower is used to determine if all words have to be lowercase or not
    # triggers is a dict of all triggers
    # unique_words is set of words changed during this session

    current_data = collections.defaultdict(int)

    # Reading current file
    commit_counter = 0
    print_counter = 0
    prev = None
    for line in input_file:
        commit_counter += len(line)

        list_line = [line]
        line_processing(list_line, is_lower)
        line = list_line[0]

        for word in line:
            if prev is None:
                prev = word
            else:
                if correct_pair(prev, word):
                    unique_words.add(prev)
                    current_data[(prev, word)] += 1
                prev = word

        # Check if should commit yet
        if commit_counter >= triggers['commit']:
            print_counter += 1
            commit_counter = 0
            commit(current_data, model_path)
            current_data = collections.defaultdict(int)
            # Check if should print yet
            if print_counter == triggers['print']:
                print_counter = 0
                print('.', end="")
                sys.stdout.flush()

    commit(current_data, model_path)


# This is the main function of the file. It reads all files and creates model
def train(model_path, input_paths, is_lower, if_compress, if_delete, triggers):
    # model_path is a path to model, given by user
    # input_path is a path to input directory, given by user
    # is_lower is used to determine if all words have to be lowercase or not
    # if_compress is used to determine if data will be compressed or not
    # if_delete is used to determine if old model should be erased
    # triggers is a dict of all triggers

    # Opening model
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

    if input_paths == sys.stdin:
        input_paths = [sys.stdin]

    # Reading each file
    unique_words = set()
    path_cnt = 0
    for cur in input_paths:
        if cur == sys.stdin:
            input_file = cur
        else:
            # open file and print message
            path_cnt += 1
            input_file = open(cur, "r")
            print("[%d/%d] " % (path_cnt, len(input_paths)), end=" ")
            print("Processing " + cur)

            # read file
            read_file(input_file, is_lower, model_path, triggers, unique_words)

            # Closing current file
            input_file.close()
        sys.stdout.flush()

    # Trained all files in input directory
    print("Train successful")

    # Compressing files
    if if_compress:
        print("Compressing data...")
        compress(model_path, unique_words)
        print("Compressed successful")


# This function initialize triggers
def init_triggers(commit_trigger_, triggers_dict):
    # commit_trigger_ is a commit_trigger given by user
    # triggers_dict is a dict of all triggers
    if commit_trigger_ is not None:
        triggers_dict['commit'] = int(commit_trigger_)
    # calculation of print_trigger
    triggers_dict['print'] = (max(DEFAULT_COMMIT_TRIGGER // triggers_dict['commit'], 1))


# This function initialize parser
def init_parser():
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
    parser.add_argument("-c_t", "--commit_trigger", action="store",
                        help='higher - faster program works, but more memory '
                             'it uses. Default: %d' % DEFAULT_COMMIT_TRIGGER)
    return parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args(input().split())

    triggers = {"commit": DEFAULT_COMMIT_TRIGGER, 'print': 1}
    # commit_trigger stands for amount of symbols we are able to store in RAM
    # print_trigger stands for amount commits during one file to print that
    # program is still working
    init_triggers(args.commit_trigger, triggers)

    if args.input_dir is None:
        train(args.model, sys.stdin, args.lc,
              not args.nc, not args.add, triggers)
    else:
        files = os.listdir(args.input_dir)
        files = list(map(lambda x: os.path.join(args.input_dir, x), files))
        txt = list(filter(lambda x: x.endswith('.txt'), files))
        train(args.model, txt, args.lc, not args.nc, not args.add, triggers)
