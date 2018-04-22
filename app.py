# -*- coding: utf-8 -*-
import connexion
import logging
import datetime
import asyncio
import aiohttp.web


logging.basicConfig(level=logging.INFO)

# our memory-only pet storage
LAST_ID = 0
PETS = {}


@asyncio.coroutine
def get_pets(limit, animal_type=None):
    data = [pet for pet in PETS.values()
            if not animal_type or pet['animal_type'] == animal_type][:limit]
    return aiohttp.web.json_response(data)


@asyncio.coroutine
def get_pet(pet_id):
    pet = PETS.get(pet_id)
    return aiohttp.web.json_response(data=pet, status=200 if pet else 404)


@asyncio.coroutine
def put_pet(pet_id, pet):
    exists = pet_id in PETS
    if exists:
        logging.info('Updating pet %s..', pet_id)
        PETS[pet_id].update(pet)
    else:
        global LAST_ID
        LAST_ID += 1
        pet_id = LAST_ID
        pet['id'] = pet_id
        logging.info('Creating pet %s..', pet_id)
        pet['created'] = str(datetime.datetime.utcnow())
        PETS[pet_id] = pet
    status = 200 if exists else 201
    return aiohttp.web.json_response(data='', status=status)


@asyncio.coroutine
def delete_pet(pet_id):
    if pet_id in PETS:
        logging.info('Deleting pet %s..', pet_id)
        del PETS[pet_id]
        return aiohttp.web.json_response(data='', status=204)
    else:
        return aiohttp.web.json_response(data='', status=404)


@asyncio.coroutine
def test_connexion(test_client):
    app = connexion.AioHttpApp(__name__)
    app.add_api('swagger.yaml', base_path='/api')
    aiohttp_app = app.app
    client = yield from test_client(aiohttp_app)

    resp = yield from client.get('/1')
    assert resp.status == 404

    # Check empty
    resp = yield from client.get('/api/pets')
    json_data = yield from resp.json()
    assert json_data == []

    # Add new pet
    pet = {"name": "Tosi", "animal_type": "cat"}
    resp = yield from client.put('/api/pets/1', json=pet)
    assert resp.status == 201

    # Check all
    resp = yield from client.get('/api/pets')
    json_data = yield from resp.json()
    assert len(json_data) == 1
    assert json_data[0]['id'] == 1
    assert json_data[0]['name'] == 'Tosi'

    resp = yield from client.delete('/api/pets/1')
    assert resp.status == 204

    resp = yield from client.delete('/api/pets/1')
    assert resp.status == 404

    resp = yield from client.get('/api/pets')
    json_data = yield from resp.json()
    assert len(json_data) == 0


if __name__ == '__main__':
    # pass
    # app = connexion.FlaskApp(__name__)
    app = connexion.AioHttpApp(__name__)
    app.add_api('swagger.yaml', base_path='/api')
    app.run(port=8080)
