from elasticsearch import Elasticsearch
import pandas as pd
# from sqlalchemy import create_engine
import yaml

with open('config/config.yaml', "r") as config_file:
    config = yaml.safe_load(config_file)

# engine = create_engine("elasticsearch:///?Server=127.0.0.1&;Port=9200&User=admin&Password=123456")
# conn_args = {"verify_certs": False, "ssl_show_warn": False,
#              'http_auth': (config['elasticsearch']['username'], config['elasticsearch']['password']),
#             }
# conn = create_engine(f"elasticsearch+{config['elasticsearch']['host']}:{config['elasticsearch']['port']}",
#                      connect_args=conn_args)
conn_raw = Elasticsearch(f"{config['elasticsearch']['host']}:{config['elasticsearch']['port']}/",
                         verify_certs=False, ssl_show_warn=False,
                         http_auth=(config['elasticsearch']['username'], config['elasticsearch']['password']))

# import eland as ed
# df = ed.DataFrame(es_client, es_index_pattern='messages-*')


def get_chats():
    req = {
        "size": 0,
        "aggs":{
            "unique_names": {
                "terms": {
                    "field": "chat.keyword",
                    "size": 9999
                }
            }
        },
        "_source": False
    }

    data = conn_raw.search(body=req, index=config['index_format'])['aggregations']['unique_names']['buckets']
    chats = list()
    for value in data:
        chats.append({'label': value['key'], 'value': value['key']})

    return chats


def get_users():
    req = {
        "size": 0,
        "aggs": {
            "unique_names": {
                "terms": {
                    "field": "username.keyword",
                    "size": 999000
                }
            }
        },
        "_source": False
    }
    data = conn_raw.search(body=req, index=config['index_format'])['aggregations']['unique_names']['buckets']
    users = list()
    for value in data:
        users.append({'label': value['key'], 'value': value['key']})

    return users


def generate_sql(date_from=pd.Timestamp.now().strftime('%Y-%m-%d'),
                 condition='AND',
                 search_words=None, username=None, chat=None, limit=0):
    # date_from
    # "message_id": 48654,
    # "username": "kyiv_informator_ua",
    # "firstName": "Інформатор Київ",
    # "lastName": null,
    # "user_id": null,
    # "phone": null,
    # "chat": "Інформатор Київ",
    # "chat_id": -1001139619281,
    # "message": sent message in Telegram

    sql = f''' 
            SELECT 
                * 
            FROM 
                "{config['index_format']}" 
            WHERE
                timestamp  >= '{date_from}'
        '''

    if username is not None:
        if len(username) > 0:
            line = f'''username = \'{username.pop(0)}\''''
            while len(username) > 0:
                line = f'''{line} OR username = \'{username.pop(0)}\' '''
            sql = f'''
                {sql} 
                AND ({line})
        '''
    # if first_name is not None:
    #     sql = f'''
    #         {sql}
    #         AND firstName = '{first_name}'
    #     '''
    # if last_name is not None:
    #     sql = f'''
    #         {sql}
    #         AND lastName = '{last_name}'
    #     '''
    # if user_id is not None:
    #     sql = f'''
    #         {sql}
    #         AND user_id = {user_id}
    #     '''
    # if phone is not None:
    #     sql = f'''
    #         {sql}
    #         AND phone = '{phone}'
    #     '''
    if chat is not None:
        if len(chat) > 0:
            line = f'''chat = \'{chat.pop(0)}\''''
            while len(chat) > 0:
                line = f'''{line} OR chat = \'{chat.pop(0)}\' '''
            sql = f'''
                {sql} 
                AND ({line})
            '''

    if search_words is not None:
        if len(search_words) > 0:
            words = search_words.split(',')
            line = f'''message LIKE \'%%{words.pop(0)}%%\''''
            while len(words) > 0:
                line = f'''{line} {condition} message LIKE \'%%{words.pop(0)}%%\' '''
            sql = f'''
                {sql} 
                AND ({line})
            '''

    if limit > 0:
        sql = sql + f' LIMIT {limit}\n'
    # sql = sql + ' ORDER BY "timestamp"\n'
    return sql


def generate_query(date_from=pd.Timestamp.now().strftime('%Y-%m-%d'),
                   condition='AND',
                   search_words=None, username=None, chat=None, limit=0):

    q_timestamp = {"range": {"timestamp": {"gte": date_from}}}

    if username is not None:
        if len(username) > 0:
            q_username = {'bool': {"should": []}}
            for name in username:
                q_username['bool']['should'].append({"match": {"username": name}})
        else:
            q_username = ''
    else:
        q_username = ''

    if chat is not None:
        if len(chat) > 0:
            q_chat = {'bool': {"should": []}}
            for ch in chat:
                q_chat['bool']['should'].append({"match": {"chat": ch}})
        else:
            q_chat = ''
    else:
        q_chat = ''

    if search_words is not None:
        if condition == 'AND':
            cond = 'must'
        else:
            cond = 'should'
        q_message = {'bool': {cond: []}}
        if len(search_words) > 0:
            words = search_words.split(',')
            while len(words) > 0:
                q_message['bool'][cond].append({"match": {"message": f"%%{words.pop(0)}%%"}})
    else:
        q_message = ''

    if len(q_chat) > 0 or len(q_username) > 0 or len(q_message) > 0:
        sub_query = {'bool': {'must': []}}
        if len(q_chat) > 0:
            sub_query['bool']['must'].append(q_chat)
        if len(q_username) > 0:
            sub_query['bool']['must'].append(q_username)
        if len(q_message) > 0:
            sub_query['bool']['must'].append(q_message)
        query = {'bool':
                     {'must': [
                         q_timestamp,
                         sub_query
                     ]
                     }
                }
    else:
        query = {'bool': {'must': [q_timestamp]}}

    return query


def get_messages(date_from, condition='AND', search_words=None, username=None, chat=None, limit=10):
    columns = ['timestamp', 'chat', 'username', 'firstName', 'lastName', 'phone', 'message']

    sql = generate_query(date_from=date_from,
                         condition=condition,
                         search_words=search_words,
                         username=username,
                         chat=chat
                        )
    if limit == 0:
        data = conn_raw.search(index=config['index_format'], query=sql, size=10000, sort='timestamp:desc')
    else:
        data = conn_raw.search(index=config['index_format'], query=sql, size=limit, sort='timestamp:desc')
    df = pd.DataFrame()
    while len(data['hits']['hits']) > 0:
        row = data['hits']['hits'].pop(0)
        df = pd.concat([df, pd.DataFrame(row['_source'], index=[0])], ignore_index=True, sort=False)
    if df.empty:
        df = pd.DataFrame(columns=columns)
    else:
        df = df[['timestamp', 'chat', 'username', 'firstName', 'lastName', 'phone', 'message']]
    return df
