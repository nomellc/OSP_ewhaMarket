from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
from datetime import datetime, timedelta
import hashlib
import sys

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

@application.route("/")
def hello():
    return redirect(url_for('view_list'))

@application.route("/login")
def login():
    return render_template("login.html")

@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('view_list'))

@application.route("/signup")
def view_signup():
    return render_template("signup.html")

@application.route('/check_id', methods=['POST'])
def check_id():
    data = request.json
    user_id = data['id']
    if DB.user_duplicate_check(user_id):
        return "사용 가능한 ID입니다."
    else:
        return "이미 존재하는 ID입니다."

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    
    if DB.find_user(id_, pw_hash):
        session['id'] = id_
        return redirect(url_for('view_list'))
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", "all")
    sort = request.args.get("sort", "name")
    per_page = 6
    per_row = 3
    row_count = int(per_page / per_row)
    start_idx = per_page * page
    end_idx = per_page * (page + 1)
    
    if category == "all":
        data = DB.get_items(sort=sort)
    else:
        data = DB.get_items_bycategory(category, sort=sort)

    if sort == '최신순':
        sort = 'newest'
    elif sort == '오래된순':
        sort = 'oldest'
    elif sort == '낮은 가격순':
        sort = 'price_asc'
    elif sort == '높은 가격순':
        sort = 'price_desc'

    item_counts = len(data)
    page_count = int((item_counts / per_page) + 1)

    # 데이터 슬라이싱
    sliced_data = dict(list(data.items())[start_idx:end_idx])

    # 데이터를 행별로 분리
    rows_data = [dict(list(sliced_data.items())[i*per_row:(i+1)*per_row]) for i in range(row_count)]

    # 전달할 데이터 준비
    render_data = {
        'row_data': rows_data,
        'limit': per_page,
        'page': page,
        'page_count': page_count,
        'total': item_counts,
        'category': category,
        'sort': sort
    }

    return render_template("index.html", **render_data)

@application.route("/view_detail/<name>/", endpoint='view_detail_by_name')
def view_item_detail(name):
    data = DB.get_item_byname(str(name))
    is_logged_in = 'id' in session  # 로그인 상태인지 확인
    return render_template("detail.html", name=name, data=data, is_logged_in=is_logged_in)

@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    data = DB.get_review_byname(name)
    return render_template("review_detail.html", name=name, data=data)

@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page=6 # item count to display per page
    per_row=1# item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_reviews() #read the table
    sorted_reviews = sorted(data.items(), key=lambda x: x[1].get('thumb_count', 0), reverse=True)
    item_counts = len(data)
    data = sorted(data.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
    data = dict(data[start_idx:end_idx])
    tot_count = len(data)
    top_images = list(sorted_reviews)[:5]
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    
    return render_template(
     "review.html",
     datas=data.items(),
     top_images=top_images,
     row1=locals()['data_0'].items(),
     row2=locals()['data_1'].items(),
     row3=locals()['data_2'].items(),
     row4=locals()['data_3'].items(),
     row5=locals()['data_4'].items(),
     row6=locals()['data_5'].items(),
     limit=per_page,
     page=page,
     page_count=int((item_counts/per_page)+1),
     total=item_counts)

@application.route("/reg_items")
def reg_item():
    if 'id' not in session:
        flash("로그인이 필요한 페이지입니다.")
        return redirect(url_for('login'))
    return render_template("reg_items.html")

@application.route("/contact")
def view_contact():
    return render_template("contact.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file = request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data = request.form
    item_name = data['item_title'] 
    DB.insert_item(item_name, data, image_file.filename)

    item_data = DB.get_item_byname(item_name) 

    return render_template("detail.html", name=item_name, data=item_data)


@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    is_id_checked = request.form.get('isIdChecked') == 'true'
    is_password_checked = request.form.get('isPasswordChecked') == 'true'

    if is_id_checked and is_password_checked:
        if DB.insert_user({'id': data['id'], 'pw': pw_hash, 'nickname': data['nickname'], 'email': data['email'], 'phonenum': data.get('phonenum', '')}):
            flash("회원가입이 완료되었습니다. 환영합니다.")
            return render_template("login.html")
        else:
            flash("이미 존재하는 ID입니다.")
            return render_template("signup.html")
    else:
        flash("아이디/비밀번호 체크를 해주세요.")
        return render_template("signup.html")

@application.route("/reg_review_init/<name>/<item_title>")
def reg_review_init(name, item_title):
    return render_template("reg_reviews.html", name=name, item_title=item_title)

@application.route("/reg_review", methods=['POST'])
def reg_review():
    # 현재 UTC 시간을 가져옴
    current_time_utc = datetime.utcnow()
    # 한국 시간대로 변환
    current_time_korea = current_time_utc + timedelta(hours=9)
    # ISO 형식의 문자열로 변환
    current_time_date_only = current_time_korea.strftime("%Y-%m-%d")
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.reg_review(data, image_file.filename, current_time_date_only)
    return redirect(url_for('view_review'))

@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'],name)
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['id'],'Y',name)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['id'],'N',name)
    return jsonify({'msg': '안좋아요 완료!'})

