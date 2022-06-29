
from datetime import date
from time import sleep
import requests
from pprint import pprint
from datetime import date
import json

with open('token.txt') as file:
    VK_TOKEN = file.readline()
    YD_TOKEN = file.readline()

class VK_photo:
    def __init__(self):
        self.v_api = '5.131'

    def get_foto_album(self, user_id:int=None, album:str='profile', count:int=5):
        '''Получает список фото в указанном альбоме ВК, указанного пользователя'''
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'album_id': album,
            'owner_id': user_id,
            'extended': 1,
            'count': count,
            'access_token': VK_TOKEN,
            'v': self.v_api
            }
        request = requests.get(url=url, params=params)
        response = request.json()
        print(f'\176 В альбоме VK "{album}" найдено {response["response"]["count"]} фото.\nСохраняем {count} шт.')
        foto_list = response['response']['items']
        with open('foto_list.json', 'w') as file:
            json.dump(foto_list, file, indent=1)
        return foto_list

class YaUploader:
    def __init__(self):
        self.token = YD_TOKEN

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def get_path(self, path:str):
        '''Проверяет путь'''
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            "path": path
            }
        headers = self.get_headers()
        check = requests.get(url=url, params=params, headers=headers)
        return check.status_code

    def post_path(self, path:str):
        '''Создает путь'''
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            "path": path
            }
        headers = self.get_headers()
        create = requests.put(url=url, params=params, headers=headers)
        print(f'Директория {path} создана на диске.')
        return create.status_code

    def __check_upload_file(self, href):
        '''Проверяет статус загрузки'''
        while True:
            headers = self.get_headers()
            request = requests.get(url=href, headers=headers)
            response = request.json()
            if response['status'] == 'success':
                print('Успешно')
                break
            elif response['status'] == 'failed ':
                print('Ошибка')
                break
            else:
                print('В процессе...')
                sleep(3)
        return

    def upload_file_directly(self, file_link: str, file_path: str):
        '''Загружает файл на диск, запускает проверку загрузки'''
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {
            'url': file_link,
            'path': file_path, 
            'overwrite': 'false'}
        headers = self.get_headers()
        request = requests.post(url=url, params=params, headers=headers)
        response = request.json()
        if request.status_code == 202:
            print(f'\176 Скачивание файла {file_path} на ЯндексДиск...')
            self.__check_upload_file(response["href"])
        else:
            print(request.status_code, request.text)
        return

    def vk_fotos_upload(self, files:list, album:str='VK_fotos'):
        '''Обрабатывает список для загрузки, запускает загрузку'''
        self.post_path(album)
        print(f'\176 Начинаем загрузку файлов...')
        for file in files:
            file_link = file['sizes'][-1]['url']
            file_path = f'{album}/{file["likes"]["count"]}.jpg'
            if self.get_path(file_path) == 200:
                file_path = f'{album}/{file["likes"]["count"]}_{date.today()}.jpg'
            self.upload_file_directly(file_link, file_path)
        else:
            print('Загрузка завершена')
        return

vk_user_id = 4837880 # ID пользователя ВК, по-умолчанию ссылается на себя
vk_album = 'profile' # Альбом ВК скачивания, по умолчанию - альбом фото-профиля
yd_path = 'VK_fotos' # папка на ЯндексДиске, куда сохранять фото
foto_count = 5 # Срез фото для скачивания

VK = VK_photo()
YD = YaUploader()

foto_list = VK.get_foto_album(user_id = 4837880)
YD.vk_fotos_upload(foto_list)

