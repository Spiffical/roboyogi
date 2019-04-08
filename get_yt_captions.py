#!/usr/bin/python

# This script takes a JSON file with youtube video metadata and scrapes diycaptions.com
# to generate a csv file containing the captions of the videos and info about the captions
# Sample usage:
#   python get_yt_captions.py data/youtube_videos.txt data/yoga_captions.csv

import csv
import argparse
import json
import os.path
from bs4 import BeautifulSoup
from requests_retry import get_response
from time import sleep


def collect_captions(video_data, output_file):

    with open(video_data) as json_file:
        json_data = json.load(json_file)

    for vid in json_data:

        vid_id = vid['id']
        channel_id = vid['channelId']
        channel_title = vid['channelTitle']

        # Sometimes running this script multiple times is necessary because scraping
        # diycaptions.com fails for various reasons. Therefore check if caption of video
        # ID has already been retrieved
        if os.path.isfile(output_file):
            with open(output_file, 'r') as csv_file:
                readCSV = csv.reader(csv_file, delimiter=',')
                analyzed_ids = [row[0] for row in readCSV]
                if vid_id in analyzed_ids:
                    print('Already have caption for: %s' % vid_id)
                    continue

        # Specify the diycaptions url
        url = 'http://diycaptions.com/php/get-automatic-captions-as-txt.php?id=%s&language=en' % vid_id

        response = get_response(url)
        if response.status_code == 503:
            sleep(5)  # Sleep to avoid 'Resource Limit is Reached' error (508)
            continue

        # parse the html using beautiful soup and store in variable `soup`
        soup = BeautifulSoup(response.content, 'html.parser')

        # get all the information needed
        hyperinfo_box = soup.find('div', attrs={'class': 'well'})

        # take out the youtube captions from the <div contenteditable="true">
        try:
            caption_box = hyperinfo_box.find('div', attrs={'contenteditable': 'true'})
            caption = caption_box.text.strip().replace(' \n', ' ').replace('\n', ' ')
        except:
            print('No caption available: %s' % url)
            sleep(3)  # Sleep to avoid 'Resource Limit is Reached' error (508)
            continue

        if caption[:2] == '- ':
            caption = caption[2:]

        # retrieve the character count and duration (seconds)
        char_count = int(hyperinfo_box.findAll('b')[0].next_sibling.replace("|", ""))
        duration = int(hyperinfo_box.findAll('b')[1].next_sibling.replace("|", ""))

        # write to csv file
        with open(output_file, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([vid_id, char_count, duration, caption, channel_id, channel_title])

        sleep(3)  # Sleep to avoid 'Resource Limit is Reached' error (508)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_metadata_file', help='JSON formatted file containing video metadata', type=str)
    parser.add_argument('output_file', help='name of output file containing captions', type=str)
    args = parser.parse_args()

    input_file_name = args.video_metadata_file
    output_file_name = args.output_file

    collect_captions(input_file_name, output_file_name)
