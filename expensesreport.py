from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from flask import Flask, request
from flask import render_template
from psycopg2 import connect, ProgrammingError, IntegrityError
import xlsxwriter

app = Flask(__name__)


def create_connection():
    cnx = connect(user='postgres',
                  password='coderslab',
                  host='localhost',
                  database='expensesreport')

    cnx.autocommit = True
    cursor = cnx.cursor()

    return (cnx, cursor)


def close_connection(cnx, cursor):
    cursor.close()
    cnx.close()

def add_expanse(cursor, form_data):
    if form_data['name'] != "" and form_data['description'] != "":
        try:
            cursor.execute(f"INSERT INTO expenses(name, description, price, category_id, date, quantity) "
                           f"VALUES('{form_data['name']}', '{form_data['description']}', {form_data['price']}, "
                           f"{form_data['category_id']}, '{form_data['date']}', {form_data['quantity']});")
            s = "Expense added"
        except IntegrityError:
            return "There is no such category"
    else:
        s = "Invalid data"

    return s

def show_expenses(cursor):
    cursor.execute("SELECT * FROM expenses;")
    s = "<h3>Expenses:</h3><br>"
    for (id, category_id, name, desc, price, date, quantity) in cursor:
        s += f"Expense id: {id} &emsp;&emsp;&emsp; <a href='http://127.0.0.1:5000/del_exp/{id}'>Delete</a><br>"
        s += f"Name: {name}<br>"
        s += f"Description: {desc}<br>"
        s += f"Price for item: {price}<br>"
        s += f"Quantity: {quantity}<br>"
        s += f"Date: {date}<br>"
        s += f"Category id: {category_id}<br><br>"
    if s == "<h3>Expenses:</h3><br>":
        s = "There is no expenses yet :("

    return s


def add_category(cursor, form_data):
    if form_data['name'] != "" and form_data['description'] != "":
        cursor.execute(f"INSERT INTO category(name, description) VALUES('{form_data['name']}', '{form_data['description']}');")
        s = "Category added"
    else:
        s = "Invalid data"

    return s

def show_categories(cursor):
    cursor.execute("SELECT * FROM category;")
    s = "<h3>Categories:</h3><br>"
    for (id, name, desc) in cursor:
        s += f"ID: {id} &emsp;&emsp;&emsp; <a href='http://127.0.0.1:5000/del_cat/{id}'>Delete</a><br>"
        s += f"Name: {name}<br>"
        s += f"Description: {desc}<br><br>"
    if s == "<h3>Categories:</h3><br>":
        s = "There is no categories yet :("

    return s


@app.route("/", methods=["GET"])
def start():
    if request.method == "GET":
        return render_template('start.html')





@app.route("/del_cat/<int:id>", methods=["GET"])
def del_category(id):
    if request.method == "GET":
        (cnx, cursor) = create_connection()

        sql = f"DELETE FROM category WHERE id={id}"
        cursor.execute(sql)

        close_connection(cnx, cursor)

        return "Category deleted<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"

@app.route("/add_category", methods=["GET", "POST"])
def a_category():
    if request.method == "GET":
        return render_template('add_category.html')
    elif request.method == "POST":
        (cnx, cursor) = create_connection()
        try:
            s = add_category(cursor, request.form)

        except ProgrammingError:
            s = "Invalid data"

        close_connection(cnx, cursor)

        return s + "<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"

@app.route("/show_categories", methods=["GET", "POST"])
def s_category():
    if request.method == "GET":

        (cnx, cursor) = create_connection()

        s = show_categories(cursor)

        close_connection(cnx, cursor)

        return s + "<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"



@app.route("/add_expense", methods=["GET", "POST"])
def a_expanse():
    if request.method == "GET":
        return render_template('add_expense.html')
    elif request.method == "POST":
        (cnx, cursor) = create_connection()
        try:
            s = add_expanse(cursor, request.form)

        except ProgrammingError:
            s = "Invalid data"

        close_connection(cnx, cursor)

        return s+"<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"

@app.route("/show_expenses", methods=["GET", "POST"])
def s_expenses():
    if request.method == "GET":

        (cnx, cursor) = create_connection()

        s = show_expenses(cursor)

        close_connection(cnx, cursor)

        return s + "<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"

@app.route("/del_exp/<int:id>", methods=["GET"])
def del_expense(id):
    if request.method == "GET":
        (cnx, cursor) = create_connection()

        sql = f"DELETE FROM expenses WHERE id={id}"
        cursor.execute(sql)

        close_connection(cnx, cursor)

        return "Expense deleted<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"


