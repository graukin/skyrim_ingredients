try:
    from colors import *
except ImportError:
    colors_lib=False
else:
    colors_lib=True

class ingr_printer:
    def __init__ (self):
        self.offset4 = '    '
        self.offset2 = '  '
        self.offset0 = ''
        self.use_colors=True

    def print_status(self):
        print colors_lib

    def try_to_color(self, text, fg_color=None, style_name=None):
        if colors_lib and self.use_colors:
            return color(text, fg=fg_color, style=style_name)
        else:
            return text

    def bake_ingredient_name(self, ingr, prefix):
        res=prefix
        if 'dlc' in ingr:
            res=res + self.try_to_color(ingr['name'] + ' [' + ingr['dlc'] + ']', style_name='italic')
        else:
            res=res + ingr['name']
        return res

    def bake_effect_name(self, effect_name, prefix):
        res=prefix
        if effect_name.startswith('Damage ') or effect_name.startswith('Lingering ') or effect_name.startswith('Ravage '):
            return res + self.try_to_color(effect_name, fg_color='red')
        elif effect_name.startswith('Weakness '):
            return res + self.try_to_color(effect_name, fg_color='yellow')
        elif effect_name.startswith('Fortify ') or effect_name.startswith('Restore '):
            return res + self.try_to_color(effect_name, fg_color='blue')
        elif effect_name.startswith('Resist '):
            return res + self.try_to_color(effect_name, fg_color='cyan')
        elif effect_name.startswith('Regenerate '):
            return res + self.try_to_color(effect_name, fg_color='magenta')
        else:
            return res + effect_name

    def print_all_ingredients(self, ingr_list):
        print 'Ingredients:'
        for ingr in ingr_list:
            print self.bake_ingredient_name(ingr, self.offset4)
        print len(ingr_list),'ingredient(s)'

    def print_all_effects(self, effect_list):
        print 'Effects:'
        for effect in effect_list:
            print self.bake_effect_name(effect, self.offset4)
        print len(effect_list),'effect(s)'

    def print_ingredient_info(self, ingr):
        print 'Name:', ingr['name']
        if 'dlc' in ingr.keys():
            print 'DLC: ', ingr['dlc']
        print 'Value:', ingr['value']
        print 'Weight:', ingr['weight']
        print 'Effects:'
        for e in ingr['effects']:
            print self.bake_effect_name(e, self.offset2)
        print 'Tip:', ingr['tip']

    def print_effect_info(self, ingr_list):
        for ingr in ingr_list:
            print self.bake_ingredient_name(ingr, self.offset2)

    def print_combination(self, ingr_list, effect_list):
        t_list=[]
        for ingredient in ingr_list:
            t_list.append(self.bake_ingredient_name(ingredient, self.offset0))
        r=' + '.join(t_list)
        t_list=[]
        for effect in effect_list:
            t_list.append(self.bake_effect_name(effect, self.offset0))
        r=r + ' -> ' + ', '.join(t_list)
        print r

    def print_combination_stack(self, stack):
        for el in stack:
            self.print_combination(el[0], el[1])
