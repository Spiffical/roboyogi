#!/usr/bin/python

# This script is a modified example from
# https://developers.google.com/youtube/v3/docs/search/list
# It executes a search request for the specified search term,
# which in this case is going to be 'yoga'.
# Sample usage:
#   python search_yt_vids.py --q=yoga --max-results=25
# NOTE: To use this script, you must provide a developer key obtained
#       in the Google APIs Console. Search for "REPLACE_ME" in this code
#       to find the correct place to provide that key..

import argparse
import os.path
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'REPLACE_ME'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  nextPageToken = ''
  new_data = []
  for i in range(options.pages):
      # Call the search.list method to retrieve results matching the specified
      # query term.
      search_response = youtube.search().list(
        q=options.q,
        part='id,snippet',
        maxResults=options.max_results,
        type=options.type,
        videoCaption=options.caption,
        videoDuration=options.duration,
        pageToken=nextPageToken
      ).execute()

      # Add each result to data list
      for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
          new_data.append({'title': search_result['snippet']['title'],
                           'id': search_result['id']['videoId'],
                           'channelId': search_result['snippet']['channelId'],
                           'channelTitle': search_result['snippet']['channelTitle']})
        else:
          print('script requires videos, not playlists or channels')

      try:
        nextPageToken = search_response['nextPageToken']
      except KeyError:
        break

  # Save the new data into a JSON file
  txt_file = 'yoga_videos.txt'
  if os.path.isfile(txt_file):  # Merge two lists if file already exists
      with open(txt_file) as json_file:
          json_data = json.load(json_file)
          json_ids = [item['id'] for item in json_data]
          for vid in new_data:
              if vid['id'] in json_ids:
                  continue
              else:
                  json_data.append(vid)
  else:
      json_data = new_data

  with open(txt_file, 'w') as outfile:
      json.dump(json_data, outfile, indent=4)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--q', help='Search term', default='Google')
  parser.add_argument('--max-results', help='Max results', default=50)
  parser.add_argument('--type', help='Type of result', default='video')
  parser.add_argument('--caption', help='Type of captioning', default='closedCaption')  # Want only good captions
  parser.add_argument('--duration', help='Length of video', default='long')  # More likely yoga routines if long
  parser.add_argument('--pages', help='Number of pages to return', default=10, type=int)
  args = parser.parse_args()

  try:
    youtube_search(args)
  except HttpError as e:
    print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))

