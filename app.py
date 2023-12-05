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
    return render_template("seven_login.html")

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
        return render_template("seven_login.html")

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
        data = DB.get_items(sort=sort) # 정렬 파라미터를 get_items에 전달
    else:
        data = DB.get_items_bycategory(category, sort=sort)
    data = dict(sorted(data.items(), key=lambda x: x[0], reverse=False))
    item_counts = len(data)
    if item_counts <= per_page:
        data = dict(list(data.items())[:item_counts])
    else:
        data = dict(list(data.items())[start_idx:end_idx])

    tot_count = len(data)

    for i in range(row_count):
        start = i * per_row
        end = start + per_row
        data_key = 'data_{}'.format(i)
        if start < tot_count:
            if end > tot_count:  # 마지막 페이지의 마지막 행 처리
                locals()[data_key] = dict(list(data.items())[start:])
            else:
                locals()[data_key] = dict(list(data.items())[start:end])

    # 여기서 locals()['data_0'] 또는 locals()['data_1']이 존재하지 않을 수 있으므로, 이를 고려하여 템플릿에 데이터 전달
    return render_template("list.html", 
                           row1=locals().get('data_0', {}).items(), 
                           row2=locals().get('data_1', {}).items(), 
                           limit=per_page, 
                           page=page, 
                           page_count=int((item_counts / per_page) + 1), 
                           total=item_counts,
                           category=category)

@application.route("/view_detail/<name>/", endpoint='view_detail_by_name')
def view_item_detail(name):
    data = DB.get_item_byname(str(name))
    is_logged_in = 'id' in session  # 로그인 상태인지 확인
    print("웹사이트에 들어갑니다", name)
    return render_template("detail.html", name=name, data=data, is_logged_in=is_logged_in)

@application.route("/view_review_detail/<name>/")
def view_review_detail(name):
    data = DB.get_review_byname(name)
    return render_template("six_review_detail.html", name=name, data=data)

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
     "five_review_1109.html",
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
    return render_template("one_item_regi.html")

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
            return render_template("seven_login.html")
        else:
            flash("user id already exist!")
            return render_template("eight_register.html")
    else:
        flash("아이디/비밀번호 체크를 해주세요.")
        return render_template("eight_register.html")
    
#@application.route('dynamicurl/<varible_name>/')
#def DynamicUrl(varible_name):
#    return str(varible_name)

@application.route("/reg_review_init/<name>/<item_title>")
def reg_review_init(name, item_title):
    print("제목: ", item_title)
    return render_template("four_review.html", name=name, item_title=item_title)

@application.route("/reg_review", methods=['POST'])
def reg_review():
    # 현재 UTC 시간을 가져옴
    current_time_utc = datetime.utcnow()
    # 한국 시간대로 변환
    current_time_korea = current_time_utc + timedelta(hours=9)
    #print(current_time_korea)
    #current_time=datetime.utcnow().isoformat()
    #current_time_date_only = datetime.fromisoformat(current_time).strftime("%Y-%m-%d")
    # ISO 형식의 문자열로 변환
    current_time_date_only = current_time_korea.strftime("%Y-%m-%d")
    #print(current_time_date_only)
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.reg_review(data, image_file.filename, current_time_date_only)
    return redirect(url_for('view_review'))

@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    print("왜 나에게 이런 일이?1", name)
    my_heart = DB.get_heart_byname(session['id'],name)
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    print("왜 나에게 이런 일이?2", name)
    my_heart = DB.update_heart(session['id'],'Y',name)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    print("왜 나에게 이런 일이?3", name)
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
    print(data)
    print(follower)
    return render_template("nine_following.html", data=data, follower=follower)

@application.route("/yourpage/<name>/")
def view_yourpage(name):
    data = DB.get_followercount_byname(name)
    following = DB.get_followingcount_byname(name)
    print(data)
    return render_template("yourpage.html", name=name, data=data, following=following)

@application.route("/mypage/<id>/")
def my_page(id):
    data = DB.get_followingcount_byname(str(id))
    follower = DB.get_followercount_byname(str(id))
    return render_template("nine_mypage.html", data=data, follower=follower)

@application.route("/mysell/<id>/")
def my_sell(id):
    data=DB.get_sellitems_by_id(str(id)) #read the table
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
    flash("상품이 구매되었습니다.")
    #return render_template("detail.html", data=data)
    return redirect(url_for('view_detail_by_name', name=item_name))

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
