import os
from typing import Optional
from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB = os.getenv('MONGO_DB', 'mcon357')


def _get_collection() -> Collection:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return db['users']


def get_user_by_google_id(google_id: str) -> Optional[dict]:
    coll = _get_collection()
    return coll.find_one({'google_id': str(google_id)})


def create_user(google_id: str, name: str, email: str, picture: str, birthday: str) -> dict:
    coll = _get_collection()
    user = {
        'google_id': str(google_id),
        'name': name,
        'email': email,
        'picture': picture,
        'birthday': birthday,
    }
    coll.insert_one(user)
    return user


def update_user(google_id: str, **fields) -> Optional[dict]:
    coll = _get_collection()
    coll.update_one({'google_id': str(google_id)}, {'$set': fields})
    return coll.find_one({'google_id': str(google_id)})
