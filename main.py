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
        query = "select image1, title, price, id, user_id from postdata WHERE keyword LIKE %s"

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
        query = "select image1, title, price, id, user_id from postdata order by id DESC"
        cursor.execute(query)
        raw = cursor.fetchall()

        data_list = [list(row) for row in raw]
        print(data_list)

        cursor.close()
        conn.close()

        return render_template('home.html', logininfo=userId, datalist=data_list)


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


@app.route('/detail/<idx>', methods=['GET'])
def detail(idx):
    if 'userId' in session:
        userId = session['userId']
    else:
        userId = None
    print(idx)

    conn = connectsql()
    cursor = conn.cursor()
    query = "select image1, image2, image3, keyword, title, price, state, user_id,  content, id from postdata WHERE id = %s"
    value = idx
    cursor.execute(query, value)
    tmp = cursor.fetchall()
    tmp1 = [list(row) for row in tmp]
    if len(tmp1) != 0:
        data_list = tmp1[0]
    else:
        data_list = 0

    post_user_id=data_list[7]

    lg = 0  # logged in or not
    flag = 0 #followed or not followed
    if userId!=None:
        lg = 1
        query1 = "SELECT following_id FROM _following WHERE user_id = %s"
        value1 = userId
        cursor.execute(query1, value1)
        tmp2 = cursor.fetchall()
        followings = [list(row) for row in tmp2]
        print(followings)
        cursor.close()
        conn.close()

        flag = 0
        cnt = 0
        if len(followings) == 0:
            return render_template('detail.html', logininfo=userId, datalist=data_list, posting_id=data_list[7], flag=flag, lg=lg)
        else:
            for row in followings:
                if row[0] == post_user_id:
                    flag = 1
                    break
                else:
                    cnt = cnt + 1
        if cnt == len(followings):
            flag = 0

    return render_template('detail.html', logininfo=userId, datalist=data_list, posting_id=data_list[7], flag=flag, lg=lg)


@app.route('/following_detail/<idx>', methods=['GET'])
def following_detail(idx):
    if 'userId' in session:
        userId = session['userId']
    else:
        userId = None
    print(idx)

    conn = connectsql()
    cursor = conn.cursor()
    query = "select image1, image2, image3, keyword, title, price, state, user_id, content from postdata WHERE id = %s"
    value = (idx)
    cursor.execute(query, value)
    tmp = cursor.fetchall()
    tmp1 = [list(row) for row in tmp]
    if len(tmp1) != 0:
        data_list = tmp1[0]
    else:
        data_list = 0

    post_user_id=data_list[7]

    lg = 0  # logged in or not
    flag = 0 #followed or not followed
    if userId!=None:
        lg = 1
        query1 = "SELECT following_id FROM _following WHERE user_id = %s"
        value1 = userId
        cursor.execute(query1, value1)
        tmp2 = cursor.fetchall()
        followings = [list(row) for row in tmp2]
        print(followings)
        cursor.close()
        conn.close()

        flag = 0
        cnt = 0
        if len(followings) == 0:
            return render_template('following_detail.html', logininfo=userId, datalist=data_list, posting_id=data_list[7], flag=flag, lg=lg)
        else:
            for row in followings:
                if row[0] == post_user_id:
                    flag = 1
                    break
                else:
                    cnt = cnt + 1
        if cnt == len(followings):
            flag = 0

    return render_template('following_detail.html', logininfo=userId, datalist=data_list, posting_id=data_list[7], flag=flag, lg=lg)


@app.route('/mydetail/<id>', methods=['GET'])
def mydetail(id):
    if 'userId' in session:
        userId = session['userId']
    else:
        userId = None
    conn = connectsql()
    cursor = conn.cursor()
    query = "select id, image1, image2, image3, keyword, title, price, state, content from postdata WHERE id = %s"
    value = id
    cursor.execute(query, value)
    tmp = cursor.fetchall()
    tmp1 = [list(row) for row in tmp]
    data_list = tmp1[0]
    print(data_list)

    cursor.close()
    conn.close()
    return render_template('mydetail.html',  logininfo=userId, datalist=data_list)


@app.route('/mypage', methods=['GET'])
def mypage():
    if 'userId' in session:
        userId = session['userId']
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, image2, image3, keyword, id, title, price, state from postdata WHERE user_id = %s order by id DESC"
        cursor.execute(query, userId)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_selling.html', logininfo=userId, datalist=data_list)
    else:
        userId = None
        return render_template('mypageError.html', logininfo=userId)


@app.route('/mypage_sale', methods=['GET'])
def mypage_sale():
    if 'userId' in session:
        userId = session['userId']
        currentState = "판매중"
        value = (userId, currentState)
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, image2, image3, keyword, id, title, price, state from postdata WHERE user_id = %s and state = %s order by id DESC"
        cursor.execute(query, value)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_selling_sale.html', logininfo=userId, datalist=data_list)
    else:
        userId = None
        return render_template('mypageError.html', logininfo=userId)


