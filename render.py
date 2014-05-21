#!/usr/bin/env python
#coding: utf8

from etc import config
from threading import Lock

_default_encoding = lambda: 'utf-8'

def to_unicode(data, encoding="GB18030"):
    """convert data from some encoding to unicode
    data could be string, list, tuple or dict
    that contains string as key or value
    """
    if data is None:
        return unicode('')
    if isinstance(data, unicode):
        return data

    if isinstance(data, (list, tuple)):
        u_data = []
        for item in data:
            u_data.append(to_unicode(item, encoding))

    elif isinstance(data, dict):
        u_data = {}
        for key in data:
            u_data[to_unicode(key, encoding)] = to_unicode(data[key], encoding)

    elif isinstance(data, str):
        u_data = unicode(data, encoding, 'ignore')

    else:
        u_data = data

    return u_data


class TempateEngineException(Exception): pass

class Jinja2Engine(object):
    def __init__(self, **kwargs):
        if not kwargs.get('template_root'):
            raise TemplateEngineException('must config template_root')

        import jinja2
        self._jinja2 = jinja2
        self._template_encoding = kwargs.get('template_encoding', _default_encoding())
        self._data_encoding = kwargs.get('data_encoding', _default_encoding())
        self._output_encoding = kwargs.get('output_encoding', None)

        env_init_args = {
            'loader': self._jinja2.FileSystemLoader(kwargs['template_root'], self._template_encoding),
        }
        env_init_args.update(kwargs.get('env_init', {}))
        self._env = self._jinja2.Environment(**env_init_args)
        
    def _load_template(self, template=None, from_string=None):
        if from_string:
            return self._env.from_string(template)
        return self._env.get_template(template)

    def render(self, template, data={}, **kwargs):
        udata = {}
        for k, v in data.iteritems():
            udata[to_unicode(k)] = to_unicode(v)
        o_template = self._load_template(template, kwargs.get('from_string', False))
        output = o_template.render(udata)
        if self._output_encoding:
            return output.encode(self._output_encoding, 'ignore')
        return output

jinja2_engine = None

def get_render_instance():
    global jinja2_engine 
    if not jinja2_engine:
        with Lock():
            jinja2_engine = Jinja2Engine(**config.templ_config)

    return jinja2_engine 

def render(template, data={}, **kwargs):
    return get_render_instance().render(template, data=data, **kwargs)
