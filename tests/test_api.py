async def test_get_without_data(cli, base_url):
    resp = await cli.get(base_url)
    assert resp.status == 400
    resp_json = await resp.json()
    assert resp_json == {'errors': [{'message': 'Must provide query string.'}]}


async def test_get_without_json(cli, base_url):
    resp = await cli.get(base_url, json={'value': 'foo'})
    assert resp.status == 400


async def test_post_without_json(cli, base_url):
    resp = await cli.post(base_url, json={'id': 1})
    assert resp.status == 400
