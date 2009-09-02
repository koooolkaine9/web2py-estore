# try something like
store=SQLDB("sqlite://store.db")

store.define_table('category',
  SQLField('name'),
  SQLField('headline',length=512))

store.define_table('product',
  SQLField('name'),
  SQLField('category',store.category),
  SQLField('short_description',length=512),
  SQLField('long_description','text',default=''),
  SQLField('small_image','upload'),
  SQLField('large_image','upload',default=''),
  SQLField('quantity_in_stock','integer',default=0),
  SQLField('price','double',default=1.00),
  SQLField('old_price','double',default=0.0),
  SQLField('weight_in_pounds','double',default=1),
  SQLField('tax_rate_in_your_state','double',default=10.0),
  SQLField('tax_rate_outside_your_state','double',default=0.00),
  SQLField('featured','boolean',default='T'),
  SQLField('allow_rating','boolean',default='T'),
  SQLField('rating','integer',default='0'),
  SQLField('viewed','integer',default='0'),
  SQLField('clicked','integer',default='0'))

store.define_table('comment',
  SQLField('product',store.product),
  SQLField('author'),
  SQLField('email'),
  SQLField('body','text'),
  SQLField('rate','integer'))

store.define_table('info',
  SQLField('google_merchant_id',length=256),
  SQLField('name',default='[store name]'),
  SQLField('headline',length=64,default='[store headline]'),
  SQLField('address',default='[store address]'),
  SQLField('city',default='[store city]'),
  SQLField('state',length=2,default='[store state]'),
  SQLField('zip_code',length=10,default='[store zip]'),
  SQLField('phone',default='[store phone number]'),
  SQLField('fax',default='[store fax number]'),
  SQLField('email',requires=IS_EMAIL(),default='yourname@yourdomain.com'),
  SQLField('description','text',default='[about your store]'),
  SQLField('why_buy','text',default='[why buy at your store]'),
  SQLField('return_policy','text',default='[what is your return policy]'),

  SQLField('logo','upload',default=''),
  SQLField('color_background',length=10,default='white'),
  SQLField('color_foreground',length=10,default='black'),
  SQLField('color_header',length=10,default='#339900'),
  SQLField('color_link',length=10,default='#ff0033'),
  SQLField('font_family',length=32,default='arial, helvetica'),

  SQLField('ship_usps_express_mail','boolean',default=True),
  SQLField('ship_usps_express_mail_fc','double',default=0),
  SQLField('ship_usps_express_mail_vc','double',default=0),
  SQLField('ship_usps_express_mail_bc','double',default=0),
  SQLField('ship_usps_priority_mail','boolean',default=True),
  SQLField('ship_usps_priority_mail_fc','double',default=0),
  SQLField('ship_usps_priority_mail_vc','double',default=0),
  SQLField('ship_usps_priority_mail_bc','double',default=0),
  SQLField('ship_ups_next_day_air','boolean',default=True),
  SQLField('ship_ups_next_day_air_fc','double',default=0),
  SQLField('ship_ups_next_day_air_vc','double',default=0),
  SQLField('ship_ups_next_day_air_bc','double',default=0),
  SQLField('ship_ups_second_day_air','boolean',default=True),
  SQLField('ship_ups_second_day_air_fc','double',default=0),
  SQLField('ship_ups_second_day_air_vc','double',default=0),
  SQLField('ship_ups_second_day_air_bc','double',default=0),
  SQLField('ship_ups_ground','boolean',default=True),
  SQLField('ship_ups_ground_fc','double',default=0),
  SQLField('ship_ups_ground_vc','double',default=0),
  SQLField('ship_ups_ground_bc','double',default=0),
  SQLField('ship_fedex_priority_overnight','boolean',default=True),
  SQLField('ship_fedex_priority_overnight_fc','double',default=0),
  SQLField('ship_fedex_priority_overnight_vc','double',default=0),
  SQLField('ship_fedex_priority_overnight_bc','double',default=0),
  SQLField('ship_fedex_second_day','boolean',default=True),
  SQLField('ship_fedex_second_day_fc','double',default=0),
  SQLField('ship_fedex_second_day_vc','double',default=0),
  SQLField('ship_fedex_second_day_bc','double',default=0),
  SQLField('ship_fedex_ground','boolean',default=True),
  SQLField('ship_fedex_ground_fc','double',default=0),
  SQLField('ship_fedex_ground_vc','double',default=0),
  SQLField('ship_fedex_ground_bc','double',default=0)
)

#store(store.info.id>0).delete()
if len(store(store.info.id>0).select())==0:
    store.info.insert(name='[store name]')
mystore=store(store.info.id>0).select()[0]

store.product.category.requires=IS_IN_DB(store,'category.id','category.name')
store.product.name.requires=IS_NOT_EMPTY()
store.product.short_description.requires=IS_NOT_EMPTY()
store.product.quantity_in_stock.requires=IS_INT_IN_RANGE(0,1000)
store.product.price.requires=IS_FLOAT_IN_RANGE(0,10000)
store.product.rating.requires=IS_INT_IN_RANGE(-10000,10000)
store.product.viewed.requires=IS_INT_IN_RANGE(0,1000000)
store.product.clicked.requires=IS_INT_IN_RANGE(0,1000000)
store.comment.product.requires=IS_IN_DB(store,'product.id','product.name')
store.comment.author.requires=IS_NOT_EMPTY()
store.comment.email.requires=IS_EMAIL()
store.comment.body.requires=IS_NOT_EMPTY()
store.comment.rate.requires=IS_IN_SET(range(5,0,-1))
for field in store.info.fields:
    if field[:-2] in ['fc','vc']:
        store.info[field].requires=IS_FLOAT_IN_RANGE(0,100)
mystore=store(store.info.id>0).select()[0]