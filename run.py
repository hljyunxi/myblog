#!/usr/bin/env python
#coding: utf8

import sys, os
import fnmatch
from datetime import datetime

from markdown import markdown
import tornado.ioloop
import tornado.web

from etc import config
from render import render

def format_post(item):
    bits = item.split('_', 1)

    date = datetime.strptime(bits[0], '%Y%m%d')
    title = bits[1].replace('_', ' ').replace('.md', '').title()
    slug = title.lower().replace(' ', '-')

    return {'date': date, 'title': title, 'slug': slug}


def get_post_dir():
    return os.path.dirname(os.path.abspath(__file__)) + '/templates/posts'

def get_post_items():
    items = os.listdir(get_post_dir())
    items.sort(reverse=True)
    return items


def get_posts():
    posts = []

    for item in get_post_items():
        if item[0] == '.' or item[0] == '_':
            continue

        post = format_post(item)
        posts.append(post)

    return posts


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        template = render('index.html', data={
            'posts': get_posts()
        })
        self.write(str(template))

class PostHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        assert kwargs['post_name']
        post_name = kwargs.get('post_name').encode(config.default_encoding)
        
        post = None
        for i in get_post_items():
            if fnmatch.fnmatch(i, '*_%s.md'%post_name):
                post = i
                break
        else:
            self.write('Not Found')
            return
        
        template = render('post.html', data={
            'content': markdown(open('templates/posts/%s'%post).read().decode(config.default_encoding))
        })
        self.write(template)


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/post/(?P<post_name>.*)", PostHandler),
    (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': 'static/js'}),
    (r'/img/(.*)', tornado.web.StaticFileHandler, {'path': 'static/img'}),
    (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'static/css'}),
])

if __name__ == '__main__':
    import daemon
    daemon.daemon('./tornado.pid')
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
