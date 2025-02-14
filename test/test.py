import boto3
import csv

from boto3.dynamodb.conditions import Key, Attr
import datetime
from decimal import *


dynamodb = boto3.resource('dynamodb', endpoint_url="http://127.0.0.1:8001")

def _changeTimestamp(keyname,data):
    if keyname in data:
        data[keyname + "_norm"] = datetime.datetime.fromtimestamp(float(data[keyname])).strftime("%Y%m%d%H%M")
    return data

def _changeListTimestamp(keyname,datalist):
    return list(map(lambda x: _changeTimestamp(keyname,x), datalist))

def save_dynamodb_table_to_csv(table_name, csv_file_name):
    """
    指定されたDynamoDBテーブルのデータをCSVファイルに保存する関数

    Args:
        table_name (str): DynamoDBテーブル名
        csv_file_name (str): 保存するCSVファイル名
    """

    table = dynamodb.Table(table_name)
    # テーブル全体のスキャンを実行
    response = table.scan()
    data = response['Items']

    # スキャン結果が全て取得できるまで繰り返す
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    data = _changeListTimestamp("Atimestamp",data)

    write_csv(csv_file_name,data,table_name)

def write_csv(csv_file_name,data,table_name):

    # CSVファイルに書き込み
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())

        writer = csv.DictWriter(csvfile, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(data)

    print(f"DynamoDBテーブル '{table_name}' のデータが '{csv_file_name}' に保存されました。")


save_dynamodb_table_to_csv("Yobikake","yobikake.csv")
save_dynamodb_table_to_csv("Users","user.csv")
save_dynamodb_table_to_csv("Comment","comment.csv")

save_dynamodb_table_to_csv("Kibun","kibun.csv")
"""
table = dynamodb.Table("Yobikake")
keyp =Key("Ayobikakerareru").eq("ちいちゃん") #& Key('Atimestamp').between(Decimal(str(1726827119.491559)), Decimal(str(1726927119.491559)))
fe =Attr("Akibun_timestamp").eq("1727483414")
# スキャンして期間内のデータを列挙
response = table.query(KeyConditionExpression = keyp,FilterExpression=fe)
data = response['Items']
write_csv("yobikake_between.csv",data,"Yobikake")

"""

print("全て終了")