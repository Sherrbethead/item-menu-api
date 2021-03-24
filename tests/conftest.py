import json
import asyncio
from os import chdir, getcwd
from sys import path

import pytest
from dynaconf import settings

from item_menu.app import Application

# chdir('../item_menu')
# path.insert(0, getcwd())


@pytest.yield_fixture
def loop():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    yield new_loop
    new_loop.close()


@pytest.fixture
async def base_url():
    return '/graphql'


@pytest.fixture
async def cli(aiohttp_client):
    app = Application(settings)
    return await aiohttp_client(app.init_app())


@pytest.fixture
async def json_request():
    with open('autoroute_request.json', 'r', encoding='utf-8') as fh:
        return json.load(fh)
