from chalice import Chalice, NotFoundError,BadRequestError, ConflictError,UnauthorizedError
from chalicelib import database
from datetime import datetime,timedelta
from urllib.parse import unquote
from functools import reduce



app = Chalice(app_name='hobopy-backend')
app.debug = True
app.api.cors = True

# loginする
@app.route('/login', methods=['POST'], cors=True)
def login_user():
    changes = app.current_request.json_body
    user =database.get_user( changes["id"] )

    if user==None:
        return False

    if user["Apassword"]==changes["Apassword"]:
        session = database.create_session(user)
        return session
    else:
        return False

#/session/20250101のように表記する77
@app.route('/session/{before_date}',methods=['DELETE'],cors=True)
def session(before_date):
    ses = _login_check()
    post = app.current_request.json_body
    user = ses['user']
    if user == None or user["Atype"] != "admin":
        raise BadRequestError(f"bad user")
    return database.cleanup_session(datetime.strptime(before_date, '%Y%m%d'))

#ログインを検査する
def _login_check():
    if "Authorization" not in app.current_request.headers :
        raise UnauthorizedError("no bearer 1")
    bearer = app.current_request.headers["Authorization"].split(" ")
    if len(bearer) != 2:
        raise UnauthorizedError("no bearer 2")
    session_id = bearer[1]
    check = database.session_check(session_id)
    if check == None:
        raise UnauthorizedError(f"no session")
    user = database.get_user(check["Auser_id"])
    if user == None:
        raise UnauthorizedError(f"bad user")
    return {"user":user,"session":check}

def _checkKodomoToOtona(child_id,adult_id):
    kodomoOtona = database.get_kodomoToOtona(child_id)
    return reduce(lambda result, record: result or record["Aadult_id"] == adult_id, kodomoOtona, False)

def _changeTimestamp(keyname,data):
    if keyname in data:
        data[keyname+ "_date"] = datetime.fromtimestamp(float(data[keyname])).strftime("%Y%m%d%H%M")
    return data

def _changeListTimestamp(keyname,datalist):
    return list(map(lambda x: _changeTimestamp(keyname,x), datalist))

#ユーザーを作る、IDはかぶってはいけない
@app.route('/users', methods=['POST'], cors=True)
def create_user():
    user = app.current_request.json_body
        
    ans = database.create_user(user)
    if ans==None:
        raise ConflictError("id is conflict")
    else:
        return ans

#気分のデータを作成する
@app.route('/kibuns', methods=['POST'], cors=True)
def create_kibun():
    kibun = app.current_request.json_body
    session = _login_check()   
    return _changeTimestamp("Atimestamp",database.create_kibun(kibun,session["user"]["id"]))

#大人が子供の気分のデータをとってくる、または、公開されている気分のデータをとる
#mae:7 (何日前か)
@app.route('/kibuns/{child_id}/{mae}',methods=['GET'],cors=True)
def get_kibuns(child_id,mae):
    child_id = unquote(child_id)
    session = _login_check()
    kokai = True
    if child_id == session['user']["id"] or (session['user']['Atype'] == 'adult' and _checkKodomoToOtona(child_id,session["user"]["id"])):
        kokai = False
    now = datetime.now()
    ago = now - timedelta(days=int(mae))
    return _changeListTimestamp("Atimestamp",database.get_kibuns(child_id,ago,now,kokai))

#大人と子供のデータを作成する
@app.route('/kodomotootonas', methods=['POST'], cors=True)
def create_kodomotootona():
    kodomotootona = app.current_request.json_body
    session = _login_check()   
    return database.create_kodomotootona(kodomotootona,session["user"]["id"])

#大人と子供のデータをとる
@app.route('/kodomotootonas',methods=['GET'],cors=True)
def get_kodomotootonas():
    session = _login_check()
    return database.get_kodomoToOtona(session["user"]["id"])

#大人が、自分を指定した子供のリストを取る
@app.route('/otonatokodomos',methods=['GET'],cors=True)
def get_otonaToKodomos():
    session = _login_check()
    return database.get_otonaToKodomo(session["user"]["id"])
   

#大人と子供のデータを消す
@app.route('/kodomotootonas/{adult_id}', methods=['DELETE'],cors=True)
def delete_user(adult_id):
    session = _login_check()
    adult_id = unquote(adult_id)
    return database.delete_kodomoToOtona(session["user"]["id"],adult_id)

#よびかけのデータを作成する
@app.route('/yobikakes', methods=['POST'], cors=True)
def create_yobikake():
    kibun = app.current_request.json_body
    session = _login_check()   
    return _changeTimestamp("Atimestamp",database.create_yobikake(kibun,session["user"]["id"]))

#子供への呼びかけのデータをとる
#kibun_timestamp：該当する気分
@app.route('/yobikakes/{child_id}/{kibun_timestamp}',methods=['GET'],cors=True)
def get_yobikakes(child_id,kibun_timestamp):
    session = _login_check()
    child_id = unquote(child_id)

    return _changeListTimestamp("Atimestamp",database.get_yobikakesForKibun(child_id,kibun_timestamp,True))

