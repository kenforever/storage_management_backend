# -*- coding: utf-8 -*-
import sqlite3
import flask
from flask import request, json, jsonify
from flask_jwt_extended.utils import create_access_token, create_refresh_token, get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta
from flask_cors import CORS
import os
from flask_cors import cross_origin
from record import add_record

data = json.load(open("./config.json"))
print(data)
secret_key = data['Secret_key']
access_token_expires = data['access_token_expires']
refresh_token_expires = data['refresh_token_expires']

app = flask.Flask(__name__)
CORS(app, cors_allowed_origins='*')
jwt = JWTManager()
app.config["JWT_SECRET_KEY"] = secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=access_token_expires)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=refresh_token_expires)
jwt.init_app(app)


@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello Flask!</h1>"

@app.route('/login', methods=['POST'])
def login(): 
    username = request.values['username']
    password = request.values['password'] 

    database_connect = sqlite3.connect('account.db')
    c = database_connect.cursor()
    data = c.execute("SELECT password from account where username=?",(username,))
    correct_password = ""
    for row in data:                    #  check password 
        correct_password = row[0]
    if correct_password == "":          #  database dont have this username
        database_connect.commit()
        database_connect.close()
        return jsonify({"msg": "username or password wrong!"}), 401
    if correct_password == password:    #  username and password have no problem
        access_token = create_access_token(identity=username)       # create token
        database_connect.commit()
        database_connect.close()
        refresh_token = create_refresh_token(identity="example_user")
        return jsonify(access_token=access_token, refresh_token=refresh_token)
    else:
        database_connect.commit()       #  database have this username but password wrong 
        database_connect.close()
        return jsonify({"msg": "username or password wrong!"}), 401

@app.route('/create_account', methods=['POST'])
def create_account(): 
    username = request.values['username']
    password = request.values['password'] 
    database_connect = sqlite3.connect('account.db')
    c = database_connect.cursor()

    duplicate_check = c.execute("SELECT username from account")             #  check if there have any duplicate username
    for row in duplicate_check:
        if row[0] == username :
            database_connect.commit()
            database_connect.close()
            return jsonify({"msg": "there have a duplicate username"}), 401

    c.execute("insert into account values(?,?)",(username,password))        #  insert username and password into database
    database_connect.commit()
    database_connect.close()
    return jsonify({"msg": "finish"}), 200

@app.route('/warehouse_init', methods=['GET'])
@cross_origin()
@jwt_required()
def init():
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    #  warehouse database initialization 
    #  table warehouse have 
    #  nickname     text    nickname, should be unique in table warehouse
    #  object_name  text    object name, the name of the object 
    #  add_date     text    object add date, format shoud be like year-month-day hour:minue:second 
    #  operator     text    operator, adder of the object, should be their username 
    #  object_type  text    object type, type of object
    #  lend         int     lend, 0 mean have not been borrow, 1 mean already have been borrowed
    try:
        c.execute('''CREATE TABLE warehouse(nickname text, object_name text, add_date text, operator text, object_type text, lend INTEGER)''')
    except Exception as e:
        database_connect.commit()
        database_connect.close()
        return e
    database_connect.commit()
    database_connect.close()
    return jsonify({"msg": "finish"}), 200

@app.route('/warehouse_record_init', methods=['GET'])
@cross_origin()
@jwt_required()
def record_init():
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    #  warehouse record database initialization 
    #  table record have 
    #  nickname     text    nickname, should be unique in table warehouse, not uniqle in talbe record
    #  date         text    object operation date, format shoud be like year-month-day hour:minue:second 
    #  operator     text    operator, operator of the object, should be their username 
    #  operation    int     operation, what user do, only have 4 type of data: add, remove, lend, return
    c.execute('''CREATE TABLE record(nickname text,date text, operator text, operation text)''')
    database_connect.commit()
    database_connect.close()
    return jsonify({"msg": "finish"}), 200

@app.route('/add_object', methods=['POST'])
@jwt_required()
@cross_origin()
def add_object():
    current_user = get_jwt_identity()               #  get current username
    object_name = request.values['object_name']
    nickname = request.values['nickname']
    operator = current_user
    object_type = request.values["object_type"]

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")   #  date and time, format shoud be like year-month-day hour:minue:second
    add_date = dt_string
    
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()

    duplicate_check = c.execute("SELECT nickname  from warehouse")      #  duplicate_check, check if there have object that have the same nickname
    for row in duplicate_check:
        if row[0] == nickname :
            database_connect.commit()
            database_connect.close()
            return jsonify({"msg": "there have a duplicate object"}), 401
    try:
        c.execute("insert into warehouse values(?,?,?,?,?,?)",(nickname,object_name,add_date,operator,object_type,0))
    except Exception as e:
        return jsonify({"msg":str(e)})
    database_connect.commit()
    database_connect.close()
    add_record(nickname,current_user,"add_object")
    return jsonify({"msg": "finish"}), 200

