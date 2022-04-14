import time
import requests
import json
import os
from tqdm import tqdm


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

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
            r = requests.get(photo['url'])
            disk_file_path = str(photo['date']) + '.jpg'
            photo_on_disk['file_name'] = disk_file_path
            photo_on_disk['size'] = photo['type']
            photos_on_disk_list.append(photo_on_disk)
            with open(disk_file_path, "wb") as code:
                code.write(r.content)
        return photos_on_disk_list


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def upload_link(self, disk_file_path: str):
        disk_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': disk_file_path, 'overwrite': 'true'}
        response = requests.get(disk_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, filename: str, folder_name=""):
        href = self.upload_link(disk_file_path=folder_name + filename).get("href", "")
        response = requests.put(href, data=open(filename, "rb"))
        response.raise_for_status()
        if response.status_code != 201:
            print('Ошибка при загрузке файла на Яндекс.Диск!')

    def new_folder(self, folder_name: str):
        disk_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': folder_name, 'overwrite': 'true'}
        response = requests.put(disk_url, headers=headers, params=params)
        return response.json()

if __name__ == '__main__':
    with open('tokenVK.txt', 'r') as file_object:
        tokenVK = file_object.read().strip()

    vk_client = VkUser(tokenVK, '5.131')
    album_id = 'profile'
    count_photos = 5
    vk_photos_list = vk_client.get_photos_list(552934290, album_id, count_photos)
    photos_list = vk_client.upload_photos_to_disk(vk_photos_list)
    with open('tokenYaD.txt', 'r') as file_object:
        tokenYaD = file_object.read().strip()

    uploader = YaUploader(tokenYaD)
    folder_name = 'LoadedPhotos/'
    uploader.new_folder(folder_name)
    with tqdm(total=len(photos_list)) as pbar:
        for photo in photos_list:
            pbar.set_description("Загрузка фотографий на Яндекс.Диск")
            uploader.upload_file_to_disk(photo['file_name'], folder_name)
            os.remove(photo['file_name'])
            time.sleep(0.01)
            pbar.update(1)

    log_file_name = 'log.txt'
    with open(log_file_name, 'w') as outfile:
        json.dump(photos_list, outfile)

    uploader.upload_file_to_disk(log_file_name, folder_name)
    # os.remove(log_file_name)

