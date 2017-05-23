import requests
import json
import enum
# from tinydb import TinyDB


class Grades(enum.Enum):
    Overall = "01"
    Fun = "02"
    Innovation = "03"
    Theme = "04"
    Graphics = "05"
    Audio = "06"
    Humor = "07"
    Mood = "08"


class EntryType(enum.Enum):
    Jam = 'jam'

PARENT_NODE = 9405
FEED_URI = 'https://api.ldjam.com/vx/node/feed/{parent_node}/grade-{grade}-result+reverse/item/game/{entry_type}?offset={offset}&limit={limit}'


def get_node_list(grade_category, entry_type, offset=0, limit=50):

    uri = FEED_URI.format(
        parent_node=PARENT_NODE,
        grade=grade_category.value,
        entry_type=entry_type.value,
        offset=offset,
        limit=limit)

    data = requests.get(url=uri)
    return json.loads(data.text)


NODE_URI = 'https://api.ldjam.com/vx/node/get/{nodes}'


def get_node_data(node_ids):

    uri = NODE_URI.format(nodes="+".join(str(nid) for nid in node_ids))
    data = requests.get(url=uri)
    return json.loads(data.text)


def get_identifiers_from_node_list(node_list):

    return [node['id'] for node in node_list['feed']]


def store_node(db, node):

    record = {'id': node['id'], 'authors': [node['author']]}

    for key in node['magic']:

        if key == 'given':
            record['given'] = node[key]
        elif key == 'grade':
            record['received'] = node[key]
        elif key.startswith('grade-'):

            _, category, info_type = key.split("-")
            category = Grades(category).name
            if category not in record:
                record[category] = {}
            record[category][info_type] = node[key]

    db.insert(record)


def store_nodes(db, nodes):

    for node in nodes['node']:
        store_node(db, node)


def run():

    db = None
    list_size = 30
    offset = 0
    chunk_size = 10

    node_list = get_node_list(Grades.Overall, EntryType.Jam, offset=offset, limit=list_size)
    node_ids = get_identifiers_from_node_list(node_list)
    node_count = len(node_ids)
    while node_ids:
        nodes = get_node_data(node_ids[:chunk_size])
        store_node(db, nodes)
        node_ids = node_ids[chunk_size:]

    offset += node_count