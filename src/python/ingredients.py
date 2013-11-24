import sys
import argparse
import json

import db_commands as db
import ingr_printer as pr

prompt = '> '
printer = None

def work_out_args(argv):
    parser=argparse.ArgumentParser('')
    parser.add_argument('-l', '--load_data', help='load data in table')
    parser.add_argument('-f', '--force', action='store_true', help='use the Force, Luke')
    args = parser.parse_args()
    if args.load_data!=None:
        if connection==None:
            exit()
        else:
            db.load_data(args.load_data, args.force)

def prepare_printer():
    global printer
    printer = pr.ingr_printer()

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

def main(argv=None):
    db.connect()
    work_out_args(argv)
    prepare_printer()
    if not db.check():
        db.close_all()
        return
    while True:
        string = raw_input(prompt)
        # for exit print 'exit' or 'quit'
        if string=='exit' or string=='quit':
            db.close_all()
            break
        if string=='help' or string=='h':
            print_help()
        elif string=='all ingredients' or string=='ingredients':
            printer.print_all_ingredients(db.get_all_ingredients())
        elif string=='all effects' or string=='effects':
            printer.print_all_effects(db.get_all_effects())
        elif string.startswith('i ') and len(string) > 2:
            printer.print_ingredient_info(db.get_ingredient(string[2:]))
        elif string.startswith('e ') and len(string) > 2:
            printer.print_effect_info(db.get_effect(string[2:]))
        elif string.startswith('c ') and len(string) > 2:
            l=string[2:].split('+')
            l=map(str.strip, l)
            printer.print_combination_stack(db.get_combinations(l))
        elif string.startswith('m ') and len(string) > 2:
            l=string[2:].split('+')
            l=map(str.strip, l)
            i_list=[]
            for i in l:
                i_list.append(db.get_ingredient(i))
            printer.print_combination_stack([[i_list, db.get_mix_result(l)]])
        else:
            print 'Unknown command. Try "h" or "help"'

if __name__ == '__main__':
    sys.exit(main())
