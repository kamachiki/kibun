import os
import boto3
import uuid
import boto3.dynamodb
from boto3.dynamodb.conditions import Key, Attr
from datetime import *
import html
import math

import boto3.dynamodb.conditions

def _get_database(): #データーベースをとってくる
    endpoint = os.environ.get('DB_ENDPOINT')
    if endpoint:
        return boto3.resource('dynamodb', endpoint_url=endpoint)
    else:
        return boto3.resource('dynamodb')
    
def get_user(user_id):
    table = _get_database().Table(os.environ['DB_TABLE_USER'])
    response = table.query(
        KeyConditionExpression=Key('id').eq(user_id)
    )
    items = response['Items']
    return items[0] if items else None

def create_session(user):
    item = {
        "id":  uuid.uuid4().hex,
        "Auser_id": user["id"],
        "Atimestamp": int(datetime.now().timestamp())
    }
    table = _get_database().Table(os.environ['DB_TABLE_USER_SESSION'])
    table.put_item(Item=item)
    return item

 # 対象の日時を指定 (before)
def cleanup_session(before):
    table = _get_database().Table(os.environ['DB_TABLE_USER_SESSION'])
   
    # スキャンして古いデータを列挙
    response = table.scan(
        FilterExpression='Atimestamp < :target_date',  # 作成日時が対象日時より前のデータをフィルタ
        ExpressionAttributeValues={
            ':target_date': int( before.timestamp() ) # Unixタイムスタンプに変換
        }
    )

    # 削除対象のアイテムをリストに格納
    items_to_delete = [{'id': item['id']} for item in response['Items']]  
    # データが多い場合は、LastEvaluatedKeyを使って続きを取得
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            FilterExpression='Atimestamp < :target_date',
            ExpressionAttributeValues={
                ':target_date': before.timestamp()
            }
        )
        items_to_delete.extend([{'id': item['id']} for item in response['Items']])
    # items_to_delete の中身を確認
    if items_to_delete:  # 削除対象がある場合のみ実行
        # バッチ書き込みでアイテムを削除
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item( Key={
                    'id': item['id']
                })
            return len(items_to_delete)
    else:
        return 0

def session_check(session_id):
    return _get_item(session_id,'DB_TABLE_USER_SESSION')

def _get_item(id,tablename):
    table = _get_database().Table(os.environ[tablename])
    response = table.query(
        KeyConditionExpression=Key('id').eq(id)
    )
    items = response['Items']
    return items[0] if items else None

def create_user(user):
    auser = get_user(user["id"])
    if auser==None:
        if user['Atype']=="child":
            
            item = {
            'id':user['id'],
            'Apassword': user['Apassword'],
            'Agakunen': user['Agakunen'],
            'Atype': "child",
        }
        if user['Atype']=="adult":
            item = {
                'id':user['id'],
                'Apassword':user['Apassword'],
                'Amail-address':user['Amail-address'],
                'Atype':"adult"
            }
        table = _get_database().Table(os.environ['DB_TABLE_USER'])
        table.put_item(Item=item)
        return item
    else:
        return None


def _get_lists(query_name,user_id,mae,ushiro,tablename):
    table = _get_database().Table(os.environ[tablename])


    #keye = query_name + ' = :pk_value AND Atimestamp BETWEEN :start AND :end' 
    #keyp = {':pk_value': user_id,
    #        ':start': int(mae.timestamp()),
    #        ':end': int(ushiro.timestamp())}
    
    keyp =Key(query_name).eq(user_id) & Key('Atimestamp').between(int(mae.timestamp()), int(ushiro.timestamp()))

    # スキャンして期間内のデータを列挙
    response = table.query(
        KeyConditionExpression=  keyp
    )
    items = response['Items']
    # データが多い場合は、LastEvaluatedKeyを使って続きを取得
    while 'LastEvaluatedKey' in response:
        response = table.query(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            KeyConditionExpression= keyp
            )
        items.extend(response['Items'])
    return items

