import os
import json
import brush as b

class ingr_printer:
    def __init__ (self, file_name):
        self.offset4 = '    '
        self.offset2 = '  '
        self.offset0 = ''
        config_data = open(file_name)
        config=json.load(config_data)
        config_data.close()
        self.load_common(config['common'])
        self.load_ingredients(config['ingredients'])
        self.load_effects(config['effects'])

# load use_colors
    def load_common(self, section):
        self.use_colors = True if section['use_colors']=='True' else False

# load brushes for ingredients
    def load_ingredients(self, section):
        self.ingr_brushes={}
        for brush in section:
            self.ingr_brushes[brush['name']] = b.Brush(brush)

#load brushes for effects
    def load_effects(self, section):
        self.effects_brushes={}
        for brush in section:
            self.effects_brushes[brush['name']] = b.Brush(brush)

    def print_status(self):
        print self.use_colors

    def bake_ingredient_name(self, ingr, prefix):
        name=ingr['name'] + (' [' + ingr['dlc'] + ']' if 'dlc' in ingr else '');
        for brush in self.ingr_brushes:
            if self.ingr_brushes[brush].check_object(ingr):
                name=self.ingr_brushes[brush].color_text(name)
        return prefix + name

    def bake_effect_name(self, effect_name, prefix):
        for brush in self.effects_brushes:
            if self.effects_brushes[brush].check_marker(effect_name):
                effect_name=self.effects_brushes[brush].color_text(effect_name)
        return prefix + effect_name

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
