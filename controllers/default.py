
if not session.chart: session.chart, session.balance={},0
app=request.application
response.menu=\
 [['Store Front',request.function=='index','/%s/default/index'%app],
  ['About Us',request.function=='aboutus','/%s/default/aboutus'%app],
  ['Contact Us',request.function=='contactus','/%s/default/contactus'%app],
  ['Shopping Chart $%.2f'%float(session.balance),request.function=='checkout',
   '/%s/default/checkout'%app]]

session.google_merchant_id=mystore.google_merchant_id

if not session.google_merchant_id:
    session.flash = 'Need to add a Google Checkout ID'
    redirect(URL(r=request, c='manage', f='index'))

def index():
    categories=store(store.category.id > 0).select(orderby=store.category.name)
    featured=store(store.product.featured=='T')\
             .select(orderby=~store.product.id)
    return dict(categories=categories,featured=featured)

def category():
    if len(request.args) < 1: redirect(URL(r=request,f='index'))
    category=int(request.args[0])
    if len(request.args) == 3: 
        start,stop=int(request.args[1]),int(request.args[2])
    else:
        start, stop = 0, 20
    categories = store(store.category.id>0).select(orderby=store.category.name)
    for item in categories: 
        if item.id == category:
            category_name=item.name
    if start == 0: featured=store(store.product.featured=='T')\
                  (store.product.category==category)\
                  .select(orderby=~store.product.id)
    else: featured = []
    ids = [p.id for p in featured]
    favourites = store(store.product.category==category)\
                  .select(orderby=~store.product.rating, limitby=(start,stop))
    favourites = [f for f in favourites if not f.id in ids] 
    return dict(category_name=category_name, categories=categories,
                featured=featured, favourites=favourites)

def product():
    if not request.args: redirect(URL(r=request, f='index'))
    product_name = request.args[0].replace('_', ' ') # XXX need proper way to deal with whitespace
    products = store(store.product.name == product_name).select()
    if not products: redirect(URL(r=request, f='index'))
    product = products[0]
    product.update_record(viewed=product.viewed+1)
    # post a comment about a product    
    form = SQLFORM(store.comment, fields=['author', 'email', 'body', 'rate'])
    form.vars.product = product.id
    nc = store(store.comment.product == product.id).count()
    if form.accepts(request.vars, session):
        t = products[0].rating*nc + int(form.vars.rate)
        products[0].update_record(rating=t/(nc+1))
        response.flash = 'comment posted'
    if form.errors: response.flash = 'please check your form below'
    comments = store(store.comment.product == product.id).select(orderby=~store.comment.id)
    related_ids = [row.better for row in store(store.up_sell.product == product.id).select(store.up_sell.better)] \
                + [row.related for row in store(store.cross_sell.product == product.id).select(store.cross_sell.related)]
    related = store(store.product.id.belongs(related_ids)).select()
    return dict(product=product, comments=comments, related=related, form=form)


def add_to_chart():
    # allow add to chart
    pid=request.args[0]
    product=store(store.product.id == pid).select()[0]
    product.update_record(clicked=product.clicked+1)
    try: qty = session.chart[pid] + 1
    except: qty = 1
    session.chart[pid] = qty
    session.balance += product.price
    redirect(URL(r=request, f='checkout'))

def remove_from_chart():
    # allow add to chart
    pid=request.args[0]
    product=store(store.product.id == pid).select()[0]
    if session.chart.has_key(pid):
        session.balance -= product.price
        session.chart[pid] -= 1
        if not session.chart[pid]: del session.chart[pid]
    redirect(URL(r=request,f='checkout'))

def empty_chart():
    # allow add to chart
    session.chart, session.balance = {}, 0
    redirect(URL(r=request, f='checkout'))

def checkout():
    pids = session.chart.keys()
    chart = {}
    pids = session.chart.keys()
    products = {}
    for pid in pids: products[pid] = store(store.product.id==pid).select()[0]
    return dict(products=products, merchant_id=session.google_merchant_id)

def popup():
    return dict()

def show():
    response.session_id=None
    import gluon.contenttype, os
    filename = request.args[0]
    response.headers['Content-Type'] = gluon.contenttype.contenttype(filename)
    return open(os.path.join(request.folder,'uploads/', '%s' % filename), 'rb').read()

def aboutus(): return dict()

def contactus(): return dict()
