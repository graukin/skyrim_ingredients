import rethinkdb as r
import sys
import os
import argparse
import json

from rethinkdb.errors import RqlRuntimeError, RqlDriverError

RDB_HOST = os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015

prompt = '> '
db_name= 'games'
t_name = 'skyrim_ingredients'

connection = None

def work_out_args(argv):
    parser=argparse.ArgumentParser('')
    parser.add_argument('-l', '--load_data', help='load data in table')
    parser.add_argument('-f', '--force', action='store_true', help='use the Force, Luke')
    args = parser.parse_args()
    if args.load_data!=None:
        if connection==None:
            exit()
        else:
            print 'connected successfully'
            load_data(args.load_data, args.force)

def print_no_db():
    print '''!!! You haven't got necessary table (or some other problems occur)! Run
  >$ ingredients.py --load_data <path_to_json>
to load data in your DB'''

def connect():
    print 'Try to connect...'
    global connection
    try:
        connection=r.connect(host=RDB_HOST, port=RDB_PORT);
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

def print_help():
    print '''Commands:
    'all ingredients' or just 'ingredients' for the whole list of ingredients
    'all effects' or just 'effects' for the whole list of effects
    'i <ingredient_name>' for info about given ingredient. Case-sensitive :(
    'e <effect_name>' for list of ingredients with given effect. Also case-sensitive
    'c <effect1> [+ <effect2> [+ <effect3>]...]' for list of ingredients for given combination
    'm <ingredient1> + <ingredient2> [ + <ingredient3>] for result of mixing given ingredients
    'help' or 'h' for this message :)
    'quit' or 'exit' for exit'''

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

def print_ingredient(name):
    l=r.db(db_name).table(t_name).filter({'name' : name}).run(connection)
    for item in l:
        print_raw_ingredient(item)

def print_effect(name):
    l=r.db(db_name).table(t_name).filter(r.row['effects'].contains(name)).pluck('name', 'dlc').order_by(r.asc('name')).run(connection)
    for item in l:
        print construct_name(item, 'name', 'dlc')

def print_raw_combination(obj):
    res=''
    for key in obj.keys():
        if key.startswith('name'):
            res=res + ' + ' + construct_name(obj, key, 'dlc' if key=='name' else 'dlc'+key[4:])
    print res[3:], '->', ', '.join(obj['effects'])

def print_combination(effects):
    if len(effects)==1:
        l=r.db(db_name).table(t_name).filter(r.row['effects'].contains(effects[0])).inner_join(
            r.db(db_name).table(t_name).filter(r.row['effects'].contains(effects[0])),
            lambda lrow, rrow:
                lrow['name'] < rrow['name']
        ).map(
            lambda res:
                r.expr({
                    'name1' : res['left']['name'],
                    'dlc1' : r.branch(res['left'].has_fields('dlc'), res['left']['dlc'], None),
                    'name2' : res['right']['name'],
                    'dlc2' : r.branch(res['right'].has_fields('dlc'), res['right']['dlc'], None),
                    'effects' : res['left']['effects'].set_intersection(res['right']['effects'])
                })
        ).run(connection)
        for item in l:
            print_raw_combination(item)
    elif len(effects)==2:
        # dark magic starts here
        l=r.db(db_name).table(t_name).filter(r.row['effects'].contains(effects[0], effects[1])).inner_join(
            r.db(db_name).table(t_name).filter(r.row['effects'].contains(effects[0], effects[1])),
            lambda lrow, rrow:
                lrow['name'] < rrow['name']
        ).map(
            lambda res:
                r.expr({
                    'name1' : res['left']['name'],
                    'dlc1' : r.branch(res['left'].has_fields('dlc'), res['left']['dlc'], None),
                    'name2' : res['right']['name'],
                    'dlc2' : r.branch(res['right'].has_fields('dlc'), res['right']['dlc'], None),
                    'effects' : res['left']['effects'].set_intersection(res['right']['effects'])
                })
        ).run(connection)
        for item in l:
            print_raw_combination(item)
        l=r.db(db_name).table(t_name).filter(lambda row: row['effects'].contains(effects[0]) & ~row['effects'].contains(effects[1])).inner_join(
            r.db(db_name).table(t_name).filter(lambda row: ~row['effects'].contains(effects[0]) & row['effects'].contains(effects[1])),
            lambda lrow, rrow:
                lrow['name'] < rrow['name']
        ).map(
            lambda res:
                r.expr({
                    'name1' : res['left']['name'],
                    'dlc1' : r.branch(res['left'].has_fields('dlc'), res['left']['dlc'], None),
                    'name2' : res['right']['name'],
                    'dlc2' : r.branch(res['right'].has_fields('dlc'), res['right']['dlc'], None),
                    'effects1' : res['left']['effects'],
                    'effects2' : res['right']['effects']
                })
        ).inner_join(
            r.db(db_name).table(t_name).filter(r.row['effects'].contains(effects[0], effects[1])),
            lambda lrow, rrow:
                lrow['name1'].ne(rrow['name']) &
                lrow['name2'].ne(rrow['name'])
        ).map(
            lambda res:
                r.expr({
                     'name1' : res['left']['name1'],
                     'dlc1' : res['left']['dlc1'],
                     'name2' : res['left']['name2'],
                     'dlc2' : res['left']['dlc2'],
                     'name3' : res['right']['name'],
                     'dlc3' : r.branch(res['right'].has_fields('dlc'), res['right']['dlc'], None),
                     'effects' : res['left']['effects1'].set_intersection(res['left']['effects2']).set_union(
                     res['left']['effects1'].set_intersection(res['right']['effects'])).set_union(
                     res['left']['effects2'].set_intersection(res['right']['effects'])).distinct()
                })
        ).run(connection)
        for item in l:
            print_raw_combination(item)

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
    l1=get_effect_list(ingredients[0])
    l2=get_effect_list(ingredients[1])
    if len(ingredients) == 2:
        if l1==None or l2==None:
            res=None
        else:
            res=[val for val in l1 if val in l2]
    else:
        l3=get_effect_list(ingredients[2])
        if l1==None or l2==None or l3==None:
            res=None
        else:
            res=[val for val in l1 if val in l2]
            res2=[val for val in l1 if val in l3]
            res3=[val for val in l2 if val in l3]
            for val in res2:
                if not val in res:
                    res.append(val)
            for val in res3:
                if not val in res:
                    res.append(val)
    if res==None:
        print ' + '.join(ingredients), '-> Nothing'
    else:
        print ' + '.join(ingredients), '->', ', '.join(res)

def main(argv=None):
    connect()
    work_out_args(argv)
    if not check():
        close_all()
        return
    while True:
        string = raw_input(prompt)
        # for exit print 'exit' or 'quit'
        if string=='exit' or string=='quit':
            close_all()
            break
        if string=='help' or string=='h':
            print_help()
        elif string=='all ingredients' or string=='ingredients':
            print_all_ingredients()
        elif string=='all effects' or string=='effects':
            print_all_effects()
        elif string.startswith('i ') and len(string) > 2:
            print_ingredient(string[2:])
        elif string.startswith('e ') and len(string) > 2:
            print_effect(string[2:])
        elif string.startswith('c ') and len(string) > 2:
            l=string[2:].split('+')
            l=map(str.strip, l)
            print_combination(l)
        elif string.startswith('m ') and len(string) > 2:
            l=string[2:].split('+')
            l=map(str.strip, l)
            print_mix_result(l)
        else:
            print 'Unknown command. Try "h" or "help"'

if __name__ == '__main__':
    sys.exit(main())
