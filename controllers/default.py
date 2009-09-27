
if not session.cart:
    # instantiate new cart
    session.cart, session.balance = [], 0
session.google_merchant_id = mystore.google_merchant_id

    
response.menu = [
  ['Store Front', request.function == 'index', URL(r=request, f='index')],
  ['About Us', request.function == 'aboutus', URL(r=request, f='aboutus')],
  ['Contact Us', request.function == 'contactus', URL(r=request, f='contactus')],
  ['Shopping Cart $%.2f' % float(session.balance), request.function == 'checkout', URL(r=request, f='checkout')]
]



def index():
    categories = store().select(store.category.ALL, orderby=store.category.name)
    featured = store(store.product.featured == True).select()
    return dict(categories=categories,featured=featured)

def category():
    if not request.args: redirect(URL(r=request, f='index'))
    category_id = pretty_id(request.args[0])
    if len(request.args) == 3:
        # pagination
        start, stop = int(request.args[1]), int(request.args[2])
    else:
        start, stop = 0, 20
    categories = store().select(store.category.ALL, orderby=store.category.name)
    category_name = None
    for category in categories: 
        if category.id == category_id:
            response.title = category_name = category.name
    if not category_name: redirect(URL(r=request, f='index'))
    if start == 0:
        featured = store(store.product.featured == True)(store.product.category == category_id).select()
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
    response.title = product.name
    product.update_record(viewed=product.viewed+1)
    
    options = store(store.option.product == product.id).select()    
    product_form = FORM(
        TABLE(
            [TR(TD(INPUT(_name='option', _value=option.id, _type='checkbox', _onchange="update_price(this, %.2f)" % option.price), option.description), H3('$%.2f' % option.price)) for option in options],        
            TR(
                'Price:',
                H2('$%.2f' % float(product.price), _id='total_price')
            ),
            BR(),
            TH('Qty:', INPUT(_name='quantity', _class='integer', _value=1, _size=1)), INPUT(_type='submit', _value='Add to cart'),
        )
    )
    if product_form.accepts(request.vars, session):  
        quantity = int(product_form.vars.quantity)
        option_ids = product_form.vars.option
        if not isinstance(option_ids, list):
            option_ids = [option_ids] if option_ids else []
        option_ids = [int(o) for o in option_ids]
        
        product.update_record(clicked=product.clicked+1)    
        session.cart.append((product_id, quantity, option_ids))
        redirect(URL(r=request, f='checkout'))
    
    
    # post a comment about a product    
    comment_form = SQLFORM(store.comment, fields=['author', 'email', 'body', 'rate'])
    comment_form.vars.product = product.id
    if comment_form.accepts(request.vars, session):
        nc = store(store.comment.product == product.id).count()
        t = products[0].rating*nc + int(comment_form.vars.rate)
        products[0].update_record(rating=t/(nc+1))
        response.flash = 'comment posted'
    if comment_form.errors: response.flash = 'invalid comment'
    comments = store(store.comment.product == product.id).select()
    
    better_ids = [row.better for row in store(store.up_sell.product == product.id).select(store.up_sell.better)]
    related_ids = [row.p2 for row in store(store.cross_sell.p1 == product.id).select()] + [row.p1 for row in store(store.cross_sell.p2 == product.id).select()]
    suggested = [] # XXXstore(store.product.id.belongs(better_ids + related_ids)).select()
    return dict(product=product, comments=comments, options=options, suggested=suggested, product_form=product_form, comment_form=comment_form)



"""


{{ if product.old_price: }}
<b>was ${{= '%.2f' % float(product.old_price) }}</b>
{{ pass }}
</form>

"""

def remove_from_cart():
    # remove product from cart
    del session.cart[int(request.args[0])]
    redirect(URL(r=request, f='checkout'))

def empty_cart():
    # empty cart of all products
    session.cart.clear()
    session.balance = 0
    redirect(URL(r=request, f='checkout'))


def checkout():
    order = []
    balance = 0
    for product_id, qty, option_ids in session.cart:
        products = store(store.product.id == product_id).select()
        if products:
            product = products[0]
            options = [store.option[id] for id in option_ids]# XXX store(store.option.id.belongs(option_ids)).select() if option_ids else []
            total_price = qty * (product.price + sum([option.price for option in options]))
            order.append((product_id, qty, total_price, product, options))
            balance += total_price
        else:
            # invalid product
            pass
    session.balance = balance # XXX is updating in time?
    return dict(order=order, merchant_id=session.google_merchant_id)

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
