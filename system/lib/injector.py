# -*- coding: utf8
__author__ = 'nolka'


class Injector(object):
    """
    Класс предназначен для внедрения свойств и методов в другие классы с настройкой через конфиг
    Функции-конструктору, которые конструируют свойства или методы не должны самостоятельно внедрять свои данные в объект,
    который передается в каждую из этих функций, вместо этого они должны возвращать готовые свойства или методы обратно
    в инжектор либо в виде простого значения, либо в виде словаря вида {'attr_name': 'attr_value'}.
    Можно использовать классы-конструкторы, для этого в них должен быть реализован метод __call__. И да, это еще не оттестировано
    """
    def inject(self, obj, prop, value_callback, callback_data={}):
        result = value_callback(obj, **callback_data)
        if isinstance(result, dict):
            for attr, prop in result.iteritems():
                setattr(obj, attr, prop)
        else:
            setattr(obj, prop, result)
        return obj

    def inject_attrs(self, obj, attrs, overriden_params={}):
        for name, callback_data in attrs.iteritems():
            callback_args = {}
            if isinstance(callback_data, tuple) or isinstance(callback_data, list):
                callback = callback_data[0]
                if len(callback_data) > 1:
                    callback_args = callback_data[1]
            else:
                callback = callback_data

            if overriden_params:
                callback_args.update(overriden_params)
            obj = self.inject(obj, name, callback, callback_args)
        return obj

injector = Injector()