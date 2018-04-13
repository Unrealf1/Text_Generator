import argparse
import random
import numpy
import os

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", action="store",
                    help="model file path", required="true")
parser.add_argument("-s", "--seed", action="store",
                    help="initial word")
parser.add_argument("-l", "--length", action="store",
                    help="lengs of text in words")
parser.add_argument("-o", "--output", action="store",
                    help="output file path")
					
args = parser.parse_args(input().split())
    
if not os.path.exists(args.model) or os.path.isfile(args.model):
    print("Error: Can't open model!")       

cur_word = args.seed
counter = int(args.length)
while counter > 1:
    if cur_word is None:
            word_list = os.listdir(args.model)
            cur_word = numpy.random.choice(word_list)
            print()
    counter -= 1
    print(cur_word, end=' ')
    word_file_name = os.path.join(args.model, cur_word)
    if os.path.exists(word_file_name) and os.path.isfile(word_file_name):
        word_file = open(word_file_name, 'r')
        sm = 0
        poss_word = list()
        possibility = list()
        for I in word_file:
            tmp = I.split()
            poss_word.append(tmp[0])
            possibility.append(tmp[1])
            sm += int(tmp[1])
        
        for i in range (len(possibility)):
            possibility[i] = int(possibility[i]) / sm

        cur_word = numpy.random.choice(poss_word, p=possibility)
            
    else:
        cur_word = None
    
print()

