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
    
    def get_items(self, sort='name'):
        items = self.db.child("item").get().val()
        if not items:
            return {}
    
        items_list = list(items.items()) 
        
        if sort == 'price_asc':
            items_list.sort(key=lambda x: int(x[1].get('price', 0)))
        elif sort == 'price_desc':
            items_list.sort(key=lambda x: int(x[1].get('price', 0)), reverse=True)
        elif sort == 'name':
        # Check if 'item_title' key exists, use an empty string as default
            items_list.sort(key=lambda x: x[1].get('item_title', '').lower())

        return dict(items_list)
    
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value=""
        for res in items.each():
            key_value = res.key()
            
            if key_value == name:
                target_value = res.val()
        return target_value
    
    def get_items_bycategory(self, cate, sort='name'):
        items = self.db.child("item").get().val()
        if not items:
            return {}
        
        filtered_items = {k: v for k, v in items.items() if v['category'] == cate}

        if sort == 'price_asc':
            filtered_items = sorted(filtered_items.items(), key=lambda x: int(x[1]['price']))
        elif sort == 'price_desc':
            filtered_items = sorted(filtered_items.items(), key=lambda x: int(x[1]['price']), reverse=True)
        elif sort == 'name':
            filtered_items = sorted(filtered_items.items(), key=lambda x: x[1]['item_title'])

        return dict(filtered_items)
    
    def insert_user(self, data):
        user_info ={
            "id":data['id'],
            "pw":data['pw'],
            "nickname":data['nickname'],
            "email":data['email'],
            "phonenum":data['phonenum']
        }
        if self.user_duplicate_check(data['id']):
            self.db.child("user").push(user_info)
            print(data)
            return True
        else:
            return False
    
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()

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

    def get_follow(self, name):
        following = self.db.child("follow").child(name).get().val()

        return following
    
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
        self.db.child("follower").child(name).child(user_id).set(follow_info)
        follow = self.db.child("follow").child(user_id).get().val()
        follower = self.db.child("follower").child(name).get().val()
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
            self.db.child("following_count").child(user_id).set(count)
        
        if follower is None:
            return 0
        follower_count = 0
        for follower_status in follower.values():
            if isinstance(follower_status, dict) and follower_status.get("following", "") == 'Y':
                follower_count += 1
        print("follower Current count:", follower_count)
        current_follower_data = self.db.child("follower").child(name).get().val()
        if current_follower_data is not None:
            current_follower_data["follower_count"] = follower_count
            self.db.child("follower_count").child(name).set(follower_count)
        return True

    def get_followingcount_byname(self, id):
        data = self.db.child("following_count").child(id).get().val()
        return data
    
    def get_followercount_byname(self, name):
        data = self.db.child("follower_count").child(name).get().val()
        return data
    
    def get_sellitems_by_id(self, id):
        items = self.db.child("item").get()
        matching_items = []
        if items.val() is not None:
            for res in items.each():
                # 각 물건(케이크, 쿠키, 마들렌 등)의 데이터에 접근
                item_data = res.val()

                # 만약 해당 물건에 id 키가 있다면
                if "seller" in item_data and item_data["seller"] == id:
                    matching_items.append(item_data)
        return matching_items
    
    def get_solditems_by_id(self, id):
        items = self.db.child("sold").child(id).get()
        matching_items = []
        if items.val() is not None:
            for res in items.each():
                # 각 물건(케이크, 쿠키, 마들렌 등)의 데이터에 접근
                item_data = res.val()
                matching_items.append(item_data)
        return matching_items
        
    def move_sell_item_to_sold(self, id, item_title):
        sell_items = self.db.child("item").child(item_title).get().val()
        if sell_items is not None:
            # 판매자 확인
            if "seller" in sell_items and sell_items["seller"] == id:
                # 판매된 아이템을 'sold' 노드로 이동
                self.db.child("sold").child(id).push(sell_items)
                
                # 판매 아이템 삭제 (참고: 실제로 데이터베이스에서 삭제하려면 remove() 사용)
                self.db.child("item").child(item_title).remove()
                return True
        return False

    def insert_buy_item(self, data):
        id=data['id']
        buy_info={
            "item_name" : data['item_name'],
            "timestamp" : data['timestamp']
        }
        self.db.child("buy").child(data['id']).push(buy_info)
        return True
    
    def get_buyitems_by_id(self, id):
        matching_items = []
        buy_items_ref = self.db.child("buy").child(id).get()

        if buy_items_ref.val() is not None:
            for res in buy_items_ref.each():
                value = res.val()
                item_ref = self.db.child("item").child(value['item_name']).get()

                if item_ref.val() is not None:
                    item_data = item_ref.val()
                    matching_items.append({
                        "item_title": item_data.get("item_title"),
                        "img_path": item_data.get("img_path"),
                        "price": item_data.get("price")
                    })

        return matching_items


    
    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).child(name).get().val()
        #hearts = self.db.child("heart").child(uid).get()
        target_value=""
        if hearts == None:
            return target_value
        else:
            target_value=hearts['isHeart']
            print("새로고침 후 상태", target_value)
        return target_value

    def update_heart(self, user_id, isHeart, item):
        if self.db.child("heart").child(user_id).child(item).get().val()==None :
            sell_items=self.db.child("item").child(item).get().val()
            like_info={
                "item_title":sell_items['item_title'],
                "price":sell_items['price'],
                "img_path": sell_items['img_path'],
                "isHeart": isHeart
            }
            if sell_items is not None:
                self.db.child("heart").child(user_id).child(item).set(like_info)
                print("새 거고,", isHeart)
        else :
            self.db.child("heart").child(user_id).child(item).update({"isHeart": isHeart})
            print("헌 거고,", isHeart)
        return True