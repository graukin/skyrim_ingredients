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
    'e <effect_name>' for list of ingredients with given effect
    'help' or 'h' for this message :)
    'quit' or 'exit' for exit'''

def print_all_ingredients():
    print 'All ingredients:'
    l=r.db(db_name).table(t_name).pluck('name').order_by(r.asc('name')).run(connection)
    for item in l:
        print ' ',item['name']
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
        res=item['name']
        if 'dlc' in item.keys():
            res=res+' ['+item['dlc']+']'
        print res

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

if __name__ == '__main__':
    sys.exit(main())
