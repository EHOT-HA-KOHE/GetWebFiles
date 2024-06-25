import re
import os
import zipfile
import json
import shutil

from requests.exceptions import ConnectionError

from pyrogram import Client, filters
from pyrogram.types import BotCommand
from pywebcopy import save_webpage

from loguru_config import logger


# Считываем данные из файла
with open('tg_connection_data.json', 'r', encoding='utf-8') as f:
    connection_data = json.load(f)

# Получаем переменные из данных
api_id_bot = connection_data["api_id_bot"]
api_hash_bot = connection_data["api_hash_bot"]
bot_token = connection_data["bot_token"]

# Подключение Telegram
bot = Client("web_copy_bot", api_id=api_id_bot, api_hash=api_hash_bot, bot_token=bot_token)


class CopyWeb:
    download_folder = './downloaded_site'

    def __init__(self, url):
        self.url = url

    @staticmethod
    def sure_folder_exists(folder_path):
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
            except OSError as error:
                logger.error(f"Ошибка при создании папки: {error}")

    @staticmethod
    def url_to_folder_name(web_url):
        # Убираем протокол (http(s)://) и завершающий слэш, если он есть
        clean_url = re.sub(r'^https?://', '', web_url).rstrip('/')

        # Заменяем все символы, кроме букв, цифр, дефисов, точек на подчеркивания
        fol_name = re.sub(r'[^a-zA-Z0-9\-\.]', '_', clean_url)

        return fol_name

    @staticmethod
    def copy_web(web_url, folder_to_download, fol_name):
        try:
            # Копируем весь сайт
            save_webpage(
                url=web_url,
                project_folder=folder_to_download,
                project_name=fol_name,
                bypass_robots=True,
                # debug=True,
                open_in_browser=False
            )
        except Exception as err:
            logger.error(f"Website copy error!\n{err}")

    @staticmethod
    def remove_html_comments(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # Удаляем многострочные комментарии
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as err:
            logger.error(f"HTML comments delete err!\n{err}")

    @staticmethod
    def remove_js_comments(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # Удаляем многострочные комментарии
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # Удаляем однострочные комментарии
            content = re.sub(r'//.*', '', content)

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)

        except Exception as err:
            logger.error(f"JS comments delete err!\n{err}")

    @staticmethod
    def remove_css_comments(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # Удаляем многострочные комментарии
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as err:
            logger.error(f"CSS comments delete err!\n{err}")

    @staticmethod
    def zip_folder(folder_path, zip_path=None):
        try:
            if zip_path is None:
                # Если путь для сохранения ZIP не указан, сохранить рядом с исходной папкой
                zip_path = os.path.join(os.path.dirname(folder_path), os.path.basename(folder_path) + '.zip')

            # Создать ZIP-файл и добавить в него все файлы из указанной папки
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                        zipf.write(file_path, arcname=file_arcname)
        except Exception as err:
            logger.error(f"ZIP creating err!\n{err}")

    def del_comments(self, path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    self.remove_html_comments(file_path)
                elif file.endswith('.js'):
                    file_path = os.path.join(root, file)
                    self.remove_js_comments(file_path)
                elif file.endswith('.css'):  # здесь было изменено расширение файла
                    file_path = os.path.join(root, file)
                    self.remove_css_comments(file_path)

    def is_link_correct(self):
        if not (self.url.startswith('https://') or self.url.startswith('http://')):
            return False
        return True

    def start(self):
        self.sure_folder_exists(self.download_folder)
        folder_name = self.url_to_folder_name(self.url)
        web_folder_path = f'{self.download_folder}/{folder_name}'

        try:
            self.copy_web(self.url, self.download_folder, folder_name)

            self.del_comments(web_folder_path)
            self.zip_folder(web_folder_path)

            return [True, {'zip_path': f'{web_folder_path}.zip', 'url': self.url}, web_folder_path]

        except ConnectionError as e:
            return [False, f"Ошибка подключения: {e}. \n\n"
                           f"**Вероятно вы ошиблись с адресом сайта, это корректный адрес {self.url}?** \n\n"
                           f"Так же возможно, проблемы с разрешением доменного имени или сервер недоступен.",
                    web_folder_path]
        except Exception as err:
            return [False, str(err), web_folder_path]


def clear_sites_folder(folder_path):
    # Проверяем, существует ли папка
    if not os.path.isdir(folder_path):
        logger.error("Указанный путь не существует или не является папкой.")
        return

    # Проходимся по всем объектам внутри папки
    for item_name in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item_name)
        try:
            # Если это файл, удаляем его
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            # Если это папка, удаляем её со всем содержимым
            elif os.path.isdir(item_path):
                # Рекурсивно удаляем содержимое папки
                for root, dirs, files in os.walk(item_path, topdown=False):
                    for name in files:
                        os.unlink(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                # Удаляем саму папку
                os.rmdir(item_path)
        except Exception as e:
            logger.error(f"Ошибка при удалении {item_path}: {e}")


def del_already_sent_files(path):
    if os.path.exists(f'{path}.zip'):
        os.remove(f'{path}.zip')

    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)


@bot.on_message(filters.command("download_web") & filters.private)
async def download_web(client, message):
    if len(message.command) == 2:

        web = CopyWeb(message.command[-1])
        if not web.is_link_correct():
            await bot.send_message(
                message.chat.id,
                'Command format is not correct. Example: \n\n`/download_web https://example.com`\n\n'
                'Must start with "https://" or "http://"')
            return

        await bot.send_message(message.chat.id, f'Start copy {message.command[-1]}, please wait...')

        res = web.start()
        if res[0]:
            await bot.send_document(chat_id=message.chat.id, document=res[1].get('zip_path'),
                                    caption=res[1].get('url'))
        else:
            await bot.send_message(message.chat.id, str(res[1]))

        del_already_sent_files(res[2])

    else:
        await bot.send_message(message.chat.id, 'Command format is not correct. Example: '
                                                '\n\n`/download_web https://example.com`')


if __name__ == '__main__':
    logger.info('I AM ALIVE BOT')
    clear_sites_folder(f'{CopyWeb.download_folder}')

    # bot.start()
    # bot.set_bot_commands([BotCommand("download_web", "Скачать сайт"),])
    # bot.stop()

    bot.run()
