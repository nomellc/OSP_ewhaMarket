from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import hashlib
import sys

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

@application.route("/")
def hello():
    return render_template("index.html")
    #return redirect(url_for("view_list"))

@application.route("/login")
def login():
    return render_template("login.html")

@application.route("/logout")
def logout_user():
    session.clear()
    return render_template("index.html")

@application.route("/mypage")
def view_mypage():
    return render_template("mypage.html")

@application.route("/signup")
def view_signup():
    return render_template("signup.html")

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    per_page = 6
    per_row = 3
    row_count = int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_items()
    item_counts = len(data)
    data = dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):
        if(i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])
    return render_template("list.html", datas=data.items(), row1=locals()['data_0'].items(), row2=locals()['data_1'].items(), limit=per_page, page=page, page_count=int((item_counts/per_page)+1), total=item_counts)

@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)
    return render_template("detail.html", name=name, data=data)

@application.route("/review_detail")
def view_review_detail():
    return render_template("six_review_detail.html")

@application.route("/review")
def view_review():
    return render_template("four_review.html")

@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")

@application.route("/contact")
def view_contact():
    return render_template("contact.html")

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_, pw_hash):
        session['id']=id_
        return render_template("index.html")
    else:
        flash("Wrong ID or PW!")
        return render_template("login.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file=request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.insert_item(data['name'], data, image_file.filename)
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))

@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    data_with_more_info = {
        'id' : data['id'],
        'pw' : pw_hash,
        'nickname' : data['nickname'],
        'email' : data['email'],
        'phonenum' : data.get('phonenum', '')
    }
    if DB.insert_user(data_with_more_info):
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)