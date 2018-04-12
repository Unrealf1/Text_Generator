import sqlite3
import re
import os
import argparse
import sys

MAX_INPUT_SIZE = 20000

def insert_pair(first, second, data_base_cursor):
    sql = "SELECT COUNT(*) FROM dictionary WHERE first = ? AND second = ?"
    cnt = data_base_cursor.execute(sql, (first, second)).fetchall()
    if cnt[0][0] == 0:
        data_base_cursor.execute("INSERT INTO dictionary(first, second, amount) VALUES(?, ?, 1)", (first, second))
    else:
        data_base_cursor.execute("UPDATE dictionary SET amount = amount + 1 WHERE first = ? AND second = ?", (first, second))

def train(model_path, input_paths, is_lower):
    try:
        file = open(model_path)
    except IOError as e:
        pass
    else:
        with file:
           file.close()
           os.remove(model_path)

    conn = sqlite3.connect(model_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE dictionary
                     (first text, second text, amount integer)""")
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
                conn.commit()
                if print_counter == 10:
                    print_counter = 0
                    print(cur, ' work in progress...')
        conn.commit()
        if cur != sys.stdin:
            print("Trained " + cur)

    print("Train successful")

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
    