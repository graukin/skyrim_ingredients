import rethinkdb as r
import os

from rethinkdb.errors import RqlRuntimeError, RqlDriverError

RDB_HOST = os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015

connection = None
db_name= 'games'
t_name = 'skyrim_ingredients'

def print_no_db():
    print '''!!! You haven't got necessary table (or some other problems occur)! Run
  >$ ingredients.py --load_data <path_to_json>
to load data in your DB'''

def connect():
    print 'Try to connect...'
    global connection
    try:
        connection=r.connect(host=RDB_HOST, port=RDB_PORT);
        print 'connected successfully'
    except RqlRuntimeError as e:
        print e

def close_all():
    global connection
    connection.close()
    print 'Close connection'

def check():
    if connection==None:
        print_no_db()
        return False
    elif not db_name in r.db_list().run(connection):
        print_no_db()
        return False
    elif not t_name in r.db(db_name).table_list().run(connection):
        print_no_db()
        return False
    elif r.db(db_name).table(t_name).count().run(connection) < 1:
        print_no_db()
        return False
    return True

# load data from file into db

def load_data(path2data, force_load):
    print 'Try to load data from ', path2data
    l=r.db_list().run(connection)
    if not db_name in l:
       try:
           a=r.db_create(db_name).run(connection)
           if a['created']!=1:
              print 'WTF?!'
              close_all()
              exit()
           print 'database "', db_name, '" is created'
       except RqlRuntimeError as e:
           print e
           close_all()
    else:
       print 'database "', db_name, '" already exists'
    l=r.db(db_name).table_list().run(connection)
    if not t_name in l:
        try:
            a=r.db(db_name).table_create(t_name).run(connection)
            if a['created']!=1:
               print 'WTF?!'
               close_all()
               exit()
            print 'table "', t_name, '" is created'
        except RqlRuntimeException as e:
            print e
            close_all()
    else:
        print 'table "', t_name, '" already exists'
        if not force_load:
            if r.db(db_name).table(t_name).count().run(connection) > 0:
                print 'There is something in your table'
                return

    json_data = open(path2data)
    data=json.load(json_data)
    json_data.close()
    cnt=0
    for item in data:
        print 'Load data about ',item['name']
        a=r.db(db_name).table(t_name).insert(item).run(connection)
        if a['errors']!=0:
            print 'Oops! Something goes wrong'
            print a['first_error']
            close_all()
        cnt=cnt+a['inserted']
    print cnt, 'new items are loaded'

# work with data

# from object obj { name_key : name, dlc_key : dlc(optional)} get 'name' or 'name [dlc]'
def construct_name(obj, name_key, dlc_key):
    if dlc_key in obj.keys() and obj[dlc_key] != None:
         return obj[name_key] + ' [' + obj[dlc_key] + ']'
    return obj[name_key]

def print_all_ingredients():
    print 'All ingredients:'
    l=r.db(db_name).table(t_name).pluck('name', 'dlc').order_by(r.asc('name')).run(connection)
    for item in l:
        print ' ', construct_name(item, 'name', 'dlc')
    print r.db(db_name).table(t_name).count().run(connection), 'ingredient(s)'

def print_all_effects():
    print 'All effects:'
    l=r.db(db_name).table(t_name).concat_map(lambda ingr: ingr['effects']).distinct().run(connection)
    for item in l:
        print ' ',item
    print len(l), 'effect(s)'

def print_raw_ingredient(obj):
    print 'Name:', obj['name']
    if 'dlc' in obj.keys():
        print 'DLC: ', obj['dlc']
    print 'Value:', obj['value']
    print 'Weight:', obj['weight']
    print 'Effects:'
    for e in obj['effects']:
        print ' ', e
    print 'Tip:', obj['tip']

def get_ingredient(name):
    l=r.db(db_name).table(t_name).filter({'name' : name}).limit(1).run(connection)
    res=None
    for item in l:
        res=item
    return res

def print_ingredient(name):
    l=get_ingredient(name)
    print_raw_ingredient(l)

def get_effect(name):
    l=r.db(db_name).table(t_name).filter(r.row['effects'].contains(name)).pluck('name', 'dlc', 'effects').order_by(r.asc('name')).run(connection)
    return l

def print_effect(name):
    l=get_effect(name)
    for item in l:
        print construct_name(item, 'name', 'dlc')

def print_raw_combination(obj):
    res=''
    for key in obj.keys():
        if key.startswith('name'):
            res=res + ' + ' + construct_name(obj, key, 'dlc' if key=='name' else 'dlc'+key[4:])
    print res[3:], '->', ', '.join(obj['effects'])

def check_combination(ingr_list, check_list):
    e_map={};
    for ingr in ingr_list:
        for e in ingr['effects']:
            if e in e_map:
                e_map[e] = e_map[e] + 1
            else:
                e_map[e] = 1;
    res_list=[val for val in e_map if e_map[val]>1]
    if check_list != None:
        for ef in check_list:
            if not ef in res_list:
                return []
    return res_list

def print_combination(effects):
    ingr_map={}
    for effect in effects:
        l=get_effect(effect)
        for item in l:
            if not item['name'] in ingr_map:
                ingr_map[item['name']]=item

    # 2 ingredients
    for in1 in ingr_map:
        for in2 in ingr_map:
            if in1 < in2:
                combo = check_combination([ingr_map[in1], ingr_map[in2]], effects)
                if combo != None and len(combo) > 0:
                    print construct_name(ingr_map[in1], 'name', 'dlc'), '+', construct_name(ingr_map[in2], 'name', 'dlc'), '->', ', '.join(combo)
    # 3 ingredients
    for in1 in ingr_map:
        for in2 in ingr_map:
            for in3 in ingr_map:
                if in1 < in2 and in2 < in3:
                    combo = check_combination([ingr_map[in1], ingr_map[in2], ingr_map[in3]], effects)
                    if combo != None and len(combo) > 0:
                        print construct_name(ingr_map[in1], 'name', 'dlc'), '+', construct_name(ingr_map[in2], 'name', 'dlc'), '+', construct_name(ingr_map[in3], 'name', 'dlc'), '->', ', '.join(combo)

def get_effect_list(ingredient):
    l=r.db(db_name).table(t_name).filter(r.row['name']==ingredient).pluck('effects').run(connection)
    res_list=[]
    for item in l:
        res_list=item['effects']
    if len(res_list) != 4:
        return None
    return res_list

def print_mix_result(ingredients):
    if len(ingredients) < 2 or len(ingredients) > 3:
        print 'You need mix 2 or 3 ingredients for potion'
        return
    res=None
    ingr_list=[]
    ingr_list.append(get_ingredient(ingredients[0]))
    ingr_list.append(get_ingredient(ingredients[1]))
    if len(ingredients) == 3:
        ingr_list.append(get_ingredient(ingredients[2]))
    res=check_combination(ingr_list, None)
    if res==None:
        print ' + '.join(ingredients), '-> Nothing'
    else:
        print ' + '.join(ingredients), '->', ', '.join(res)
