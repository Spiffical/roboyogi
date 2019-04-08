# Sample usage:
#   python gen_trainingset.py data/yoga_captions.csv data/all_captions_training.txt

import argparse
import csv

def make_text_file(csv_caption_file, output_file):
    with open(csv_caption_file, 'r') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        with open(output_file, 'w') as f:
            for i, row in enumerate(readCSV):
                f.write(row[3])
                f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_caption_file', help='csv file containing caption data', type=str)
    parser.add_argument('output_file', help='name of output text file containing only captions', type=str)
    args = parser.parse_args()

    input_file_name = args.csv_caption_file
    output_file_name = args.output_file

    make_text_file(input_file_name, output_file_name)
