from psycopg2 import connect


cnx = connect(user='postgres',
              password='coderslab',
              host='localhost',
              database='postgres')

cnx.autocommit = True
cursor = cnx.cursor()

sql = "CREATE DATABASE expensesreport;"
cursor.execute(sql)
cursor.close()
cnx.close()

cnx = connect(user='postgres',
              password='coderslab',
              host='localhost',
              database='expensesreport')

cnx.autocommit = True
cursor = cnx.cursor()

sql1 ="""CREATE TABLE category(
id serial PRIMARY KEY,
name varchar(255),
description varchar(255));
"""

sql2 ="""CREATE TABLE expenses(
id serial PRIMARY KEY,
category_id int,
name varchar(255),
description varchar(255),
price decimal(7,2),
date varchar(30),
quantity int,
FOREIGN KEY(category_id) REFERENCES category(id));
"""

cursor.execute(sql1)
cursor.execute(sql2)


cursor.close()
cnx.close()