#自分への呼びかけのデータをとる
@app.route('/myyobikakes/{mae}',methods=['GET'],cors=True)
def get_yobikakes(mae):
    session = _login_check()
    now = datetime.now()
    ago = now - timedelta(days=int(mae))
    return _changeListTimestamp("Atimestamp",database.get_yobikakes(session["user"]["id"],ago,now))


#よびかけを消す
#@app.route('/yobikake/{child_id}/{timestamp}', methods=['DELETE'], cors=True)
#def delete_yobikakes(child_id,timestamp):
 #   child_id = unquote(child_id)
  #  session = _login_check()
   # if session['user']['Atype'] != 'adult':
    #    raise BadRequestError("adult only")
    #return database.delete_yobikakes(child_id,timestamp)

#目標のデータを作成する
@app.route('/goals', methods=['POST'], cors=True)
def create_goal():
    session = _login_check()
    return _changeTimestamp("Atimestamp",database.create_goal(app.current_request.json_body,session["user"]["id"]))

#子供の目標のデータをとる
#mae:7 (何日前か)
@app.route('/goals/{child_id}/{mae}',methods=['GET'],cors=True)
def get_goals(child_id,mae):
    
    child_id = unquote(child_id)
    session = _login_check()
    
    if session['user']['Atype'] == 'adult' and _checkKodomoToOtona(child_id,session["user"]["id"]):
        now = datetime.now()
        ago = now - timedelta(days=int(mae))
        return _changeListTimestamp( "Atimestamp", database.get_goals(child_id,ago,now))
    else:
        return []

#@app.route('/goals/{timestamp}', methods=['DELETE'], cors=True)
#def delete_goals(timestamp):
    #session = _login_check()
    #return database.delete_goals(session["user"]['id'],timestamp)

#コメントのデータを作成する
@app.route('/comments', methods=['POST'], cors=True)
def create_comment():
    session = _login_check()   
    return _changeTimestamp("Atimestamp", database.create_comment(app.current_request.json_body,session["user"]))

#大人が子供へのコメントのデータをとる
#mae:7 (何日前か)
@app.route('/comments/{child_id}/{mae}',methods=['GET'],cors=True)
def get_comments(child_id,mae):
    child_id = unquote(child_id)
    session = _login_check()
    now = datetime.now()
    ago = now - timedelta(days=int(mae))
    return _changeListTimestamp( "Atimestamp",database.get_comments(child_id,ago,now))

#コメントを消す
#@app.route('/comments/{child_id}/{timestamp}', methods=['DELETE'], cors=True)
#def delete_comments(child_id,timestamp):
    #child_id = unquote(child_id)
    #session = _login_check()
    #if session['user']['Atype'] != 'adult':
        #raise BadRequestError("adult only")
    #return database.delete_comments(child_id,timestamp)

#すべてのユーザーをリストアップする
@app.route('/users', methods=['GET'], cors=True)
def get_all_users():
    session = _login_check()

    users = database.get_all_users()
    if users==None:
        return False
    for y in users:
        if "Apassword" in y:
            del y["Apassword"]
    return users


#すべてのおとなをリストアップする
@app.route('/otona_users', methods=['GET'], cors=True)
def get_otona_users():
    return _get_users("adult")
#すべての子供をリストアップする
@app.route('/kodomo_users', methods=['GET'], cors=True)
def get_kodomo_users():
    return _get_users("child")
#すべての人をリストアップする
def _get_users(type):
    session = _login_check()
    users = database.get_users(type)
    if users==None:
        return False
    for y in users:
        if "Apassword" in y:
            del y["Apassword"]
    return users

@app.route("/echo", methods=['GET'])
def echo():
    return {"echo":"echo"}

#ユーザーをとってくる（公開対象になっている大人のみ
@app.route('/kodomo/{user_id}', methods=['GET'], cors=True)
def get_kodomo(user_id):
    child_id = unquote(user_id)
    session = _login_check()
    if session['user']['Atype'] != 'adult':
        raise BadRequestError("adult only")
    kodomoOtona = database.get_kodomoToOtona(child_id)
    if reduce(lambda result, record: result or record["Aadult_id"] == session["user"]["id"], kodomoOtona, False):
        raise BadRequestError("kodomoToOtona List only")
    user =  database.get_user(child_id)
    if user==None:
        return False
    del user["Apassword"] 
    return user

#自分のユーザーをとってくる
@app.route('/user', methods=['GET'], cors=True)
def get_user():
    session = _login_check()
    user=session["user"]
    del user["Apassword"] 
    return user

#自分のユーザー情報を変更する
@app.route('/user', methods=['PUT'], cors=True)
def update_user():
    session = _login_check()
    changes = app.current_request.json_body
    return database.update_user(session["user"], changes)

#ユーザーを消去する（大人のみ）
#app.route('/users/{user_id}', methods=['DELETE'])
#def delete_user(user_id):
    #session = _login_check()
    #if session['user']['Atype'] != 'adult':
    #    raise BadRequestError("adult only")
    #return database.delete_user(user_id)
