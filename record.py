# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

def add_record(nickname, operator, operation):
    database_connect = sqlite3.connect('warehouse.db')
    c = database_connect.cursor()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")   #  date and time, format shoud be like year-month-day hour:minue:second
    date = dt_string
    c.execute("insert into record values(?,?,?,?)",(nickname,date,operator,operation))
    database_connect.commit()
    database_connect.close()