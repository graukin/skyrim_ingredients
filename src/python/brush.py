try:
    from colors import *
except ImportError:
    colors_lib=False
else:
    colors_lib=True

class Brush:
    def __init__ (self, terms):
        print terms
        self.type_ = self.get_from_map(terms, 'type')
        self.field_ = self.get_from_map(terms, 'field')
        self.marker_ = self.get_from_map(terms, 'marker')
        self.color_ = self.get_from_map(terms['brush'], 'color')
        self.style_ = self.get_from_map(terms['brush'], 'style')

    def get_from_map(self, map_, field_, default_=None):
        return map_[field_] if field_ in map_ else default_

    def check_object(self, obj):
        if self.field_ != None and self.field_ in obj:
            return self.check_marker(obj[self.field_])
        else:
            return False

    def check_marker(self, text):
        if self.type_ == None or self.marker_ == None:
            return False
        elif self.type_ == 'prefix' and text.startswith(self.marker_):
            return True
        elif self.type_ == 'full' and text == self.marker_:
            return True
        elif self.type_ == 'suffix' and text.endswith(self.marker_):
            return True
        else:
            return False

    def color_text(self, text):
        if colors_lib == True:
            return color(text, fg=self.color_, style=self.style_)
        else:
            return text
