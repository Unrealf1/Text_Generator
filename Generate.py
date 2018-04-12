import sqlite3
import argparse
import random
import numpy

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
         return c
      upto += w
   return None



parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", action="store",
                    help="model file path", required="true")
parser.add_argument("-s", "--seed", action="store",
                    help="initial word")
parser.add_argument("-l", "--length", action="store",
                    help="lengs of text in words")
parser.add_argument("-o", "--output", action="store",
                    help="output file path")
#args = parser.parse_args(input().split())
param = open("gen_param.txt")
args = parser.parse_args(param.read().split())
param.close()
try:
    file = open(args.model)
except IOError as e:
    file.close()
    print("Error: Can't open model!")
else:
    conn = sqlite3.connect(args.model)
    cursor = conn.cursor()

cur_word = args.seed
counter = int(args.length)
while counter > 1:
    if cur_word is None:
            sql = "SELECT COUNT(first) FROM dictionary "
            cnt = cursor.execute(sql).fetchall()
            rnd = int(random.uniform(0, cnt[0][0]-1))
            sql = "SELECT first FROM dictionary"
            cur_word = (cursor.execute(sql).fetchall())
            cur_word = cur_word[rnd % len(cur_word)][0]
            print()
    counter -= 1
    print(cur_word, end=' ')
    sql = "SELECT second, amount FROM dictionary WHERE first = ?"
    cursor.execute(sql, [(cur_word)])
    poss = cursor.fetchall()
    poss0 = [i[0] for i in poss]
    poss1 = [i[1] for i in poss]
    sm = 0
    for i in poss1:
        sm += i

    for i in range (len(poss1)):
        poss1[i] /= sm

    cur_word = numpy.random.choice(poss0, p=poss1)
print()

