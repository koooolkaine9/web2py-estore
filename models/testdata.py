if False: # set to True to insert test data    
    store(store.product.id > 0).delete()
    store(store.category.id > 0).delete()
    if len(store(store.product.id > 0).select()) == 0:
        fantasy_id = store.category.insert(name='Fantasy', description='Fantasy books', small_image='testdata/hp1.jpg')
        hp1 = store.product.insert(name="Harry Potter and the Sorcerer's Stone", category=fantasy_id, price=7.91, small_image='testdata/hp1.jpg')
        hp2 = store.product.insert(name="Harry Potter and the Chamber of Secrets", category=fantasy_id, price=8.91, small_image='testdata/hp2.jpg')
        hp3 = store.product.insert(name="Harry Potter and the Prisoner of Azkaban", category=fantasy_id, price=8.91, small_image='testdata/hp3.jpg')
        hp4 = store.product.insert(name="Harry Potter and the Goblet of Fire", category=fantasy_id, price=9.91, small_image='testdata/hp4.jpg')
        hp5 = store.product.insert(name="Harry Potter and the Order of the Phoenix", category=fantasy_id, price=9.91, small_image='testdata/hp5.jpg')
        hp6 = store.product.insert(name="Harry Potter and the Half-Blood Prince", category=fantasy_id, price=9.91, small_image='testdata/hp6.jpg')
        
        store.option.insert(product=hp1, description='Bookmark', price=1.5)
        store.option.insert(product=hp1, description='Hat', price=12)
        
        for p2 in (hp2, hp3, hp4, hp5, hp6):
            store.cross_sell.insert(p1=hp1, p2=p2)
            
        hp1_hard = store.product.insert(name="Harry Potter and the Sorcerer's Stone [hardcover]", category=fantasy_id, price=15.91, small_image='testdata/hp1.jpg')
        store.up_sell.insert(product=hp1, better=hp1_hard)
        