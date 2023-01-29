import math

from flask import render_template, request, redirect, url_for, session, jsonify
from app import app, login
import utils
import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from flask_login import login_required #bảo mật đăng nhập
from app.models import UserRole

@app.route("/")
def home(): #index.html

    #Phân theo danh mục trên header
    cate_id = request.args.get('category_id') #category_id trong models
    kw = request.args.get("keyword") #tương tự như trên
    page = request.args.get('page', 1)

    products = utils.load_products(cate_id=cate_id, kw=kw, page=int(page)) #cate_id, kw trong utils
    counter = utils.count_products()

    return render_template('index.html',
                           products=products, #products gọi để xuất trong file html
                           pages=math.ceil(counter/app.config['PAGE_SIZE'])) #math.ceil phương thức làm tròn vd 1.5 => 2, PAGE_SIZE gọi ở _init_.py

@app.route('/register', methods=['get', 'post']) #register.html, methode GET : truy cập vào đây show trang đăng ký, methode POST : bấm ấn đăng ký
def user_register():
    err_msg = "" #nếu đăng kí bị lỗi thì sẽ hiện ra tin nhắn
    if request.method.__eq__('POST'): #eq là dấu bằng
        name = request.form.get('name') #'name' dựa vào trường name trong input
        username = request.form.get('username') #'username' dựa vào trường name trong input
        password = request.form.get('password')
        email = request.form.get('email')
        confirm = request.form.get('confirm')
        avatar_path = None

        try: #trường hợp đăng ký thành công
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar') #'avatar' dựa vào trường name trong input
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(name=name,
                               username=username,
                               password=password,
                               email=email,
                               avatar=avatar_path)
                return redirect(url_for('user_signin')) # sau khi đã đăng ký thành công trả về trực tiếp trang được gán
            else:
                err_msg = 'Le mot de passe ressaisi est incorrect'
        except Exception as ex: #trường hợp đăng ký không thành công
            err_msg = 'Le système a une erreur' + str(ex)

    return render_template('register.html',
                           err_msg=err_msg)

@app.route('/user-login', methods=['get', 'post']) #register.html, methode GET : để view, đăng nhập lúc nào cũng là "POST"
def user_signin():
    err_msg = "" #nếu đăng nhập bị lỗi thì sẽ hiện ra tin nhắn
    if request.method.__eq__('POST'):  # eq là dấu bằng
        username = request.form.get('username')  # 'username' dựa vào trường name trong input
        password = request.form.get('password')

        user = utils.check_login(username=username,
                                 password=password)
        if user: #nếu user khác none
            login_user(user=user) #hàm gọi trên import
            if 'product_id' in request.args:
                return redirect(url_for(request.args.get('next', 'home'), product_id=request.args['product_id']))

            return redirect(url_for(request.args.get('next', 'home')))
                #next = request.args.get('next', 'home') #nếu không có next, thì nó lấy home
                #return redirect(url_for(next))  # sau khi đã đăng nhập thành công trả về trực tiếp trang được gán
        else:
            err_msg = "Identifiant ou mot de passe incorrect!!!"

    return render_template('login.html',
                           err_msg=err_msg)

@app.route('/admin-login', methods=['post']) #đăng nhập của admin, đăng nhập lúc nào cũng là "POST"
def signin_admin():
    err_msg = "" #nếu đăng nhập bị lỗi thì sẽ hiện ra tin nhắn
    username = request.form['username']  # 'username' dựa vào trường name trong input
    password = request.form['password']

    user = utils.check_login(username=username,
                             password=password,
                             role=UserRole.ADMIN)
    if user: #nếu user khác none
        login_user(user=user) #hàm gọi trên import

    return redirect('/admin')

@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

#Thông tin chung cho tất cả các trang
@app.context_processor
def common_response():
    return {
        'categories': utils.load_categories(),
        'cart_stats' : utils.count_cart(session.get('cart'))
    }

@login.user_loader #tự gọi sau khi đăng nhập thành công
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id) #hàm từ bên utils

@app.route("/products") #products.html
def product_list():
    cate_id = request.args.get("category_id") #nếu không có dữ liệu trong category_id thì nó sẽ là none, cate_id là biến đã gọi trong utils.py, category_id là từ sẽ hiện lên trên link
    kw = request.args.get("keyword") #tương tự như trên
    from_price = request.args.get("from_price") #tương tự như trên
    to_price = request.args.get("to_price") #tương tự như trên

    products = utils.load_products(cate_id=cate_id,
                                   kw=kw,
                                   from_price=from_price,
                                   to_price=to_price) #gọi danh sách products


    return render_template('products.html',
                           products=products) #trả danh sách products ra ngoài

@app.route("/products/<int:product_id>") #product_detail.html, int : số nguyên
def product_detail(product_id):
    product = utils.get_product_by_id(product_id)
    comments = utils.get_comments(product_id=product_id,
                                  page=int(request.args.get('page', 1)))

    return render_template('product_detail.html',
                           comments=comments,
                           product=product,
                           pages=math.ceil(utils.count_comment(product_id=product_id)/app.config['COMMENT_SIZE'])) #math.ceil phương thức làm tròn vd 1.5 => 2, COMMENT_SIZE gọi ở _init_.py

#trang giỏ hàng
@app.route('/cart')
def cart():
    return render_template('cart.html',
                           stats=utils.count_cart(session.get('cart')))

#thêm vào giỏ hàng
@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    #lệnh debug
    #import pdb
    #pdb.set_trace()

    cart = session.get('cart') #lấy cái giỏ ra
    if not cart: #nếu chưa có gì trong giỏ
        cart = {}

    if id in cart: #nếu sản phẩm này đã từng bỏ vào giỏ rồi
        cart[id]['quantity'] = cart[id]['quantity'] + 1

    else: #nếu sản phẩm này chưa bỏ vào giỏ
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1 #số lượng sản phẩm
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))

#trả tiền
@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        del session['cart'] #xóa sản phẩm trong giỏ sau khi thanh toán xong
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})

#cập nhật số lượng trong giỏ khi ấn nút thêm
@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    #lệnh debug
    #import pdb
    #pdb.set_trace()

    cart = session.get('cart') # lấy cái giỏ ra
    if cart and id in cart: #kiểm tra giỏ và sản phẩm có trong giỏ cần update
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))

#xóa sản phẩm trong giỏ
@app.route('/api/delete-cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart') # lấy cái giỏ ra
    if cart and product_id in cart: #kiểm tra giỏ và sản phẩm có trong giỏ cần update
        del cart[product_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))

#thêm bình luận
@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    product_id = data.get('product_id')

    try:
        c = utils.add_comment(content=content, product_id=product_id)
    except:
        return {'status': 404, 'err_msg': 'Erreur!!!'}

    return {'status': 201, 'comment': {
        'id': c.id,
        'content': c.content,
        'created_date': c.created_date,
        'user': {
            'username': current_user.username,
            'avatar': current_user.avatar
        }
    }}

if __name__ == '__main__':
    from app.admin import *
    app.run(debug=True)