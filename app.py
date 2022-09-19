from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.wtjymgq.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

# member_doc = {'id':'wlstpgns51@naver.com', 'pwd':'wls124578' }
# db.member.insert_one(member_doc)
# member = list(db.member.find({},{'_id':False}))
# print(member)

# post_doc = {
#     'img':'https://cmsphoto.ww-cdn.com/superstatic/1788037/art/default/31394272-29615629.jpg?v=1551977422',
#     'group_name':'산악사랑',
#     'address':'서울특별시 강서구 마곡동',
#     'content':'산악을 좋아하는 사람들의 모임입니다.',
#     'id':'wlstpgns51@naver.com',
#     'pwd':'wls124578'
# }
# db.post_content.insert_one(post_doc)
# post_content = list(db.post_content.find({},{'_id':False}))
# print(post_content)

@app.route('/')
def home():

   return render_template('MainPage.html')


@app.route('/udongdong/posts', methods=["GET"])
def posts_list():
    posts_list = list(db.post_content.find({}, {'_id': False}))

    return jsonify({'posts_list':posts_list})


@app.route('/udongdong/write_page', methods=["GET"])
def write_page():

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


@app.route("/udongdong/view_content", methods=["GET"])
def view_content():
    group_name = request.args.get('group_name')
    address = request.args.get('address')
    content = request.args.get('content')
    img = request.args.get('img')

    return render_template('open_post.html', group_name=group_name, address=address, content=content, img=img)

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)