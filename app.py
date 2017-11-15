# -*- coding: utf-8 -*-
import connexion
import logging
import datetime
import asyncio

from connexion import NoContent


# our memory-only pet storage
PETS = {}


@asyncio.coroutine
def get_pets(limit, animal_type=None):
    return [pet for pet in PETS.values()
            if not animal_type or pet['animal_type'] == animal_type][:limit]


@asyncio.coroutine
def get_pet(pet_id):
    pet = PETS.get(pet_id)
    return pet or ('Not found', 404)


@asyncio.coroutine
def put_pet(pet_id, pet):
    exists = pet_id in PETS
    pet['id'] = pet_id
    if exists:
        logging.info('Updating pet %s..', pet_id)
        PETS[pet_id].update(pet)
    else:
        logging.info('Creating pet %s..', pet_id)
        pet['created'] = datetime.datetime.utcnow()
        PETS[pet_id] = pet
    return NoContent, (200 if exists else 201)


@asyncio.coroutine
def delete_pet(pet_id):
    if pet_id in PETS:
        logging.info('Deleting pet %s..', pet_id)
        del PETS[pet_id]
        return NoContent, 204
    else:
        return NoContent, 404


if __name__ == '__main__':
    app = connexion.FlaskApp(__name__)
    # app = connexion.AioHttpApp(__name__)
    app.add_api('swagger.yaml', base_path='/')
    app.run(port=8080)
