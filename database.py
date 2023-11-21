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