#よびかけの記録をつくる
def create_yobikake(yobikake_data,user_id):
    item ={
        'Atimestamp':int(datetime.now().timestamp()),
        'Ayobikakeru':user_id,
        'Ayobikakerareru':yobikake_data["Ayobikakerareru"],
        'Akibun_timestamp':int(yobikake_data['Akibun_timestamp']),
        'Ayobikake':html.escape(yobikake_data['Ayobikake']),
        'Akibun':yobikake_data['Akibun'],
        'Akokai':yobikake_data['Akokai'],
        'Areason':yobikake_data['Areason'],
    }
    table = _get_database().Table(os.environ['DB_TABLE_YOBIKAKE'])
    table.put_item(Item=item)
    return item 

#気分の記録をつくる
def create_kibun(kibun,child_id):
    item ={
        'Atimestamp':math.floor(datetime.now().timestamp()),
        'Aface':kibun['Aface'],
        'Atype':kibun['Atype'],
        'Areason':html.escape(kibun['Areason']),
        'Akokai':bool(kibun['Akokai']),
        'Achild_id':child_id
    }
    table = _get_database().Table(os.environ['DB_TABLE_KIBUN'])
    table.put_item(Item=item)
    return item   

#goalの記録をつくる
def create_goal(goal,child_id):
    item ={
        'Atimestamp':int(datetime.now().timestamp()),
        'Achild_id':child_id,
        'Agoal':html.escape(goal['Agoal'])
    }
    table = _get_database().Table(os.environ['DB_TABLE_GOAL'])
    table.put_item(Item=item)
    return item   
#commentの記録をつくる
def create_comment(comment,adult_id):
    item ={
        'Atimestamp':int(datetime.now().timestamp()),
        'Achild_id':comment['Achild_id'],
        'Aadult_id':adult_id,
        'Acomment':html.escape(comment['Acomment'])
    }
    table = _get_database().Table(os.environ['DB_TABLE_COMMENT'])
    table.put_item(Item=item)
    return item   

#子供と大人の記録を作る
def create_kodomotootona(kodomotootona,child_id):
    item ={
        'Achild_id':child_id,
        'Aadult_id':kodomotootona['Aadult_id']
    }
    table = _get_database().Table(os.environ['DB_TABLE_KodomoToOtona'])
    table.put_item(Item=item)

    table = _get_database().Table(os.environ['DB_TABLE_OtonaToKodomo'])
    table.put_item(Item=item)
    return item

#子供と大人の記録を消す
def delete_kodomoToOtona(child_id,adult_id):
    table = _get_database().Table(os.environ['DB_TABLE_OtonaToKodomo'])
    response = table.delete_item(

        Key={
            "Achild_id":child_id,
            "Aadult_id":adult_id
        },
        ReturnValues='ALL_OLD'
    )

    table = _get_database().Table(os.environ['DB_TABLE_KodomoToOtona'])
    response = table.delete_item(

        Key={
            "Achild_id":child_id,
            "Aadult_id":adult_id
        },
        ReturnValues='ALL_OLD'
    )

    if 'Attributes' in response:
        return response['Attributes']
    else:
        return False

#子供のIDから大人を取り出す
def get_kodomoToOtona(child_id):
    table=_get_database().Table(os.environ['DB_TABLE_KodomoToOtona'])
    response = table.query(
        KeyConditionExpression=Key('Achild_id').eq(child_id)
    )
    items = response['Items']
    return items

#子供のIDから大人を取り出す
def get_otonaToKodomo(adult_id):
    table=_get_database().Table(os.environ['DB_TABLE_OtonaToKodomo'])
    response = table.query(
        KeyConditionExpression=Key('Aadult_id').eq(adult_id)
    )
    items = response['Items']
    return items


#maeからushiroの間の気分をとりだす。それぞれdatetime型
def get_kibuns(child_id,mae,ushiro,kokai):
    table = _get_database().Table(os.environ['DB_TABLE_KIBUN'])
    return _get_kokai(table,'Achild_id',child_id,mae,ushiro,kokai)

def get_yobikakesForKibun(child_id,kibun_timestamp,kokai):
    table = _get_database().Table(os.environ['DB_TABLE_YOBIKAKE'])

    # スキャンして期間内のデータを列挙
    keyp =Key('Ayobikakerareru').eq(child_id) 
    if kokai:
        response = table.query(
            KeyConditionExpression = keyp,
            #FilterExpression=Attr('Akokai').eq(True) & Attr("Akibun_timestamp").eq(kibun_timestamp)
            #FilterExpression=Attr("Akibun_timestamp").eq(kibun_timestamp)
        )
    else:
        response = table.query(
            KeyConditionExpression = keyp,
            #FilterExpression=Attr("Akibun_timestamp").eq(kibun_timestamp)
        )
    items = response['Items']
    return items