@app.route("/show_report", methods=["GET"])
def show_report():

    (cnx, cursor) = create_connection()

    sql = f"SELECT id FROM category;"
    cursor.execute(sql)
    categories = []
    for cat_id in cursor.fetchall():
        categories.append(cat_id[0])

    total_table = []
    for id in categories:
        total_price = 0
        cursor.execute(f"SELECT quantity, price FROM expenses WHERE category_id = {id}")
        for (quant, price) in cursor.fetchall():
            total_price += int(quant)*int(price)

        if total_price != 0:
            total_table.append(id)
            total_table.append(total_price)
    x = int(len(total_table))


    report = "<center>EXPENSES REPORT</center><br><br>"
    for i in range(x//2):
        cursor.execute(f"SELECT name FROM category WHERE id = {total_table[i*2]}")
        name1 = cursor.fetchone()[0]
        report += f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{name1}\'s:</b><br>"
        cursor.execute(f"SELECT * FROM expenses WHERE category_id = {total_table[i*2]};")
        for (id, category_id, name, desc, price, date, quantity) in cursor:
            report += f"Expense id: {id}<br>"
            report += f"Name: {name}<br>"
            report += f"Description: {desc}<br>"
            report += f"Price for item: {price}$<br>"
            report += f"Quantity: {quantity}<br>"
            report += f"Date: {date}<br>"
            report += f"Category id: {category_id}<br>"
            total_price = price * quantity
            report += f"All items cost: {total_price}$<br><br>"
        report += f"Your total {name1}'s expenses is: {total_table[i*2+1]}$<br><br><br>"

    close_connection(cnx, cursor)

    report += "<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"

    return report


@app.route("/make_pdf", methods=["GET"])
def make_pdf():
    if request.method == "GET":

        (cnx, cursor) = create_connection()

        sql = f"SELECT id FROM category;"
        cursor.execute(sql)
        categories = []
        for cat_id in cursor.fetchall():
            categories.append(cat_id[0])

        total_table = []
        for id in categories:
            total_price = 0
            cursor.execute(f"SELECT quantity, price FROM expenses WHERE category_id = {id}")
            for (quant, price) in cursor.fetchall():
                total_price += int(quant) * int(price)

            if total_price != 0:
                total_table.append(id)
                total_table.append(total_price)
        x = int(len(total_table))

        doc = SimpleDocTemplate("ExpensesReport.pdf", pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=28)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=24))
        styles.add(ParagraphStyle(name='category', fontSize=16))

        cont = []
        text = "EXPENSES REPORT"
        cont.append(Paragraph(text, styles["center"]))
        cont.append(Spacer(1, 100))

        for i in range(x // 2):
            cursor.execute(f"SELECT name FROM category WHERE id = {total_table[i*2]}")
            name1 = cursor.fetchone()[0]
            text = f"{name1}\'s:"
            cont.append(Paragraph(text, styles["category"]))
            cont.append(Spacer(1, 30))

            cursor.execute(f"SELECT * FROM expenses WHERE category_id = {total_table[i*2]};")
            for (id, category_id, name, desc, price, date, quantity) in cursor:
                text = f"Expense id: {id}"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(111, 10))
                text = f"Name: {name}"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(1, 10))
                text = f"Description: {desc}"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(1, 10))
                text = f"Price for item: {price}$"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(1, 10))
                text = f"Quantity: {quantity}"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(1, 10))
                text = f"Date: {date}"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(1, 10))
                text = f"Category id: {category_id}"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(1, 10))
                total_price = price * quantity
                text = f"All items cost: {total_price}$"
                cont.append(Paragraph(text, styles["Normal"]))
                cont.append(Spacer(1, 30))
            text = f"Your total {name1}'s expenses is: {total_table[i*2+1]}$"
            cont.append(Paragraph(text, styles["category"]))
            cont.append(Spacer(1, 50))

        close_connection(cnx, cursor)
        doc.build(cont)

        return "Done :)<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"


@app.route("/make_xlsx", methods=["GET"])
def make_xlsx():

    (cnx, cursor) = create_connection()

    sql = f"SELECT id FROM category;"
    cursor.execute(sql)
    categories = []
    for cat_id in cursor.fetchall():
        categories.append(cat_id[0])

    total_table = []
    for id in categories:
        total_price = 0
        cursor.execute(f"SELECT quantity, price FROM expenses WHERE category_id = {id}")
        for (quant, price) in cursor.fetchall():
            total_price += int(quant) * int(price)

        if total_price != 0:
            total_table.append(id)
            total_table.append(total_price)
    x = int(len(total_table))


    reports = xlsxwriter.Workbook('ExpensesReport.xlsx')
    report = reports.add_worksheet()

    row = 4
    col = 0

    report.write(2, 2, 'Expenses Report')
    for i in range(x // 2):
        cursor.execute(f"SELECT name FROM category WHERE id = {total_table[i*2]}")
        name = cursor.fetchone()[0]
        report.write(row, col+1, f'{name}\'s')
        row += 1
        total_category = 0
        cursor.execute(f"SELECT * FROM expenses WHERE category_id = {total_table[i*2]};")
        for (id, category_id, name, desc, price, date, quantity) in cursor:
            report.write(row, col, 'Expense id:')
            report.write(row, col + 1, f'{id}')
            row += 1
            report.write(row, col, 'Name:')
            report.write(row, col + 1, f'{name}')
            row += 1
            report.write(row, col, 'Description:')
            report.write(row, col + 1, f'{desc}')
            row += 1
            report.write(row, col, 'Item price:')
            report.write(row, col + 1, f'{price}')
            row += 1
            report.write(row, col, 'Quantity:')
            report.write(row, col + 1, f'{quantity}')
            row += 1
            report.write(row, col, 'Date:')
            report.write(row, col + 1, f'{date}')
            row += 1
            report.write(row, col, 'Category id:')
            report.write(row, col + 1, f'{category_id}')
            row += 1
            report.write(row, col, 'Total items:')
            total_price = price*quantity
            total_category += total_price
            report.write(row, col + 1, f'{total_price}')
            row += 2

        report.write(row, col, 'Total category:')
        report.write(row, col + 1, f'{total_category}')
        row += 3


    reports.close()

    return "Done :)<br><br><a href='http://127.0.0.1:5000/' style=text-decoration:none;>Go to Menu</a>"


if (__name__) == "__main__":
    app.run()(Debug=True)
