import argparse
import numpy
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", action="store",
                        help="model file path", required=True)
    parser.add_argument("-s", "--seed", action="store",
                        help="initial word")
    parser.add_argument("-l", "--length", action="store",
                        help="lengs of text in words")
    parser.add_argument("-o", "--output", action="store",
                        help="output file path")

    args = parser.parse_args(input().split())

    if not os.path.exists(args.model) or os.path.isfile(args.model):
        print("Error: Can't open model!")

    if args.output is not None:
        out = open(args.output, 'w')

    # start of text generation
    cur_word = args.seed
    counter = int(args.length)
    while counter > 1:
        if cur_word is None:
            # generate random word
            word_list = os.listdir(args.model)
            cur_word = numpy.random.choice(word_list)
            cur_word = cur_word[0:-2]
            if args.output is not None:
                out.write('\n')
            else:
                print()

        # printing another word
        counter -= 1
        if args.output is not None:
            out.write(cur_word + " ")
        else:
            print(cur_word, end=' ')

        # opening file for word written
        word_file_name = os.path.join(args.model, cur_word) + ".w"

        if os.path.exists(word_file_name) and os.path.isfile(word_file_name):
            # reading file
            word_file = open(word_file_name, 'r')
            sm = 0
            poss_word = list()
            possibility = list()

            # initializing poss_word and possibility
            for word_number in word_file:
                tmp = word_number.split()
                poss_word.append(tmp[0])
                possibility.append(tmp[1])
                sm += int(tmp[1])

            # normalization of possibility
            for i in range(len(possibility)):
                possibility[i] = int(possibility[i]) / sm

            # choosing next word
            cur_word = numpy.random.choice(poss_word, p=possibility)
        else:
            cur_word = None

    if args.output is not None:
        out.close()
