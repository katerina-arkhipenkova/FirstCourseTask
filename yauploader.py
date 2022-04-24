import requests


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

    def upload_file_to_disk(self, data, filename: str, folder_name=""):
        href = self.upload_link(disk_file_path=folder_name + filename).get("href", "")
        response = requests.put(href, data)
        response.raise_for_status()
        if response.status_code != 201:
            print('Ошибка при загрузке файла на Яндекс.Диск!')

    def new_folder(self, folder_name: str):
        disk_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': folder_name, 'overwrite': 'true'}
        response = requests.put(disk_url, headers=headers, params=params)
        return response.json()