@app.route('/mypage_finish_sale', methods=['GET'])
def mypage_finish_sale():
    if 'userId' in session:
        userId = session['userId']
        currentState = "판매완료"
        value = (userId, currentState)
        conn = connectsql()
        cursor = conn.cursor()
        query = "select image1, image2, image3, keyword, id, title, price, state from postdata WHERE user_id = %s and state = %s order by id DESC"
        cursor.execute(query, value)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_selling_finishSale.html', logininfo=userId, datalist=data_list)
    else:
        userId = None
        return render_template('mypageError.html', logininfo=userId)


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


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        if 'userId' in session:
            userId = session['userId']
            userPw = session['userPw']

            usertitle = request.form['title']
            userkeyword = request.form['keyword']
            userprice = request.form['price']
            userphoneNum = request.form['phoneNum']
            usercontent = request.form['content']
            state = request.form['state']
            images = request.files.getlist("file[]")
            image1 = image(images[0])
            image2 = image(images[1])
            image3 = image(images[2])

            conn = connectsql()
            cursor = conn.cursor()
            query = "UPDATE postdata SET image1 = %s, image2 = %s, image3 = %s, state = %s, title = %s, keyword = %s, price = %s, phoneNum = %s, content = %s WHERE id = %s"
            value = (image1, image2, image3, state, usertitle, userkeyword, userprice, userphoneNum, usercontent, id)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('mypage'))
    else:
        if 'userId' in session:
            userId = session['userId']
            conn = connectsql()
            cursor = conn.cursor()
            query = "select id, keyword, title, price, state, phoneNum, content from postdata WHERE id = %s"
            value = id
            cursor.execute(query, value)
            tmp = cursor.fetchall()
            tmp1 = [list(row) for row in tmp]
            data_list = tmp1[0]
            print(data_list)

            cursor.close()
            conn.close()
            return render_template('edit.html', logininfo=userId, datalist=data_list)

@app.route('/follow/<idx>')
def follow(idx):
    if 'userId' in session:
        userId = session['userId']
        userPw = session['userPw']
        conn = connectsql()
        cursor = conn.cursor()
        query_ = "select user_id from postdata where id=%s"
        cursor.execute(query_, idx)
        tmp = cursor.fetchall()
        post_userid_ = [list(row) for row in tmp]
        post_userid1 = post_userid_[0]
        post_userid = post_userid1[0]

        print(post_userid)

        value = (userId, userPw, post_userid)
        query = "insert into _following (user_id, user_pw, following_id) values (%s, %s, %s)"
        cursor.execute(query, value)
        conn.commit()

        cursor.close()
        conn.close()

        return render_template('detail_follow_succeed.html', idx_post=idx, following=post_userid)
    else:
        return render_template('followError.html')

@app.route('/unfollow/<idx>')
def unfollow(idx):
    if 'userId' in session:
        userId = session['userId']
        userPw = session['userPw']
        conn = connectsql()
        cursor = conn.cursor()
        query_ = "select user_id from postdata where id=%s"
        cursor.execute(query_, idx)
        tmp = cursor.fetchall()
        post_userid_ = [list(row) for row in tmp]
        post_userid1 = post_userid_[0]
        unfollowing = post_userid1[0]

        q_clear = "set sql_safe_updates=0"
        cursor.execute(q_clear)
        value = (userId, userPw, unfollowing)
        query = "delete from _following where user_id=%s and user_pw=%s and following_id=%s"
        cursor.execute(query, value)
        conn.commit()

        cursor.close()
        conn.close()

        return render_template('detail_unfollow_succeed.html', unfollowing=unfollowing, idx_post=idx)
    else:
        return render_template('followError.html')

@app.route('/mypage_following_list')
def mypage_following_list():
    if 'userId' in session:
        conn = connectsql()
        cursor = conn.cursor()
        userId = session['userId']
        query = "select following_id from _following where user_id = %s"
        cursor.execute(query, userId)
        tmp = cursor.fetchall()
        data_list = [list(row) for row in tmp]
        print(data_list)

        cursor.close()
        conn.close()

        return render_template('mypage_following_list.html', logininfo=userId, followings=data_list)

@app.route('/mypage_following/<user_id>')
def mypage_following(user_id):
    if 'userId'in session:
        conn = connectsql()
        cursor = conn.cursor()
        userId = session['userId']
        query = "select image1, image2, image3, keyword, title, price, state, id from postdata WHERE user_id = %s order by id DESC"
        cursor.execute(query, user_id)
        data_list = cursor.fetchall()
        print(data_list)

        cursor.close()
        conn.close()
        return render_template('mypage_following.html', logininfo=userId, datalist=data_list, id=user_id)


if __name__ == '__main__':
    app.run()
