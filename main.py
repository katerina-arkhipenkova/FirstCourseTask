import time
import requests
import json
from tqdm import tqdm
from vkuser import VkUser
from yauploader import YaUploader

if __name__ == '__main__':
    while True:
        user_input_profile = input('Введите номер профиля или screen_name: ')
        user_input_photo_count = input('Введите количество фотографий: ')
        user_input_album_id = input('Введите тип фотографий: profile, wall: ')
        break
    with open('tokenVK.txt', 'r') as file_object:
        tokenVK = file_object.read().strip()

    vk_client = VkUser(tokenVK, '5.131')
    album_id = user_input_album_id
    count_photos = int(user_input_photo_count)
    user = vk_client.get_user(user_input_profile)
    for item in user['response']:
        if item['is_closed'] is False:
            user_id = item['id']
        else:
            print('Профиль пользователя закрыт')
            exit()

    vk_photos_list = vk_client.get_photos_list(user_id, album_id, count_photos)
    photos_list = vk_client.upload_photos_to_disk(vk_photos_list)
    with open('tokenYaD.txt', 'r') as file_object:
        tokenYaD = file_object.read().strip()

    uploader = YaUploader(tokenYaD)
    folder_name = 'LoadedPhotos/'
    uploader.new_folder(folder_name)

    with tqdm(total=len(photos_list)) as pbar:
        for photo in photos_list:
            pbar.set_description("Загрузка фотографий на Яндекс.Диск")
            data = requests.get(photo['url'])
            uploader.upload_file_to_disk(data, photo['file_name'], folder_name)
            time.sleep(0.01)
            pbar.update(1)

    log_file_name = 'log.txt'
    with open(log_file_name, 'w') as outfile:
        json.dump(photos_list, outfile)
    data = open(log_file_name, "rb")
    uploader.upload_file_to_disk(data, log_file_name, folder_name)
