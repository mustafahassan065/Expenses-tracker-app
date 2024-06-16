from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import re
import secrets
import os
import mysql.connector
from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
mysql = MySQL(app)

app.config['MAIL_SERVER'] = ''
app.config['MAIL_PORT'] = 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = 'kzbfiitdknsxwrym'
app.config['MAIL_DEFAULT_SENDER'] = ''

mail = Mail(app)

def generate_verification_token():
    return secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('expensefront.html')

@app.route('/enter', methods=['GET', 'POST'])
def enter():
     message = ''
     if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM login WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['data'] = user[1] 
            session['name'] = user[2]
            session['email'] = user[3]
            message = 'Welcome to profile page!'
            return render_template('expenseform.html' , DATA_ID = user[1] , message = message)
        else:
            message = 'Please enter correct email / password !'
     return render_template('expenseEntry.html' , message = message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('data', None)
    session.pop('email', None)
    return redirect(url_for('enter'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        data = request.form['data']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM login WHERE email = %s ', (email,))
        profile = cur.fetchone()
        if profile:
             message = 'Already account exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not name or not email or not password or not data:
             message = "Please fill out the form!"
        else:
         cur.execute("INSERT INTO login (name, email,data, password) VALUES (%s, %s,%s, %s )", (name, email,data, password))
         mysql.connection.commit()
         cur.close()
         message = Message("Welcome to our Website!", recipients=[email])
         message.body = f"Dear {name},\n\nWelcome to our website! Thank you for signing up."
         mail.send(message)
         message = 'Your Account is created!'
         return  render_template('signup.html', message= message)

    return render_template('signup.html')

@app.route('/add' , methods = ['POST'])
def add():
    message = 'Welcome to your profile page!'
    if request.method == 'POST' and 'category' in request.form and 'description' in request.form and 'amount' in request.form:
     data = request.form['data']
     category = request.form['category'] 
     description = request.form['description']   
     amount = request.form['amount']
     if amount.strip() and amount.replace('.', '', 1).isdigit(): 
      Time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      cursor = mysql.connection.cursor()
      cursor.execute("INSERT INTO cash (data , category,description,amount ,Time ) VALUES(%s,%s,%s,%s,%s )" , (data,category,description,amount,Time))
      mysql.connection.commit()
      cursor.close()
      message = 'Your expense is added succesfully!'
     else:
            message = 'Amount must be a valid numeric value.'
    return render_template('expenseform.html',message=message)



@app.route('/show')
def show():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM cash WHERE data = %s', (session['data'],))
    data = cursor.fetchall()
    links = []
    totalexpenses = 0
    for index, row in enumerate(data, start=1):
         link = {
             'id' : row[0],
             'data' : row[1],
            'category': row[2],
            'description': row[3],
            'amount': row[4],
             'Time': row[5]
        }
         links.append(link)
         totalexpenses+= row[4] if row[4] is not None else 0
    return render_template('expenseshow.html' ,totalexpenses=totalexpenses, links = links)
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM cash WHERE id = %s AND data = %s', (id, session['data']))
    mysql.connection.commit()
    cursor.execute("SET @count = 0;")
    cursor.execute("UPDATE cash SET id = @count:= @count + 1;")
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('show'))

@app.route('/update/<int:id>', methods=['GET'])
def update(id):
   
    return redirect(url_for('update_page', id=id))


@app.route('/update_page/<int:id>', methods=['GET', 'POST'])
def update_page(id):
    message = 'Here , You can update!'
    if request.method == 'POST':
        message = ''
        category = request.form['category']
        description = request.form['description']
        amount = request.form['amount']
        
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE cash SET category = %s, description = %s, amount = %s WHERE id = %s AND data = %s', (category, description, amount, id, session['data']))
        mysql.connection.commit()
        cursor.close()
        message = 'your data is updated!'
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM cash WHERE id = %s AND data = %s', (id, session['data']))
    row = cursor.fetchone()
    data = {} 
    if row:
        columns = [col[0] for col in cursor.description]
        data = dict(zip(columns, row))
    cursor.close()
    return render_template('update.html' ,data=data, message=message)
    
        
  


if __name__ == '__main__':
    app.run(debug=True)

