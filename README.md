# ここみる（kibun) インストール方法

#ライブデモ
インストール済みのものは
https://y.knsn.cc/snap/snap.html#present:Username=tichan&ProjectName=kokomiru
こちらから見ることができます。

#　フロントエンドのインストール方法
* https\://snap.berkeley.edu/snap/snap.html
を開き、kokomiru.xmlを開く
開いた画面でクリックすると始まります
初期状態では、既にAWSにデプロイされたバックエンドと通信します。
デモアカウントは
子供：ID：ちきり　パスワード：おきほ
大人：ID：あさこ　パスワード：たけあき

* バックエンドを下記の方法で設定した場合、バックエンドのエンドポイントURLを、「初めの画面」のステージのスクリプトのURLに設定してください。

# バックエンドのインストール方法
* python3をインストールする
* openjdkをインストールする
* git bashをインストールする
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


