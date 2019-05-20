from src.data.query import QueryMaker
from src.db.index import *
from src.db.queries.query import *
from datetime import tzinfo, datetime, timezone
from tqdm import tqdm

_queries = db[MONGODB_CONFIG['col_queries']]
_query_maker = QueryMaker()


def insert(query):
    document = convert_to_document(query=query)
    return _queries.insert_one(document)


def get_list() -> list:
    queries = []
    cursor = _queries.find({})

    for document in cursor:
        query = convert_to_query(document)
        queries.append(query)
    return queries


def find_all():
    queries = []
    for document in _queries.find({}):
        query = convert_to_query(document)
        queries.append(query)
    return queries


def find_by_category(category):
    queries = []
    for document in _queries.find({'category': category}):
        query = convert_to_query(document)
        queries.append(query)
    return queries


def find_by_date(year, month, day, hour=0, minute=0, second=0):
    NOW = datetime(year=year, month=month, day=day,
                   hour=hour, minute=minute, second=second)
    UTC = timezone.utc

    NOW.astimezone(UTC)

    queries = _queries.find({'added_time': {'$gte': NOW}})

    print(list(queries))


def rebase():
    for document in tqdm(_queries.find({}), desc='Rebase query'):
        _id = document['_id']
        chat = document['chat']
        try:
            added_time = document['added_time']
        except KeyError:
            added_time = None

        try:

            query = _query_maker.make_query(chat=chat,
                                            added_time=added_time)
            if query is None:
                _queries.delete_one({'_id': _id})
                continue
            insert(query)
            _queries.delete_one({'_id': _id})
        except Exception as err:
            print('rebase ERROR: ', err)
            print(document)
            return document


if __name__ == '__main__':
    rebase()
    # find_by_date(2018, 5, 6, 0)
