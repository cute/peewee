import peewee

def patch_save_only():
    raw_set = peewee.FieldDescriptor.__set__

    def __set__(self, instance, value):
        if hasattr(instance,'_raw_defaults')\
           and self.att_name not in instance._raw_defaults:
            instance._raw_defaults[self.att_name]= value
        instance._data[self.att_name] = value
        raw_set(self, instance, value)

    peewee.FieldDescriptor.__set__ = __set__

    raw_init = peewee.Model.__init__
    raw_save = peewee.Model.save

    def __init__(self, *args, **kwargs):
        raw_init(self, *args, **kwargs)
        self._raw_defaults = dict()

    peewee.Model.__init__ = __init__

    def save(self, force_insert=False, only=None):
        if not self.get_id():
            return raw_save(self, force_insert=force_insert, only=only)

        field_dict = dict(self._data)
        only = []
        for key, value in self._raw_defaults.items():
            if key in field_dict and value != field_dict[key]:
                only.append(getattr(self.__class__, key))

        if only:
            return raw_save(self, force_insert=force_insert, only=only)

    peewee.Model.save = save