@application.route('/show_thumb/<name>/', methods=['GET'])
def show_thumb(name):
    item_thumb = DB.get_thumb_byname(name, session['id'])
    return jsonify({'item_thumb': item_thumb})

@application.route('/thumb/<name>/', methods=['POST'])
def thumb(name):
    item_thumb = DB.update_thumb(name, 'Y', session['id'])
    return jsonify({'msg': '도움이 됐어요!'})

@application.route('/unthumb/<name>/', methods=['POST'])
def unthumb(name):
    item_thumb = DB.update_thumb(name,'N', session['id'])
    return jsonify({'msg': '도움이 됐어요 취소!'})

@application.route('/show_follow/<name>/', methods=['GET'])
def show_follow(name):
    user_follow = DB.get_follow_byname(session['id'], name)
    return jsonify({'user_follow': user_follow})

@application.route('/follow/<name>/', methods=['POST'])
def follow(name):
    user_follow = DB.update_follow(session['id'], 'Y', name)
    return jsonify({'msg': '팔로우 완료!'})

@application.route('/unfollow/<name>/', methods=['POST'])
def unfollow(name):
    user_follow = DB.update_follow(session['id'],'N', name)
    return jsonify({'msg': '팔로잉 취소!'})

@application.route("/view_following/<name>/")
def view_following(name):
    data = DB.get_follow(name)
    follower = DB.get_followercount_byname("")
    return render_template("nine_following.html", data=data, follower=follower)

@application.route("/yourpage/<name>/")
def view_yourpage(name):
    data = DB.get_followercount_byname(name)
    following = DB.get_followingcount_byname(name)
    popular, match=DB.get_sellitems_by_id(str(name), True) #read the table
    tot_count1=len(popular)
    tot_count2=len(match)
    print("이건 popular", popular)
    print("이건 match", match)
    
    return render_template("yourpage.html", name=name, data=data, following=following, 
                           populars=popular, total1=tot_count1,
                           matches=match, total2=tot_count2)

@application.route("/mypage/<id>/")
def my_page(id):
    data = DB.get_followingcount_byname(str(id))
    follower = DB.get_followercount_byname(str(id))
    data1=DB.get_sellitems_by_id(str(id), False) #read the table
    tot_count1=len(data1)
    data2=DB.get_likeitems_by_id(str(id))
    tot_count2=len(data2)
    data3=DB.get_buyitems_by_id(str(id)) #read the table
    tot_count3=len(data3)
    return render_template("nine_mypage.html", data=data, follower=follower, 
                           datas1=data1, total1=tot_count1,
                           datas2=data2, total2=tot_count2,
                           datas3=data3, total3=tot_count3)

@application.route("/mysell/<id>/")
def my_sell(id):
    data=DB.get_sellitems_by_id(str(id), False) #read the table
    tot_count1=len(data)
    sold=DB.get_solditems_by_id(str(id)) #read the table
    tot_count2=len(sold)
    return render_template("nine_sell.html", datas=data, total1=tot_count1, solds=sold, total2=tot_count2)


    """_summary_
    판매중 버튼 클릭 -> 
    데이터베이스 item의 해당 id의 아이템 sold seller에 저장 -> 
    데이터베이스 item의 해당 id의 아이템 삭제 -> 
    html에 sold seller에 해당하는 부분을 출력
    """
@application.route("/sellsold/<id>/<item_title>/")
def sell_sold(id, item_title):
    success=DB.move_sell_item_to_sold(id, item_title)
    if success:
        flash("해당 상품이 판매완료 되었습니다.")
        return redirect(url_for('my_sell', id=id))
    else:
        flash("해당 상품이 없습니다.")
        return redirect(url_for('my_sell', id=id))

@application.route("/mylike/<id>/")
def my_like(id):
    data=DB.get_likeitems_by_id(str(id))
    tot_count=len(data)
    return render_template("nine_like.html", datas=data, total=tot_count)

@application.route("/mybuy/<id>/")
def my_buy(id):
    data=DB.get_buyitems_by_id(str(id)) #read the table
    tot_count=len(data)
    return render_template("nine_buy.html", datas=data, total=tot_count)

@application.route("/buybutton/<name>/")
def buy_button(name):
    timestamp = int(datetime.timestamp(datetime.now()))
    item_name = request.args.get('item_name')  # URL 쿼리 매개변수에서 item_name 가져오기
    data = {
    'id': name,
    'item_name': item_name,
    'timestamp': timestamp}
    # DB.insert_buy_item 함수 호출 시 item_name도 함께 전달
    DB.insert_buy_item(data)
    DB.update_sell_count(item_name)
    flash("상품이 구매되었습니다.")
    #return render_template("detail.html", data=data)
    return redirect(url_for('view_detail_by_name', name=item_name))

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
