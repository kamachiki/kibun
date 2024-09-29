# ここみる(kibun) インストール方法

#　フロントエンドのインストール方法
* https://snap.berkeley.edu/snap/snap.htmlを開き、kibun.xmlを開く
初期状態では、AWSにデプロイされたバックエンドと通信します。

* バックエンドを下記の方法で設定した場合、バックエンドのエンドポイントURLを、「初めの画面」のステージのスクリプトのURLに設定してください。


# バックエンドのインストール方法
* python3をインストールする
* openjdkをインストールする
* pip install awscli --upgrade --user でawscliをインストールする
* AWSのAccess Key IDとSecret access keyを入手する（権限はAdministratorAccess
* aws configureコマンドで上記を設定する
* pip install chalice　でchaliceをインストールする
* pip install boto3 でboto3をインストールする
* gh repo clone kamachiki/kibun　で展開
* etc/create-table.shを実行して、テーブルを作る
* （又は）https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html からアジアパシフィック（東京）リージョンのファイルをダウンロードする。
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar \ > -sharedDb -port 8001
で起動する
etc/create-table-local.sh を実行してテーブルを作る
* chalice deply --stage prod　でデプロイ
* （又は）chalice local --stage prod でローカル展開