@app.route('/get_object', methods=['POST'])
@cross_origin()
@jwt_required()
def get_object():
    target = request.values['target']
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    data = c.execute("SELECT * from warehouse where nickname=?",(target,))
    return_data =[]
    for row in data:
        row_data = {}
        row_data['nickname'] = row[0]
        row_data['object_name'] = row[1]
        row_data['add_date'] = row[2]
        row_data['operator'] = row[3]
        row_data['object_type'] = row[4]
        row_data['lend'] = row[5]
        return_data.append(row_data)

    database_connect.commit()
    database_connect.close()
    if return_data == []:
        return jsonify({"msg": "dont have this object"}), 401
    return jsonify(return_data), 200

@app.route('/remove_object', methods=['POST'])
@cross_origin()
@jwt_required()
def remove_object():
    target = request.values['target']
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    avaliable_check=c.execute("DELETE from warehouse where nickname=?;",(target,))
    rows = avaliable_check.fetchall()
    print(rows)
    if rows == []:
        return jsonify({"msg": "we dont have this object!"}), 404

    database_connect.commit()
    database_connect.close()
    current_user = get_jwt_identity()    
    add_record(target,current_user,"remove_object")
    return jsonify({"msg": "finish"}), 200

@app.route('/lend_object', methods=['POST'])
@jwt_required()
@cross_origin()
def lend_object():
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    target = request.values['target']

    avaliable_check = c.execute("SELECT nickname from warehouse where nickname=?",(target,))
    rows = avaliable_check.fetchall()
    print(rows)
    if rows == []:
        return jsonify({"msg": "we dont have this object!"}), 404

    lend_check = c.execute("SELECT lend from warehouse where nickname=?",(target,))     #  check if the object have been borrow
    for row in lend_check:
        if row[0] == 1:
            database_connect.commit()
            database_connect.close()
            return jsonify({"msg": "object have been borrow!"}), 401
        
    c.execute("UPDATE warehouse set lend = 1 where nickname=?",(target,))
    data = c.execute("SELECT * from warehouse where nickname=?",(target,))

    database_connect.commit()
    database_connect.close()
    current_user = get_jwt_identity()    
    add_record(target,current_user,"lend_object")
    return jsonify({"msg": "finish"}), 200

@app.route('/return_object', methods=['POST'])
@jwt_required()
@cross_origin()
def return_object():
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    target = request.values['target']

    avaliable_check = c.execute("SELECT nickname from warehouse where nickname=?",(target,))
    rows = avaliable_check.fetchall()
    print(rows)
    if rows == []:
        return jsonify({"msg": "we dont have this object!"}), 404

    lend_check = c.execute("SELECT lend from warehouse where nickname=?",(target,))     #  check if the object have been borrow
    for row in lend_check:
        if row[0] == 0:
            database_connect.commit()
            database_connect.close()
            return jsonify({"msg": "object have not been borrow!"}), 401
        
    c.execute("UPDATE warehouse set lend = 0 where nickname=?",(target,))
    data = c.execute("SELECT * from warehouse where nickname=?",(target,))

    database_connect.commit()
    database_connect.close()
    current_user = get_jwt_identity()    
    add_record(target,current_user,"return_object")
    return jsonify({"msg": "finish"}), 200

@app.route('/get_all_object', methods=['GET'])
@cross_origin()
@jwt_required()
def get_all_object():
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    all_data = c.execute("SELECT rowid, * from warehouse")
    return_data = []
    for row in all_data:
        row_data = {}
        row_data['id'] = row[0]
        row_data['nickname'] = row[1]
        row_data['object_name'] = row[2]
        row_data['add_date'] = row[3]
        row_data['operator'] = row[4]
        row_data['object_type'] = row[5]
        row_data['lend'] = row[6]
        return_data.append(row_data)
        
    database_connect.commit()
    database_connect.close()
    return jsonify(return_data),200

@app.route('/get_all_record', methods=['GET'])
@cross_origin()
@jwt_required()
def get_all_record():
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    all_data = c.execute("SELECT rowid, * from record")
    return_data = []
    for row in all_data:
        row_data = {}
        row_data['id'] = row[0]
        row_data['nickname'] = row[1]
        row_data['date'] = row[2]
        row_data['operator'] = row[3]
        row_data['operation'] = row[4]
        return_data.append(row_data)
        
    database_connect.commit()
    database_connect.close()
    return jsonify(return_data),200

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)