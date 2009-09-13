
if not session.cart:
    # instantiate new cart
    session.cart, session.balance = {}, 0
session.google_merchant_id = mystore.google_merchant_id

    
response.menu = [
  ['Store Front', request.function == 'index', URL(r=request, f='index')],
  ['About Us', request.function == 'aboutus', URL(r=request, f='aboutus')],
  ['Contact Us', request.function == 'contactus', URL(r=request, f='contactus')],
  ['Shopping Cart $%.2f' % float(session.balance), request.function == 'checkout', URL(r=request, f='checkout')]
]



def index():
    categories = store(store.category.id > 0).select(orderby=store.category.name)
    featured = store(store.product.featured == True).select(orderby=~store.product.id)
    return dict(categories=categories,featured=featured)

def category():
    if not request.args: redirect(URL(r=request, f='index'))
    category_id = pretty_id(request.args[0])
    if len(request.args) == 3: 
        start, stop = int(request.args[1]), int(request.args[2])
    else:
        start, stop = 0, 20
    categories = store(store.category.id > 0).select(orderby=store.category.name)
    for category in categories: 
        if category.id == category_id:
            category_name = category.name
    if start == 0:
        featured = store(store.product.featured == True)(store.product.category == category_id).select(orderby=~store.product.id)
    else:
        featured = []
    ids = [p.id for p in featured]
    favourites = store(store.product.category == category_id).select(orderby=~store.product.rating, limitby=(start, stop))
    favourites = [f for f in favourites if f.id not in ids] 
    return dict(category_name=category_name, categories=categories, featured=featured, favourites=favourites)

def product():
    if not request.args: redirect(URL(r=request, f='index'))
    product_id = pretty_id(request.args[0])
    products = store(store.product.id == product_id).select()
    if not products: redirect(URL(r=request, f='index'))
    product = products[0]
    product.update_record(viewed=product.viewed+1)
    
    # post a comment about a product    
    form = SQLFORM(store.comment, fields=['author', 'email', 'body', 'rate'])
    form.vars.product = product.id
    if form.accepts(request.vars, session):
        nc = store(store.comment.product == product.id).count()
        t = products[0].rating*nc + int(form.vars.rate)
        products[0].update_record(rating=t/(nc+1))
        response.flash = 'comment posted'
    if form.errors: response.flash = 'please check your form below'
    comments = store(store.comment.product == product.id).select(orderby=~store.comment.id)
    
    options = store(store.option.product == product.id).select(orderby=store.option.id)
    related_ids = [row.better for row in store(store.up_sell.product == product.id).select(store.up_sell.better)] \
                + [row.p2 for row in store(store.cross_sell.p1 == product.id).select()] \
                + [row.p1 for row in store(store.cross_sell.p2 == product.id).select()]
    related = store(store.product.id.belongs(related_ids)).select()
    return dict(product=product, comments=comments, options=options, related=related, form=form)


def add_to_cart():
    # add product to cart
    # XXX add support for adding multiple at once
    pid = request.args[0]
    product = store(store.product.id == pid).select()[0]
    product.update_record(clicked=product.clicked+1)    
    session.cart[pid] = session.cart.get(pid, 0) + 1
    session.balance += product.price
    redirect(URL(r=request, f='checkout'))

def remove_from_cart():
    # remove product from cart
    pid = request.args[0]
    product = store(store.product.id == pid).select()[0]
    if pid in session.cart:
        qty = session.cart[pid]
        session.balance -= qty * product.price
        del session.cart[pid]
    redirect(URL(r=request, f='checkout'))

def empty_cart():
    # empty cart of all products
    session.cart, session.balance = {}, 0
    redirect(URL(r=request, f='checkout'))


def checkout():
    products = {}
    balance = 0
    for pid in session.cart.keys():
        product = store.product[pid]
        if product:
            products[pid] = product
            qty = session.cart[pid]
            balance += qty * product.price
        else:
            # invalid product
            del session.cart[pid]
    session.balance = balance
    return dict(products=products, merchant_id=session.google_merchant_id)

def popup():
    return dict()

def show():
    response.session_id = None
    import gluon.contenttype, os
    filename = '/'.join(request.args)
    response.headers['Content-Type'] = gluon.contenttype.contenttype(filename)
    # XXX is this path going to be a problem on Windows?
    return open(os.path.join(request.folder, 'uploads', filename), 'rb').read()

def aboutus(): return dict()

def contactus(): return dict()