def _get_kokai(table,id_name,child_id,mae,ushiro,kokai):
    # スキャンして期間内のデータを列挙
    keyp =Key(id_name).eq(child_id) & Key('Atimestamp').between(int(mae.timestamp()), int(ushiro.timestamp()))

    if kokai:
        response = table.query(
            KeyConditionExpression = keyp,
            FilterExpression=Attr('Akokai').eq(True)
        )
    else:
        response = table.query(KeyConditionExpression =keyp) 
    items = response['Items']
    return items

#maeからushiroの間の気分をとりだす。それぞれdatetime型
def get_yobikakes(child_id,mae,ushiro):
    return _get_lists('Ayobikakerareru',child_id,mae,ushiro,'DB_TABLE_YOBIKAKE')
def get_goals(child_id,mae,ushiro):
    return _get_lists('Achild_id',child_id,mae,ushiro,'DB_TABLE_GOAL')
def get_comments(child_id,mae,ushiro):
    return _get_lists('Achild_id',child_id,mae,ushiro,'DB_TABLE_COMMENT')

#項目を消す
def delete_kibuns(child_id,timestamp):
    return _delete_item("Achild_id",child_id,"Atimestamp",timestamp,'DB_TABLE_KIBUN')
def delete_yobikakes(child_id,timestamp):
    return _delete_item('Achild_id',child_id,"Atimestamp",timestamp,'DB_TABLE_YOBIKAKE')
def delete_goals(child_id,timestamp):
    return _delete_item('Achild_id',child_id,"Atimestamp",timestamp,'DB_TABLE_GOAL')
def delete_comments(child_id,timestamp):
    return _delete_item('Achild_id',child_id,"Atimestamp",timestamp,'DB_TABLE_COMMENT')

def _delete_item(id_name,id,timestamp_name,timestamp,table_name):
    table = _get_database().Table(os.environ[table_name])
    result = table.delete_item(
        Key={
            id_name:id,
            timestamp_name:timestamp
        },
        ReturnValues='ALL_OLD'
    )
    return result['Attributes']

def get_all_users():
    table = _get_database().Table(os.environ['DB_TABLE_USER'])
    response = table.scan()
    return response['Items']

def get_otona_users():
    return get_users("adult")

def get_kodomo_users():
    return get_users("child")

def get_users(type):
    table = _get_database().Table(os.environ['DB_TABLE_USER'])
    response = table.scan(
        FilterExpression =Attr("Atype").eq(type)
    )
    return response['Items']


def get_user(user_id):
    table=_get_database().Table(os.environ['DB_TABLE_USER'])
    response = table.query(
        KeyConditionExpression=Key('id').eq(user_id)
    )
    items = response['Items']
    return items[0] if items else None

# user_id = 124522
# changes = { "id":"hogehgoe", "name": "かまだちきり", "password":"aaaaa", "type":"child","gakunen":"5"}
# changes = { "id":"hogehgoe", "name": "かまだちきり", "password":"aaaaa", "type":"adult","mail":"aaa@aaa.jp"}
def update_user(user_id, changes):
    table = _get_database().Table(os.environ['DB_TABLE_USER'])

    update_expression = []
    expression_attribute_values = {}
    if (changes["Atype"]=="child"):
        keys = ['id','Aname','Apassword','Atype','Agakunen']
    elif (changes["type"]=="adult"):
        keys = ['id','Aname','Apassword','Atype','Amail-address']

    for key in keys :
        if key in changes:
            update_expression.append(f"{key} = :{key[0:2]}")
            expression_attribute_values[f":{key[0:2]}"] = changes[key]

    result = table.update_item(
        Key={
            'id': user_id,
        },
        UpdateExpression='set ' + ','.join(update_expression),
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues='ALL_NEW'

    )
    return result['Attributes']


def delete_user(user_id):
    table = _get_database().Table(os.environ['DB_TABLE_USER'])
    result = table.delete_item(
        Key={
            'id':user_id,
        },
        ReturnValues='ALL_OLD'
    )
    return result['Attributes']