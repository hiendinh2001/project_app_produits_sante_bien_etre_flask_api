from sqlalchemy import Column, Integer, Boolean, Float, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from app import db, app
from datetime import datetime
from flask_login import UserMixin
from enum import Enum as UserEnum

class BaseModel(db.Model): #lớp chung, kế thừa (db.Model)
    __abstract__ = True #bảng này chỉ để lấy cái chung, chứ không tạo bảng

    id = Column(Integer, primary_key=True, autoincrement=True) #Khóa chính cho các bảng kế thừa

class UserRole(UserEnum):
    ADMIN = 1
    USER = 2

class User(BaseModel, UserMixin): #Bảng user, kế thừa BaseModel
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))
    active = Column(Boolean, default=True) #xem người dùng này còn hoạt động, còn trong hệ thống hay không
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER) #xem người dùng là USER hay ADMIN
    receipts = relationship('Receipt', backref='user', lazy=True) #nối với bảng Receipt
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name

class Category(BaseModel): #Lớp đại diện cho một bảng ở CSDL, bảng Category, kế thừa BaseModel
    __tablename__ = 'category'

    name = Column(String(50), nullable=False)
    products = relationship('Product', backref='category', lazy=False) #1 cái category có nhiều sản phẩm

    def __str__(self):
        return self.name

class Product(BaseModel): #Bảng product, kế thừa BaseModel
    __tablename__ = 'product'

    name = Column(String(10000), nullable=False)
    description = Column(Text)
    price = Column(Float, default=0)
    image = Column(String(500))
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False) #Khóa ngoài, Category (tên bảng tham chiếu)
    receipt_details = relationship('ReceiptDetails', backref='product', lazy=True) #quản hệ với bảng ReceiptDetails
    comments = relationship('Comment', backref='product', lazy=True)

    def __str__(self):
        return self.name

#Thanh toán đơn hàng
class Receipt(BaseModel):
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False) #Biết được hóa đơn này của khách hàng nào
    details = relationship('ReceiptDetails', backref='receipt', lazy=True) #ReceiptDetails là bảng chi tiết sản phẩm

#Lưu chi tiết sản phẩm của đơn hàng, mối quan hệ chung gian giữa bảng Receipt và bảng product do đó có hai khóa ngoại, hai khóa ngoại hợp lại thành khóa chính
class ReceiptDetails(db.Model):
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0) #số lượng sản phẩm trong hóa đơn
    unit_price = Column(Float, default=0)

#Lưu bình luận
class Comment(BaseModel):
    content = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        c1 = Category(name='Cosmétiques et Beauté')
        c2 = Category(name='Vitalité et Immunité')
        c3 = Category(name='Stress et Sommeil')

        db.session.add(c1)
        db.session.add(c2)
        db.session.add(c3)

        db.session.commit()

        p1 = Product(name='Age intense',
                     description="Soin coup d'éclat à l'acide hyaluronique.",
                     price=27.5,
                     image='images/image1.jpg',
                     category_id=1)
        p2 = Product(name='Infusion Divine',
                     description='Un trio de soins complet, nourrissant et agréablement parfumé.',
                     price=24.8,
                     image='images/image2.jpg',
                     category_id=1)
        p3 = Product(name='Rose musquée BIO',
                     description='Produit anti-âge, anti-oxydante, assouplissante et régénérante.',
                     price=14.5,
                     image='images/image3.jpg',
                     category_id=1)
        p4 = Product(name='Vitamine C 1000',
                     description='Complément alimentaire à base de vitamine C',
                     price=18.3,
                     image='images/image4.jpg',
                     category_id=2)
        p5 = Product(name='Oméga 3 2400-TG',
                     description='Complément alimentaire concentré en Acides Gras Oméga 3 (EPA et DHA) sous forme de triglycérides provenant d’huile de poisson.',
                     price=20.5,
                     image='images/image5.jpg',
                     category_id=2)
        p6 = Product(name='Safran 2% safranal',
                     description='Complément alimentaire à base d’extrait sec concentré de stigmates purs de Safran et vitamine B6.',
                     price=12.5,
                     image='images/image6.jpg',
                     category_id=2)
        p7 = Product(name='Ashwagandha BIO',
                     description="Stimule l'énergie physique et mentale.",
                     price=13.9,
                     image='images/image7.jpg',
                     category_id=3)
        p8 = Product(name='Astaxanthine',
                     description="Puissant antioxydant extrait d'algue!",
                     price=25,
                     image='images/image8.jpg',
                     category_id=3)
        p9 = Product(name='Maca force 3 BIO',
                     description="Produit exceptionnel pour renforcer votre tonus (fatigue)!",
                     price=15.2,
                     image='images/image9.jpg',
                     category_id=3)

        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.add(p5)
        db.session.add(p6)
        db.session.add(p7)
        db.session.add(p8)
        db.session.add(p9)

        db.session.commit()