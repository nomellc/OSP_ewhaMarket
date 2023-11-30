import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
    
    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data['id_i'],  # ID를 'seller'로 변경
            "item_title": data['item_title'],
            "price": data['price'],
            "category": data['category'],
            "option_dsc": data['option_dsc'],  # 'option_dsc'로 변경
            "event_check": data['event_check'],
            "item_explain": data['explain'],
            "img_path":img_path
        }
        self.db.child("item").child(name).set(item_info)
        return True
    
    def get_items(self):
        items = self.db.child("item").get().val()
        return items
    
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value=""
        print("###########", name)
        for res in items.each():
            key_value = res.key()
            
            if key_value == name:
                target_value = res.val()
        return target_value
    
    def insert_user(self, data):
        user_info ={
            "id":data['id'],
            "pw":data['pw'],
            "nickname":data['nickname'],
            "phonenum":data['phonenum']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print(data)
            return True
        else:
            return False
    
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()

        print("users###", users.val())
        if str(users.val()) == "None": # first registration
            return True
        else:
            for res in users.each():
                value = res.val()

                if value['id'] == id_string:
                    return False
            return True
        
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value = res.val()
            
            if value['id'] == id_ and value['pw'] == pw_:
                return True

        return False
    

    def reg_review(self, data, img_path, current_time):
        review_info ={
        "ID":data['id'],
        "title":data['review'],
        "rate": data['reviewStar'],
        "option": data['option'],
        "review": data['review-content'],
        "img_path":img_path,
        "timestamp":current_time
        }
        self.db.child("review").child(data['name']).set(review_info)
        
        return True

    def get_mypage(self):
        mypage_info = self.db.child("mypage").get().val()

    def get_reviews(self):
        reviews = self.db.child("review").get().val()
        return reviews
    
    def get_review_byname(self, name):
        reviews = self.db.child("review").get()
        target_value=""
        print("###########", name)
        for res in reviews.each():
            key_value = res.key()
            
            if key_value == name:
                target_value = res.val()
        return target_value
    
    def get_thumbs(self):
        thumbs = self.db.child("thumb").get().val()
    
    def get_thumb_byname(self, item, name):
        thumbs = self.db.child("thumb").child(item).get()
        target_value=""
        if thumbs.val() == None:
            return target_value

        for res in thumbs.each():
            key_value = res.key()

            if key_value == name:
                target_value=res.val()
        return target_value
    
    def update_thumb(self, item_, isThumb, user_id):
        thumb_info = {"thumbed": isThumb}
        self.db.child("thumb").child(item_).child(user_id).set(thumb_info)
        thumbs = self.db.child("thumb").child(item_).get().val()
        if thumbs is None:
            return 0
        count = 0
        for thumb_status in thumbs.values():
            if thumb_status and thumb_status.get("thumbed", "") == 'Y':
                count += 1
        print("Current count:", count)
        current_review_data = self.db.child("review").child(item_).get().val()
        if current_review_data is not None:
            current_review_data["thumb_count"] = count
            self.db.child("review").child(item_).update(current_review_data)
    
        return True
    
    def get_follow_byname(self, uid, name):
        follow = self.db.child("follow").child(uid).get()
        target_value=""
        if follow.val() == None:
            return target_value

        for res in follow.each():
            key_value = res.key()

            if key_value == name:
                target_value=res.val()
        return target_value
    
    def update_follow(self, user_id, isFollow, name):
        follow_info = {"following": isFollow}
        self.db.child("follow").child(user_id).child(name).set(follow_info)
        follow = self.db.child("follow").child(user_id).get().val()
        if follow is None:
            return 0
        count = 0
        for follow_status in follow.values():
            if isinstance(follow_status, dict) and follow_status.get("following", "") == 'Y':
                count += 1
        print("Current count:", count)
        current_follow_data = self.db.child("follow").child(user_id).get().val()
        if current_follow_data is not None:
            current_follow_data["following_count"] = count
            self.db.child("follow").child(user_id).update(current_follow_data)
            self.db.child("mypage").child(user_id).set(current_follow_data)
    
        return True


