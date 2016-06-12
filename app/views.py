from flask import render_template, request, flash, redirect, session, url_for, g
from flask.ext.login import login_user, logout_user, login_required, current_user
from app import app, db, lm, avators, pics
from .forms import LoginForm, UserProfileForm, ProductInfoForm, AddUserForm, AddSupplyForm, AddTradeRecord
from .models import User, Image, Customer, Product, TradeRecord, Supply
import time


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    data = [
        [0, 40],
        [1, 9],
        [2, 6],
        [3, 10],
        [4, 5],
        [5, 17],
        [6, 6],
        [7, 10],
        [8, 7],
        [9, 11],
        [10, 35],
        [11, 9],
        [12, 12],
        [13, 5],
        [14, 3],
        [15, 4],
        [16, 9]
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,
                           data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    return render_template('user.html', user=user)


@app.route('/product_info/<product_id>')
@login_required
def product_info(product_id):
    product = Product.query.get(product_id)
    if product_id is None:
        flash('Product ' + product_id + 'not found.')
        return redirect(url_for('index'))
    return render_template('product_info.html', product=product)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
    return render_template("add_user.html", form=form)


@app.route('/add_supply', methods=['GET', 'POST'])
@login_required
def add_supply():
    form = AddSupplyForm()
    if form.validate_on_submit():
        supply = Supply()
        supply.name = form.name.data
        supply.city = form.city.data
        supply.buyer = form.buyer.data
        supply.order_contact = form.order_contact.data
        supply.tel = form.tel.data
        db.session.add(supply)
        db.session.commit()
    return render_template("add_supply.html", form=form)


@app.route('/add_traderecord', methods=['GET', 'POST'])
@login_required
def add_traderecord():
    form = AddTradeRecord()
    if form.validate_on_submit():
        traderecord = TradeRecord()
        bar_code = form.bar_code.data
        product = Product.query.filter_by(bar_code=bar_code)
        if product is not None:
            traderecord.product_id = product.id
            traderecord.quantity = form.quantity.data
            traderecord.banker = form.banker.data
            traderecord.customer = form.customer.data
            traderecord.time = time.localtime(time.time())
            db.session.add(traderecord)
            db.session.commit()
            return render_template("add_traderecord.html", traderecord=traderecord)
    return render_template("add_traderecord.html", form=form)


@app.route('/edit_profile/<uid>', methods=['GET', 'POST'])
@login_required
def edit_user_profile(uid):
    form = UserProfileForm()
    user = User.query.get(uid)
    if user is None:
        user = User()
    if form.validate_on_submit():
        filename = avators.save(request.files['avator'])
        img = Image(path="avatars/" + filename)
        db.session.add(img)
        db.session.commit()
        user.avator_id = img.id
        db.session.add(user)
        db.session.commit()
        # g.user.store()
        flash('photo saved')
        return redirect(url_for('index'))
    return render_template('edit-user-profile.html', form=form)


@app.route('/trade')
@login_required
def trade():
    trades = TradeRecord.query.all()
    return render_template('trade.html', trades=trades, Product=Product)


@app.route('/customers')
@login_required
def customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)


@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)


@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get(product_id)
    if product is not None:
        form = ProductInfoForm(name=product.product_name,
                               category=product.category,
                               bar_code=product.bar_code,
                               size=product.size,
                               inprice=product.inprice,
                               price=product.price,
                               supply=product.supply,
                               image=product.picture())
    else:
        form = ProductInfoForm()

    app.logger.error('start')
    app.logger.error(form.errors)
    if form.validate():
        app.logger.error('validate')

    if form.validate_on_submit():
        if product is None:
            product = Product()
        product.product_name = form.name.data
        product.category = form.category.data
        product.bar_code = form.bar_code.data
        product.size = form.size.data
        product.inprice = form.inprice.data
        product.price = form.price.data
        product.supply = form.supply.data
        try:
            filename = pics.save(request.files['image'])
            img = Image(path="pics/" + filename)
            db.session.add(img)
            db.session.commit()
            product.picture_id = img.id
        except Exception as e:
            app.logger.error(e)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('edit_product.html', form=form)


@app.route('/edit_supply/<supply_id>', methods=['GET', 'POST'])
@login_required
def edit_supply(supply_id):
    supply = Supply.query.get(supply_id)
    if supply is not None:
        form = AddSupplyForm(name=supply.name,
                             city=supply.city,
                             buyer=supply.buyer,
                             order_contact=supply.order_contact,
                             tel=supply.tel,
                             address=supply.address,
                             email=supply.email,
                             payment_mathod=supply.payment_method,
                             bank_account=supply.bank_account,
                             evidence=supply.evidence)
    else:
        form = AddSupplyForm()

    app.logger.error('start')
    app.logger.error(form.errors)
    if form.validate():
        app.logger.error('validate')

    if form.validate_on_submit():
        if supply is None:
            supply = Supply()

        supply.name = form.name.data
        supply.city = form.city.data
        supply.buyer = form.buyer.data
        supply.order_contact = form.order_contact.data
        supply.tel = form.tel.data
        supply.address = form.address.data
        supply.email = form.email.data
        supply.payment_mathod = form.payment_method.data
        supply.bank_account = form.bank_account.data
        supply.evidence = form.evidence.data
        db.session.add(supply)
        db.session.commit()
        return redirect(url_for('suppliers'))
    return render_template('edit_supply.html', form=form)


@app.route('/supply_detail/<supply_id>')
@login_required
def supply_detail(supply_id):
    supply = Supply.query.get(supply_id)

    return render_template('supply_detail.html', supply=supply)


@app.route('/staffs')
@login_required
def staffs():
    users = User.query.all()
    return render_template('staffs.html', users=users)


@app.route('/suppliers')
@login_required
def suppliers():
    suppliers = Supply.query.all()
    return render_template('suppliers.html', suppliers=suppliers)


@app.route('/project_info')
@login_required
def project_info():
    return render_template('project_info.html')


@lm.user_loader
def load_user(id):
    if id is None:
        return None
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
