import argparse
import numpy
import os
import sys


DEFAULT_NEW_LINE_TRIGGER = 50


# this function generate random word from all in model
def generate_random_word(model):
    # model is a path to model, given by user
    return numpy.random.choice(os.listdir(model))[:-len('.w')]


# this function generate random word from .w file given
def choose_next_word(word_file_name):
    # word_file_name is a path to .w file related to the word
    # we are generating successor for

    if os.path.exists(word_file_name) and os.path.isfile(word_file_name):
        # reading file
        word_file = open(word_file_name, 'r', encoding="utf8")
        sm = 0
        poss_word = list()
        possibility = list()

        # initializing poss_word and possibility
        for word_number in word_file:
            tmp = word_number.split()
            poss_word.append(tmp[0])
            possibility.append(int(tmp[1]))
            sm += int(tmp[1])

        # normalization of possibility
        for i in range(len(possibility)):
            possibility[i] = possibility[i] / sm

        word_file.close()
        # choosing next word
        return numpy.random.choice(poss_word, p=possibility)
    else:
        return None


# This function initialize parser
def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", action="store",
                        help="model file path", required=True)
    parser.add_argument("-s", "--seed", action="store",
                        help="initial word")
    parser.add_argument("-l", "--length", action="store",
                        help="lengs of text in words")
    parser.add_argument("-o", "--output", action="store",
                        help="output file path")
    parser.add_argument("-p", "--paragraph", action="store",
                        help="length of paragraph. Default:%d" % DEFAULT_NEW_LINE_TRIGGER)
    return parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()

    if not os.path.exists(args.model) or os.path.isfile(args.model):
        print("Error: Can't open model!")

    if args.output is not None:
        sys.stdout = open(args.output, 'w', encoding="utf8")

    new_line_trigger = DEFAULT_NEW_LINE_TRIGGER
    if args.paragraph is not None:
        new_line_trigger = int(args.paragraph)

    # start of text generation
    cur_word = args.seed
    counter = int(args.length)
    to_print = list()

    for i in range(counter):
        if cur_word is None:
            # generate random word
            cur_word = generate_random_word(args.model)

        if (i + 1) % new_line_trigger == 0:
            for word in to_print:
                print(word, end=' ')
            print()
            to_print = list()

        # printing another word
        to_print.append(cur_word)

        cur_word = choose_next_word(os.path.join(args.model, cur_word) + ".w")

    for word in to_print:
        print(word, end=' ')
    if args.output is not None:
        sys.stdout.close()
