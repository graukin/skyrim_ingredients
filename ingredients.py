import rethinkdb as r
import sys
import os
import argparse
import json

from rethinkdb.errors import RqlRuntimeError, RqlDriverError

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015

prompt = '> '
db_name= 'games'
t_name = 'skyrim_ingredients'

connection = None

def work_out_args(argv):
    parser=argparse.ArgumentParser("")
    parser.add_argument("-l", "--load_data", help="load data in table")
    args = parser.parse_args()
    if args.load_data!=None:
        connect()
        if connection==None:
            exit()
        else:
            print "connected successfully"
            load_data(args.load_data)

def print_no_db():
    print "!!! You haven't got necessary table! Run"
    print ">$ ingredients.py --load_data <path_to_json>"
    print "to load data in your DB"

def connect():
    print "Try to connect..."
    global connection
    try:
        connection=r.connect(host=RDB_HOST, port=RDB_PORT);
    except RqlRuntimeError as e:
        print e

def close_all():
    global connection
    connection.close()

def connect_and_prepare(db, table_name):
    connect()
    if connection==None:
        print_no_db()
        return None
    elif r.db(db).table(table_name).count().run(connection) < 1:
        print_no_db()
        close_all()
        return None

def load_data(path2data):
    print "Try to load data from ", path2data
    l=r.db_list().run(connection)
    if not db_name in l:
       try:
           a=r.db_create(db_name).run(connection)
           if a['created']!=1:
              print "WTF?!"
              close_all()
              exit()
           print "database '", db_name, "' is created"
       except RqlRuntimeError as e:
           print e
           close_all()
    else:
       print "database '", db_name, "' already exists"
    l=r.db(db_name).table_list().run(connection)
    if not t_name in l:
        try:
            a=r.db(db_name).table_create(t_name).run(connection)
            if a['created']!=1:
               print "WTF?!"
               close_all()
               exit()
            print "table '", t_name, "' is created"
        except RqlRuntimeException as e:
            print e
            close_all()
    else:
        print "table '", t_name, "' already exists"

    json_data = open(path2data)
    data=json.load(json_data)
    json_data.close()
    cnt=0
    for item in data:
        print "Load data about ",item["name"]
        a=r.db(db_name).table(t_name).insert(item).run(connection)
        if a['errors']!=0:
            print "Oops! Something goes wrong"
            print a['first_error']
            close_all()
        cnt=cnt+a['inserted']
    print cnt, "new items are loaded"

def print_help():
    print "Commands:"
    print "  'all ingredients' or just 'ingredients' for the whole list of ingredients"
    print "  'all effects' or just 'effects' for the whole list of effects"
    print "  'help' or 'h' for this message :)"
    print "  'quit' or 'exit' for exit"

def print_all_ingredients():
    print "All ingredients"

def main(argv=None):
    work_out_args(argv)

    if connect_and_prepare(db_name, t_name)==None:
        exit();

    while True:
        string = raw_input(prompt)
        # for exit print "exit" or "quit"
        if string=="exit" or string=="quit":
            close_all();
            break
        if string=="help" or string=="h":
            print_help();
        elif string=="all ingredients" or string=="ingredients":
            print_all_ingredients();

if __name__ == "__main__":
    sys.exit(main())
