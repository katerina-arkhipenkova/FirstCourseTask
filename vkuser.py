import time
import requests
import datetime
from tqdm import tqdm
from pprint import pprint


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_user(self, user_screen_name=None):
        user_url = self.url + 'users.get'
        user_params = {
            'user_ids': user_screen_name
        }
        res = requests.get(user_url, params={**self.params, **user_params})
        res.raise_for_status()
        if res.status_code != 200:
            print('Ошибка при получении id пользователя!')
        return res.json()

    def get_photos(self, user_id=None, album_id='profile', count=5):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id,
            'album_id': album_id,
            'extended': 1,
            'photo_sizes': 1,
            'count': count,
            'rev': 1
        }
        res = requests.get(photos_url, params={**self.params, **photos_params})
        res.raise_for_status()
        if res.status_code != 200:
            print('Ошибка при получении фотографий пользователя!')
        return res.json()

    def get_photos_list(self, user_id=None, album_id='profile', count=5):
        photos_json = self.get_photos(user_id, album_id, count)
        photos_list = []
        with tqdm(total=count) as pbar:
            for item in photos_json['response']['items']:
                max_size_photo = item['sizes'][-1]
                for size in item['sizes']:
                    if size['type'] == 'w':
                        max_size_photo = size
                max_size_photo['likes'] = item['likes']['count']
                max_size_photo['date'] = item['date']
                photos_list.append(max_size_photo)
                pbar.set_description('Скачивание фотографий с VK')
                time.sleep(0.01)
                pbar.update(1)
        return photos_list

    def upload_photos_to_disk(self, photos_list):
        photos_on_disk_list = []
        for photo in photos_list:
            photo_on_disk = {}
            file_path = str(photo['likes']) + '.jpg'
            for p in photos_on_disk_list:
                if str(photo['likes']) + '.jpg' in p.values():
                    time_value = datetime.datetime.fromtimestamp(photo['date'])
                    file_path = str(photo['likes']) + '-' + time_value.strftime('%Y-%m-%d-%H-%M-%S') + '.jpg'

            photo_on_disk['file_name'] = file_path
            photo_on_disk['size'] = photo['type']
            photo_on_disk['url'] = photo['url']
            photos_on_disk_list.append(photo_on_disk)
        return photos_on_disk_list
