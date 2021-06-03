# 倉庫管理API

## /
沒有用

## /login
POST(username,password)

登入用

創造access_token 與 refresh_token

return json `{access_token=access_token, refresh_token=refresh_token}`

## /create_account
POST(username,password)

創造帳號

return json `{"msg":msg}`

## /warehouse_init
GET

需要token

連接 `warehouse.db` 並初始化 `warehouse` 表

## /warehouse_record_init
GET

需要token

連接 `warehouse.db` 並初始化 `record` 表

## /add_object
POST(object_name,nickname,object_type)

需要token

新增新欄位於 `warehouse` 表 

內容包括(nickname, object_name, add_time, operator, object_type, lent)

*lent 預設為0

新增新欄位於 `record` 表

內容包括(nickname, date, operator, operation)

## /get_object
POST(nickname)

需要token

根據 `nickname` 取得(nickname, object_name, add_time, operator, object_type, lend)

## /remove_object
POST(target)

需要token

根據 `target` 即 `nickname` 移除欄位

新增新欄位於 `record` 表

內容包括(nickname, date, operator, operation)

## /lend_object
POST(target)

根據 target(即nickname) 改變 `lend` 內容

新增新欄位於 `record` 表

內容包括(nickname, date, operator, operation)

## /return_object
POST(target)

根據 target(即nickname) 改變 `lend` 內容

新增新欄位於 `record` 表

內容包括(nickname, date, operator, operation)

## /get_all_object
GET

需要token

取得 `warehouse` 內所有資料 包括(id, nickname, object_name, add_date, operator, object_type)

## /get_all_record
GET

需要token

取得 `record` 內所有資料 包括(id, nickname, date, operator, operation)