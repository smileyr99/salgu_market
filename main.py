from flask import Flask, render_template, session, url_for, request, redirect
import pymysql

app = Flask(__name__)
app.secret_key = 'sample_secret'

def connectsql():
    conn = pymysql.connect(host='127.0.0.1', user = 'root', passwd = 'didhd1', db = 'roffle', charset='utf8')
    return conn

@app.route('/')
def main():
    return render_template('/home.html')


@app.route('/home')
def home():
    if 'userId' in session:
        userId = session['userId']
        return render_template('home.html', logininfo = userId)
        print('userId', userId)
    else:
        userId = None
        return render_template('home.html', logininfo = userId)
        print('userId', userId)


@app.route('/login/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['id']
        userpw = request.form['pw']

        logininfo = request.form['id']
        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM userlist WHERE user_id = %s AND user_pw = %s"
        value = (userid, userpw)
        cursor.execute(query, value)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        for row in data:
            data = row[0]

        if data:
            session['userId'] = request.form['id']
            session['userPw'] = request.form['pw']
            return render_template('home.html', logininfo=logininfo)
        else:
            return render_template('./login/loginError.html')
    else:
        return render_template('./login/login.html')


@app.route('/logout')
def logout():
    session.pop('userId', None)
    return redirect(url_for('home'))


@app.route('/regist/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        userid = request.form['id']
        usernickname = request.form['nickname']
        userpw = request.form['pw']

        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM userlist WHERE user_id = %s"
        value = userid
        cursor.execute(query, value)
        data = (cursor.fetchall())
        if data:
            conn.rollback()
            return render_template('./regist/registError.html')
        else:
            query = "INSERT INTO userlist (user_id, user_nickname, user_pw) values (%s, %s, %s)"
            value = (userid, usernickname, userpw)
            cursor.execute(query, value)
            conn.commit()
            return render_template('./regist/registSuccess.html')

        cursor.close()
        conn.close()

    else:
        return render_template('./regist/regist.html')




if __name__ == '__main__':
    app.run()
