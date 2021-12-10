import pytest
# import json
# from urllib.parse import urlparse, urljoin
from httpx import AsyncClient
import aiofiles
import hashlib

# test specs validation agains request
# upload specs / test / take server address from specs
# TODO - Test with status code compare
# TODO - Test responce codes

SERVER_URL = "http://138.197.73.160:8000/"
PROXY_URL = "http://127.0.0.1:5000/p/test_api/1/"
# Test types: "success", "fail", "error",
TEST_TYPE = "success"

GEN_HEADERS = {
    "X-Auth-Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2Vy"
    "X2lkIjoxLCJ1c2VyX2VtYWlsIjoiZ2JhZ2gxNkBmcmVldW5pLmVkdS5nZSJ9"
    ".YvBTfEmLVUsbqT2lzB9N4v_LUugDTGzHdOM_D1XwyWw",
    "Host": "http://127.0.0.1:5000"
}


async def request_coro(test_params, test_types, async_server_client, async_proxy_client):
    test_params["headers"] = GEN_HEADERS
    server_response = await async_server_client.request(**test_params)
    test_params["headers"] = GEN_HEADERS
    proxy_response = await async_proxy_client.request(**test_params)
    # await compare_cases(test_types, test_params, server_response, proxy_response)
    if 'status' in test_types:
        if TEST_TYPE == 'success':
            if test_params['method'] in ("POST", "PUT"):
                statuses = (200, 201, 204)
            elif test_params['method'] in ("GET"):
                statuses = (200, )
            else:
                statuses = tuple()
            assert proxy_response.status_code == server_response.status_code and \
                server_response.status_code in statuses
            # File upload
            # if 'file_upload' in test_types:
            #    assert server_response.json()['file_hash'] == proxy_response.json()['file_hash']
        elif TEST_TYPE == "fail":
            statuses = range(400, 500)
            assert proxy_response.status_code == server_response.status_code and \
                server_response.status_code in statuses
        elif TEST_TYPE == "error":
            statuses = range(500, 600)
            assert proxy_response.status_code == server_response.status_code and \
                server_response.status_code in statuses
    if 'file_download' in test_types:
        assert hashlib.sha256(proxy_response.content).hexdigest() == \
            hashlib.sha256(server_response.content).hexdigest()


@pytest.fixture
async def async_server_client():
    async with AsyncClient(base_url=SERVER_URL) as client:
        yield client


@pytest.fixture
async def async_proxy_client():
    async with AsyncClient(base_url=PROXY_URL) as client:
        yield client


@pytest.mark.asyncio
async def test_create_pet(async_server_client, async_proxy_client):

    test_params = {
        "url": "/pets/1",
        "method": 'POST',
        "json": {'name': 'miu',
                 'animal_type': 'cat',
                 'tags': {},
                 'created': '2021-11-30T20:21:29.234812'},
    }
    test_types = {"status_success", "status_fail"}

    await request_coro(test_params, test_types, async_server_client, async_proxy_client)


@pytest.mark.asyncio
async def test_get_pet(async_server_client, async_proxy_client):
    test_params = {
        "url": "/pets/",
        "method": "GET",
    }
    test_types = {"status_success"}

    await request_coro(test_params, test_types, async_server_client, async_proxy_client)


@pytest.mark.asyncio
async def test_set_file(async_server_client, async_proxy_client):

    async with aiofiles.open('/home/saturn/Downloads/openapi.yaml', mode='rb') as f:
        contents = await f.read()

    test_params = {
        "url": "/file",
        "files": {"file": contents},
        "method": 'POST',
    }
    test_types = {"status", "file_upload"}

    await request_coro(test_params, test_types, async_server_client, async_proxy_client)


@pytest.mark.asyncio
async def test_get_file(async_server_client, async_proxy_client):

    test_params = {
        "url": "/file",
        "method": 'GET',
    }
    test_types = {"status", "file_download"}

    await request_coro(test_params, test_types, async_server_client, async_proxy_client)


@pytest.mark.asyncio
async def test_read_items(async_server_client, async_proxy_client):

    test_params = {
        "url": "/items/",
        "method": 'GET',
        "params": {"q": "keyword=chicken&max_results=2"}
    }
    test_types = {"status"}

    await request_coro(test_params, test_types, async_server_client, async_proxy_client)


@pytest.mark.asyncio
async def test_read_items2(async_server_client, async_proxy_client):

    test_params = {
        "url": "/items/123",
        "method": 'GET',
        "params": {"q": "keyword=chicken&max_results=2"}
    }
    test_types = {"status"}

    await request_coro(test_params, test_types, async_server_client, async_proxy_client)


@pytest.mark.asyncio
async def test_login(async_server_client, async_proxy_client):

    test_params = {
        "url": "/login/",
        "method": 'POST',
        "data": {
            'username': 'some_username',
            'password': 'some_password'
        }
    }
    test_types = {"status"}

    await request_coro(test_params, test_types, async_server_client, async_proxy_client)
