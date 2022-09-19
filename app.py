from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.wtjymgq.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


@app.route('/')
def home():
    # 취합 후 루트 html 주소 변경
   return render_template('write_post.html')

@app.route("/udongdong/write", methods=["POST"])
def write_content():
    id = request.form['id']
    pwd = request.form['pwd']
    img = request.form['img']
    group_name = request.form['group_name']
    address = request.form['address']
    content = request.form['content']

    content_doc = {
        'id': id,
        'pwd': pwd,
        'img': img,
        'group_name': group_name,
        'address': address,
        'content': content
    }

    print(content_doc)
    # db.post_content.insert_one(content_doc)

    # 취합 후 메인 페이지로 이동될 수 있게 변경할 것
    return jsonify({'msg':"작성 완료"})

@app.route('/udongdong/view_content', methods=["GET"])
def view_content():
    # 취합 후 루트 html 주소 변경
   return render_template('open_post.html')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)