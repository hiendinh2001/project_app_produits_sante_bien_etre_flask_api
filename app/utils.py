# tập tin chuyên tương tác với dữ liệu

import json, os
from app import app, db
from app.models import Category, Product, User, Receipt, ReceiptDetails, Comment, UserRole
from flask_login import current_user #thanh toán cho user đăng nhập
from sqlalchemy import func #đếm cho thống kê
from sqlalchemy.sql import extract
import hashlib #cho password

def read_json(path): #đọc tập tin json chung
    with open(path, "r") as f:
        return json.load(f)

def load_categories():
    return Category.query.all()
    #return read_json(os.path.join(app.root_path, 'data/categories.json')) #Nối hai cái này thành đường dẫn tuyệt đối, dời "utils.py" đi đâu thì nó vẫn đọc được

def load_products(cate_id=None, kw=None, from_price=None, to_price=None, page=1): #cate_id, kw, from_price, to_price : giá trị mà client truyền vào
    products = Product.query.filter(Product.active.__eq__(True))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if kw:
        products = products.filter(Product.name.contains(kw))

    if from_price:
        products = products.filter(Product.price.__ge__(float(from_price))) #lớn hơn hoặc bằng

    if to_price:
        products = products.filter(Product.price.__le__(float(to_price))) #nhỏ hơn hoặc bằng

    page_size = app.config['PAGE_SIZE'] #số sản phẩm mỗi trang, lấy PAGE_SIZE từ _init_.py
    start = (page - 1) * page_size #page là page hiện tại
    end = start + page_size

    return products.slice(start, end).all() #slice: cắt trang từ start đến end

def count_products(): #đếm số lượng sản phẩm có trang Database
    return Product.query.filter(Product.active.__eq__(True)).count()

    # products = read_json(os.path.join(app.root_path, 'data/products.json')) #Nối hai cái này thành đường dẫn tuyệt đối, dời "utils.py" đi đâu thì nó vẫn đọc được

    # if cate_id: #Lọc theo danh mục : Moblie, Tablet
    #     products = [p for p in products if p['category_id'] == int(cate_id)] #category_id của products.json tương ứng với id của categories.json

    # if kw: #Tìm kiếm sản phẩm từ khóa
    #     products = [p for p in products if p['name'].lower().find(kw.lower()) >= 0] #lower:sau khi ng dùng ấn tìm kiếm thì chuyển thành chữ thường hết

    # if from_price: #Tìm kiếm sản phẩm từ giá này
    #     products = [p for p in products if p['price'] >= float(from_price)]

    # if to_price: #Tìm kiếm sản phẩm đến giá này
    #     products = [p for p in products if p['price'] <= float(to_price)]

    # return products

def get_product_by_id(product_id): #product_id : cái client nhập vào
    return Product.query.get(product_id)

    # products = read_json(os.path.join(app.root_path, 'data/products.json')) #Nối hai cái này thành đường dẫn tuyệt đối, dời "utils.py" đi đâu thì nó vẫn đọc được

    # for p in products:
    #     if p['id'] == product_id:
    #         return p

def add_user(name, username, password, **kwargs): #function để đăng ký người dùng, đây là những tham số bắt buộc để đăng ký, **kwargs : dạng từ điển vd như email, avatar không bắt buộc
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar')) #tên bảng trong CSDL là User, strip() để cắt khoảng trắng hai đầu
    db.session.add(user)
    db.session.commit()

def check_login(username, password, role=UserRole.USER): #function để đăng nhập người dùng, đây là những tham số bắt buộc để đăng nhập
    if username and password: #nếu không có thì tự động return none
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                                User.user_role.__eq__(role)).first() #filter : lọc dữ liệu trong truy vấn

def get_user_by_id(user_id):
    return User.query.get(user_id) #với id lúc nào cũng dùng get

#bỏ giỏ từ session vào
def add_receipt(cart):
    if cart:
        receipt = Receipt(user=current_user)#tạo hóa đơn,user ở đây là từ backref của models bảng
        db.session.add(receipt)

        for c in cart.values():
            d = ReceiptDetails(receipt=receipt,
                               product_id=c['id'],
                               quantity=c['quantity'],
                               unit_price=c['price']) #receipt đầu tiên là từ backref của models bảng
            db.session.add(d)

        db.session.commit()

def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }

#Thêm bình luận
def add_comment(content, product_id):
    c = Comment(content=content, product_id=product_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c

#lấy bình luận gần nhất
def get_comments(product_id, page=1):
    page_size = app.config['COMMENT_SIZE']  # số bình luận mỗi trang, lấy COMMENT_SIZE từ _init_.py
    start = (page - 1) * page_size  # page là page hiện tại

    return Comment.query.filter(Comment.product_id.__eq__(product_id))\
                    .order_by(-Comment.id).slice(start, start + page_size).all()

#Phân trang của bình luận, số lượng comment của sản phẩm này
def count_comment(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()

#Thống kê danh mục
def category_stats():
    #return Category.query.join(Product, Product.category_id.__eq__(Category.id), isouter=True)\
                         #.add_columns(func.count(Product.id))\
                         #.group_by(Category.id, Category.name).all()

    return db.session.query(Category.id, Category.name, func.count(Product.id))\
                     .join(Product, Category.id.__eq__(Product.category_id), isouter=True)\
                     .group_by(Category.id, Category.name).all()

#Thông kê doanh số bán hàng
def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Product.id, Product.name,
                         func.sum(ReceiptDetails.quantity * ReceiptDetails.unit_price))\
                  .join(ReceiptDetails, ReceiptDetails.product_id.__eq__(Product.id), isouter=True)\
                  .join(Receipt, Receipt.id.__eq__(ReceiptDetails.receipt_id))\
                  .group_by(Product.id, Product.name)
    if kw:
        p = p.filter(Product.name.contains(kw))

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date)) #ge là lớn hơn hoặc bằng

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date)) #le là nhỏ hơn hoặc bằng

    return p.all()

#Thống kê theo tháng, năm
def product_month_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetails.quantity*ReceiptDetails.unit_price))\
                     .join(ReceiptDetails, ReceiptDetails.receipt_id.__eq__(Receipt.id))\
                     .filter(extract('year', Receipt.created_date) == year)\
                     .group_by(extract('month', Receipt.created_date))\
                     .order_by(extract('month', Receipt.created_date)).all() #order_by : sắp xếp theo tháng

