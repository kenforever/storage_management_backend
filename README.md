# 倉庫管理API

## /
沒有用

## /login
POST(username,password)

登入用

創造token

## /create_account
POST(username,password)

創造帳號

## /warehouse_init
GET

需要token

初始化 `warehouse.db`

## /add_object
POST(object_name,nickname,operator,object_type)

需要token

新增新欄位於 `warehouse.db` 

內容包括(nickname,object_name, add_time, operator, object_type)

## /get_object
POST(nickname)

需要token

根據 `nickname` 取得(nickname, object_name, add_time, operator, object_type)

## /del_object
POST(target)

需要token

根據 `target` 即 `nickname` 移除欄位

## /get_all_object
GET

需要token

取得 `warehouse` 內所有資料 包括(id, nickname, object_name, add_date, operator, object_type)

