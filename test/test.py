import boto3
import csv

def save_dynamodb_table_to_csv(table_name, csv_file_name):
    """
    指定されたDynamoDBテーブルのデータをCSVファイルに保存する関数

    Args:
        table_name (str): DynamoDBテーブル名
        csv_file_name (str): 保存するCSVファイル名
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # テーブル全体のスキャンを実行
    response = table.scan()
    data = response['Items']

    # スキャン結果が全て取得できるまで繰り返す
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

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
print("全て終了")