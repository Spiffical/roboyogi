import csv
import json
import numpy as np
import os.path
from bs4 import BeautifulSoup
from requests_retry import get_response
from time import sleep

#video_data = 'yoga_videos.txt'
video_data = 'yogawithtimvids'
save_file = 'yoga_yt_captions2.csv'
vid_ids = np.loadtxt(video_data, dtype=str)
#with open(video_data) as json_file:
#    json_data = json.load(json_file)
#    vid_ids = [item['id'] for item in json_data]

#for vid in json_data:
for vid in vid_ids:

    #vid_id = vid['id']
    #vid_title = vid['title']
    #channel_id = vid['channelId']
    #channel_title = vid['channelTitle']

    vid_id = vid
    vid_title = 'yogawithtimvids'
    channel_id = 'yogawithtimvids'
    channel_title = 'yogawithtimvids'

    # check if caption of video ID has already been retrieved
    if os.path.isfile(save_file):
        with open(save_file, 'r') as csv_file:
            readCSV = csv.reader(csv_file, delimiter=',')
            analyzed_ids = [row[0] for row in readCSV]
            if vid_id in analyzed_ids:
                print('Already have caption for: %s' % vid_id)
                continue

    # specify the url
    url = 'http://diycaptions.com/php/get-automatic-captions-as-txt.php?id=%s&language=en' % vid_id

    response = get_response(url)
    if response.status_code == 503:
        sleep(10)  # Sleep to avoid 'Resource Limit is Reached' error (508)
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
    with open(save_file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([vid_id, char_count, duration, caption, channel_id, channel_title])

    sleep(3)  # Sleep to avoid 'Resource Limit is Reached' error (508)

save_file = 'yoga_yt_captions2.csv'
with open(save_file, 'r') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    with open('subset_captions.txt', 'w') as f:
        for i, row in enumerate(readCSV):
            if i < 100:
                f.write(row[3])
                f.write('\n')

