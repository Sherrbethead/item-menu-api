#!/usr/bin/python3
import logging

from aiohttp import web
from dynaconf import settings

from item_menu.app import Application


# настройка позволяет прописывать переменные окружения без префикса
settings.configure(ENVVAR_PREFIX_FOR_DYNACONF=False)


if __name__ == '__main__':
    app = Application(settings)

    try:
        web.run_app(app.init_app(), port=settings.PORT)
        logging.info('Service is stopped')
    except RuntimeError as re:
        logging.error('Service is stopped due to: {}'.format(re))
