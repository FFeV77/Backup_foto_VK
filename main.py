from time import sleep
import requests
import json
from tqdm import tqdm

with open('token.txt') as file:
    VK_TOKEN = file.readline()
    YD_TOKEN = file.readline()

class VK_photo:
    def __init__(self):
        self.v_api = '5.131'

    def get_foto_album(self, user_id:int=None, album:str='profile', count:int=5):
        '''Получает список фото в указанном альбоме ВК, указанного пользователя. Сохраняет информацию в .json'''
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
        print(f'\176 В альбоме VK "{album}" найдено {response["response"]["count"]} фото.')
        foto_list = response['response']['items']
        data = [{'file_name':str(item['likes']['count']) + '.jpg', 'size': item['sizes'][-1]['type']} for item in foto_list]
        with open('foto_list.json', 'w') as file:
            json.dump(data, file, indent=1)
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
        print(f'\176 Директория {path} создана на диске.')
        return create.status_code

    def delete_path(self, path:str):
        '''Удаляет путь'''
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            "path": path
            }
        headers = self.get_headers()
        create = requests.delete(url=url, params=params, headers=headers)
        print(f'\176 Директория {path} удалена.')
        return create.status_code

    def __check_upload_file(self, href):
        '''Проверяет статус загрузки'''
        while True:
            headers = self.get_headers()
            request = requests.get(url=href, headers=headers)
            response = request.json()
            if response['status'] == 'success':
                #print('Успешно')
                break
            elif response['status'] == 'failed':
                #print('Ошибка')
                break
            elif response['status'] == 'in-progress':
                #print('В процессе...')
                sleep(0.5)
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
            #print(f'\176 Скачивание файла {file_path} на ЯндексДиск...')
            self.__check_upload_file(response["href"])
        else:
            print(request.status_code, request.text)
        return

    def vk_fotos_upload(self, files:list, album:str='VK_fotos'):
        '''Обрабатывает список для загрузки, запускает загрузку'''
        self.post_path(album)
        print(f'\176 Начинаем загрузку файлов...')
        for file in tqdm(files, desc='Копирование'):
            file_link = file['sizes'][-1]['url']
            file_path = f'{album}/{file["likes"]["count"]}.jpg'
            if self.get_path(file_path) == 200:
                file_path = f'{album}/{file["likes"]["count"]}_{file["date"]}.jpg'
            self.upload_file_directly(file_link, file_path)
        else:
            print(f'Загрузка завершена. Загружено {len(files)} файлов')
        return


vk_user_id = 4837880 # ID пользователя ВК, по-умолчанию ссылается на себя
vk_album = 'profile' # Альбом ВК скачивания, по умолчанию - альбом фото-профиля
yd_path = 'VK_fotos' # папка на ЯндексДиске, куда сохранять фото
foto_count = 15 # Срез фото для скачивания

if __name__ == '__main__':

    VK = VK_photo()
    YD = YaUploader()

    foto_list = VK.get_foto_album(count=foto_count)
    YD.vk_fotos_upload(foto_list)
