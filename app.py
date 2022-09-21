# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, make_response, redirect

app = Flask(__name__)

import hashlib
import jwt
import datetime

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.wtjymgq.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'TEAM'

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/MainPage')
def main_page():
    # nickname = request.args.get('nickname')
    # id = request.args.get('id')

    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # print(payload['id'])

        user = db.user.find_one({'id': payload['id']})

        return render_template('MainPage.html', id=payload['id'], nickname=user['nick'])
    except jwt.ExpiredSignatureError:
        return redirect("http://localhost:5000/")
    except jwt.exceptions.DecodeError:
        return redirect("http://localhost:5000/")


@app.route('/udongdong/posts', methods=["GET"])
def posts_list():
    posts_list = list(db.post_content.find({}, {'_id': False}))

    return jsonify({'posts_list': posts_list})


@app.route('/udongdong/one_post', methods=["POST"])
def one_post():
    group_name = request.form['group_name']
    print(group_name)

    post = db.post_content.find_one({'group_name': group_name})
    print(post)

    if post is None:
        one_post = None
    elif post is not None:
        one_post = {
            'img': post['img'],
            'group_name': post['group_name'],
            'address': post['address'],
            'content': post['content'],
            'id': post['id'],
        }

        print(one_post)

    return jsonify({'one_post': one_post})


@app.route('/udongdong/write_page', methods=["GET"])
def write_page():
    id = request.args.get('id')
    nickname = request.args.get('nickname')

    return render_template('write_post.html', id=id, nickname=nickname)


@app.route("/udongdong/write", methods=["POST"])
def write_content():
    id = request.form['id']
    nickname = request.form['nickname']
    img = request.form['img']
    group_name = request.form['group_name']
    address = request.form['address']
    content = request.form['content']

    if id == "" or nickname == "" or img == "" or group_name == "" or address == "" or content == "":
        msg = "X"
    else:
        msg = "O"
        content_doc = {
            'img': img,
            'group_name': group_name,
            'address': address,
            'content': content,
            'id': id,
            'nickname': nickname
        }
        db.post_content.insert_one(content_doc)

    return jsonify({'msg': msg})


@app.route("/udongdong/delete")
def delete_content():
    group_name = request.args.get('group_name')
    db.post_content.delete_one({'group_name': group_name})

    return render_template('MainPage.html')


@app.route("/udongdong/view_content", methods=["GET"])
def view_content():
    group_name = request.args.get('group_name')
    address = request.args.get('address')
    content = request.args.get('content')
    img = request.args.get('img')
    id = request.args.get('id')
    nickname = db.user.find_one({'id': id})

    # print(group_name, address, content, img, id, nickname)

    return render_template('open_post.html', group_name=group_name, address=address, content=content, img=img, id=id,
                           nickname=nickname['nick'])


@app.route("/udongdong/test_view_content", methods=["GET"])
def test_view_content():
    group_name = request.args.get('group_name')
    id = request.args.get('id')

    group = db.post_content.find_one({'group_name': group_name})
    user = db.user.find_one({'id': id})

    return render_template('open_post.html', group_name=group['group_name'], address=group['address'],
                           content=group['content'], img=group['img'], id=group['id'],
                           nickname=user['nick'])


@app.route("/udongdong/write_comment", methods=["POST"])
def write_comment():
    user_id = request.form('user_id')
    nickname = request.form('nickname')
    comment = request.form('comment')

    comment_doc = {
        'id': user_id,
        'nick': nickname,
        'comment': comment
    }

    db.comments.insert_one(comment_doc)

    comments_list = list(db.comments.find({}, {'_id': False}))

    return jsonify({'comment_list': comments_list})


# 회원가입 페이지입니다.
@app.route('/register')
def register():
    return render_template('register.html')


# 로그인페이지 입니다.
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/join/save', methods=['POST'])
def join_save():
    userid_receive = request.form['userid_give']
    usernick_receive = request.form['usernick_give']
    userpassword_receive = request.form['userpassword_give']
    password_hash = hashlib.sha256(userpassword_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': userid_receive, 'pw': password_hash, 'nick': usernick_receive})

    return jsonify({'result': 'success'})


@app.route('/join/idcheck', methods=['POST'])
def join_idcheck():
    userid_receive = request.form['userid_give']
    exists = bool(db.user.find_one({"id": userid_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/join/nickcheck', methods=['POST'])
def join_nickcheck():
    usernick_receive = request.form['usernick_give']
    exists = bool(db.user.find_one({"nick": usernick_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# nick_name = db.user.find_one({'id':"wlstp@naver.com"})['nick']
# print(nick_name)

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/udongdong/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
