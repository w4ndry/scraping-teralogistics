import os
import json
import requests

def get_total_page(url, path, file_name):
    print('getting total page...')

    json_res = requests.get(url).json()

    with open(os.path.join(path, file_name), 'w+') as outfile:
        json.dump(json_res, outfile)

    with open(os.path.join(path, file_name)) as json_file:
        json_data = json.load(json_file)

    total_page = json_data['total_pages']

    print('Done getting total page...')

    return total_page


def get_urls(url, page):
    print('getting urls... page {}'.format(page))

    json_res = requests.get(url).json()

    urls = []
    for item in json_res['items']:
        urls.append(item['link'])

    print('Done getting urls... page {}'.format(page))

    return urls