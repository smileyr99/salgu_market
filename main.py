from flask import Flask, render_template, session, url_for, request, redirect
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'sample_secret'
UPLOAD_FOLDER = './static/uploadImg/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def connectsql():
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='didhd1', db='roffle', charset='utf8')
    return conn


@app.route('/')
def main():
    return redirect(url_for('home_viewlist'))

@app.route('/home', methods=['GET', 'POST'])
def home_viewlist():
    if request.method == 'POST':
        search = request.form['search']
        search = '%'+search+'%'
        if 'userId' in session:
            userId = session['userId']
        else:
            userId = None
        # 대표이미지 title price
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, title, price, id from postdata WHERE keyword LIKE %s"

        cursor.execute(query, search)
        raw = cursor.fetchall()

        data_list = [list(row) for row in raw]
        print(data_list)

        cursor.close()
        conn.close()

        l = len(data_list)

        return render_template('home.html', logininfo=userId, datalist=data_list, l=l)
    else:
        if 'userId' in session:
            userId = session['userId']
        else:
            userId = None
        # 대표이미지 title price

        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, title, price, id from postdata order by id DESC"
        cursor.execute(query)
        raw = cursor.fetchall()

        data_list = [list(row) for row in raw]
        print(data_list)

        cursor.close()
        conn.close()

        return render_template('home.html', logininfo=userId, datalist=data_list)

@app.route('/detail/<id>', methods=['GET'])
def detail(id):
    conn = connectsql()
    cursor = conn.cursor()
    query = "select image1, image2, image3, keyword, title, price, state, user_id, content from postdata WHERE id = %s"
    value = id
    cursor.execute(query, value)
    tmp = cursor.fetchall()
    tmp1 = [list(row) for row in tmp]
    data_list = tmp1[0]
    print(data_list)

    cursor.close()
    conn.close()
    return render_template('detail.html', datalist=data_list)


@app.route('/mydetail', methods=['GET'])
def mydetail():
    if 'userId' in session:
        userId = session['userId']
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, image2, image3, keyword, title, price, user_id, content from postdata"
        cursor.execute(query)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_selling_sale.html', loginfo=userId, datalist=data_list)
    else:
        userId = None
        return render_template('mypageError.html', loginfo=userId)


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
            return redirect(url_for('home_viewlist'))
        else:
            return render_template('./login/loginError.html')
    else:
        return render_template('./login/login.html')


@app.route('/logout')
def logout():
    session.pop('userId', None)
    session.clear()
    return redirect(url_for('home_viewlist'))


@app.route('/regist/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        userid = request.form['id']
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
            query = "INSERT INTO userlist (user_id, user_pw) values (%s, %s)"
            value = (userid, userpw)
            cursor.execute(query, value)
            conn.commit()
            return render_template('./regist/registSuccess.html')

        cursor.close()
        conn.close()

    else:
        return render_template('./regist/regist.html')


@app.route('/mypage', methods=['GET'])
def mypage():
    if 'userId' in session:
        userId = session['userId']
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, image2, image3, keyword, title, price, state from postdata WHERE user_id = %s order by id DESC"
        cursor.execute(query, userId)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_selling.html', loginfo=userId, datalist=data_list)
    else:
        userId = None
        return render_template('mypageError.html', loginfo=userId)

@app.route('/mypage_sale', methods=['GET'])
def mypage_sale():
    if 'userId' in session:
        userId = session['userId']
        currentState = "판매중"
        value = (userId, currentState)
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, image2, image3, keyword, title, price, state from postdata WHERE user_id = %s and state = %s order by id DESC"
        cursor.execute(query, value)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_selling_sale.html', loginfo=userId, datalist=data_list)
    else:
        userId = None
        return render_template('mypageError.html', loginfo=userId)


@app.route('/mypage_finish_sale', methods=['GET'])
def mypage_finish_sale():
    if 'userId' in session:
        userId = session['userId']
        currentState = "판매완료"
        value = (userId, currentState)
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, image2, image3, keyword, title, price, state from postdata WHERE user_id = %s and state = %s order by id DESC"
        cursor.execute(query, value)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_selling_finishSale.html', loginfo=userId, datalist=data_list)
    else:
        userId = None
        return render_template('mypageError.html', loginfo=userId)


def image(img):
    filename = secure_filename(img.filename)
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        if 'userId' in session:
            userId = session['userId']
            userPw = session['userPw']

            usertitle = request.form['title']
            userkeyword = request.form['keyword']
            userprice = request.form['price']
            userphoneNum = request.form['phoneNum']
            usercontent = request.form['content']
            images = request.files.getlist("file[]")
            image1 = image(images[0])
            image2 = image(images[1])
            image3 = image(images[2])
            state = '판매중'

            conn = connectsql()
            cursor = conn.cursor()
            query = "INSERT INTO postdata (user_id, user_pw, title, keyword, price, phoneNum, content, image1, image2, image3, state) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            value = (userId, userPw, usertitle, userkeyword, userprice, userphoneNum, usercontent, image1, image2, image3, state)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('mypage'))
    else:
        if 'userId' in session:
            userId = session['userId']
            return render_template('write.html', logininfo=userId)


if __name__ == '__main__':
    app.run()
