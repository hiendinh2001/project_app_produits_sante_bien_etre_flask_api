from app import app, db
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from app.models import Category, Product, UserRole
from flask_login import current_user, logout_user
from flask import redirect, request
import utils
from datetime import datetime

class AuthenticatedModelView(ModelView): #kế thừa ModalView đã import ở trên
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

class ProductView(AuthenticatedModelView):
    column_display_pk = True #hiện khóa sản phẩm
    can_view_details = True #xuất hiện thêm biểu tượng mắt
    can_export = True #Nút tải về danh sách về file csv
    column_searchable_list = ['name', 'description'] #thanh tìm kiếm
    column_filters = ['name', 'price'] #tìm kiếm riêng bằng filter
    column_exclude_list = ['image', 'active', 'created_date'] #không muốn hiển thị cột "image", "active", "created_date"
    column_labels = { #đặt tên tiêu đề của bảng
        'name': 'Nom du produit',
        'description': 'Description',
        'price': 'Prix',
        'image': 'Photo du produit',
        'category': 'Catégorie'
    }
    column_sortable_list = ['id', 'name', 'price']#sắp xếp là mặc định cho tất cả các cột nhưng chức năng này dùng để chỉ định cột muốn sắp xếp

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated

class StatsView(BaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year', datetime.now().year)

        return self.render('admin/stats.html',
                           month_stats=utils.product_month_stats(year=year),
                           stats=utils.product_stats(kw=kw,
                                                     from_date=from_date,
                                                     to_date=to_date))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html',
                           stats=utils.category_stats())

admin = Admin(app=app,
              name='Bien-être & Santé website',
              template_mode='bootstrap4',
              index_view=MyAdminIndex())
admin.add_view(AuthenticatedModelView(Category, db.session, name='Category'))
admin.add_view(ProductView(Product, db.session, name='Product'))
admin.add_view(StatsView(name='Stats'))
admin.add_view(LogoutView(name='Logout'))




