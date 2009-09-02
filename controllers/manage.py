###########################################################
### make sure administrator is on localhost
############################################################

import os
from gluon.contenttype import contenttype
from gluon.fileutils import check_credentials, listdir

if not session.authorized and not request.function=='login':
    redirect(URL(r=request,f='login'))

response.view='manage.html'
response.menu=[['manage',True,'/%s/manage/index' % (request.application)],
               ['logout',False,'/%s/manage/logout' % (request.application)],
               ['back to store',False,'/%s/default/index' % (request.application)]]

###########################################################
### list all tables in database
############################################################

def login():
    response.view='manage/login.html'
    from gluon.fileutils import check_credentials
    if check_credentials(request,'admin'):
        session.authorized=True
        redirect(URL(r=request,f='index'))
    return dict()

def logout():
    session.authorized=False
    redirect(URL(r=request,c='default',f='index'))

def index():
    import types as _types
    _dbs={}
    for _key,_value in globals().items():
        try:
            if _value.__class__==SQLDB:
                tables=_dbs[_key]=[]   
                for _tablename in _value.tables():
                    tables.append((_key,_tablename))
        except: pass
    return dict(dbs=_dbs)

###########################################################
### insert a new record
############################################################

def insert():
    try:
        dbname=request.args[0]
        db=eval(dbname)
        table=request.args[1]
        form=SQLFORM(db[table])
    except: redirect(URL(r=request,f='index'))
    if form.accepts(request.vars,session):
        response.flash='new record inserted'
        redirect(URL(r=request,f='select',args=request.args))
    elif len(request.vars):
        response.flash='There are error in your submission form'
    return dict(form=form)

###########################################################
### list all records in table and insert new record
############################################################

def download():
    filename=request.args[0]
    response.headers['Content-Type']=contenttype(filename)
    return open(os.path.join(request.folder,'uploads/','%s' % filename),'rb').read()

def csv():
    import gluon.contenttype, csv, cStringIO
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    try:
        dbname=request.vars.dbname
        db=eval(dbname)
        records=db(request.vars.query).select()
    except: redirect(URL(r=request,f='index'))
    s=cStringIO.StringIO()
    writer = csv.writer(s)
    writer.writerow(records.colnames)
    c=range(len(records.colnames))
    for i in range(len(records)):
        writer.writerow([records.response[i][j] for j in c])
    ### FILL HERE
    return s.getvalue()

def import_csv(table,file):
    import csv
    reader = csv.reader(file)
    colnames=None
    for line in reader:
        if not colnames: 
            colnames=[x[x.find('.')+1:] for x in line]
            c=[i for i in range(len(line)) if colnames[i]!='id']            
        else:
            items=[(colnames[i],line[i]) for i in c]
            table.insert(**dict(items))

def select():
    try:
        dbname=request.args[0]
        db=eval(dbname)
        if not request.vars.query:
            table=request.args[1]
            query='%s.id>0' % table        
        else: query=request.vars.query
    except: redirect(URL(r=request,f='index'))
    if request.vars.csvfile!=None:        
        try:
            import_csv(db[table],request.vars.csvfile.file)
            response.flash='data uploaded'
        except: reponse.flash='unable to parse csv file'
    if request.vars.delete_all and request.vars.delete_all_sure=='yes':
        try:
            db(query).delete()
            response.flash='records deleted'
        except: response.flash='invalid SQL FILTER'
    elif request.vars.update_string:
        try:
            env=dict(db=db,query=query)
            exec('db(query).update('+request.vars.update_string+')') in env
            response.flash='records updated'
        except: response.flash='invalid SQL FILTER or UPDATE STRING'
    if request.vars.start: start=int(request.vars.start)
    else: start=0
    limitby=(start,start+100)
    try:
        records=db(query).select(limitby=limitby)
    except: 
        response.flash='invalid SQL FILTER'
        return dict(records='no records',nrecords=0,query=query,start=0)
    linkto=URL(r=request,f='update/%s'% (dbname))
    upload=URL(r=request,f='download')
    return dict(start=start,query=query,\
                nrecords=len(records),\
                records=SQLTABLE(records,linkto,upload,_class='sortable'))

###########################################################
### edit delete one record
############################################################

def update():
    try:
        dbname=request.args[0]
        db=eval(dbname)
        table=request.args[1]
    except: redirect(URL(r=request,f='index'))
    try:
        id=int(request.args[2])
        record=db(db[table].id==id).select()[0]
    except: redirect(URL(r=request,f='select/%s/%s'%(dbname,table)))
    form=SQLFORM(db[table],record,deletable=True,
                 linkto=URL(r=request,f='select/'+dbname),
                 upload=URL(r=request,f='download/'))
    if form.accepts(request.vars,session): 
        response.flash='done!'        
        redirect(URL(r=request,f='select/%s/%s'%(dbname,table)))
    return dict(form=form)

def cleanup():
    app=request.application
    files=listdir('applications/%s/cache/' % app,'',0)
    for file in files: os.unlink(file)
    files=listdir('applications/%s/errors/' % app,'',0)
    for file in files: os.unlink(file)
    files=listdir('applications/%s/sessions/' % app,'',0)
    for file in files: os.unlink(file)
    session.flash="cache, errors and sessions cleaned"
    redirect(URL(r=request,f='index'))

def setup():
    response.view='manage/setup.html'
    form=SQLFORM(store.info,mystore)
    if form.accepts(request.vars,session):
        response.flash='that was easy! now go vist your store.'
    else:
        response.flash='welcome to the store-in-a-stick setup'        
    return dict(form=form)