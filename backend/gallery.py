"""
gallery.py
==========
A simple photo gallery.  Made so that I can play with some CoffeeScript on the frontend.
"""

from flask import Flask, send_file, request
from flask.ext import restful
from functools import wraps
from mimetypes import types_map
from uuid import uuid1
import os

app = Flask(__name__)
api = restful.Api(app)

@api.representation('image/jpeg')
def image(data, code, **kwargs):
    # TODO there's a possible bug here in that I never do anything
    # with the code *or* the potential kwargs['headers']
    path = os.path.join(app.config['PHOTO_STORE'],
                        '{}.jpg'.format(data['id']))
    return send_file(path)

def override_mediatypes(f):
    """Specifically overrides the mediatypes requested from the browser's
    Accept: header, if the URL includes one.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        extension = request.path.split('/')[-1]
        if extension in types_map.keys():
            return [types_map[extension]]
        return f(*args, **kwargs)
    return wrapper


def safe_jpeg():
    """
    Generates a random filename.
    """
    unused = False
    while not unused:
        name = str(uuid1())
        path = os.path.join(app.config['PHOTO_STORE'],
                            '{}.jpg'.format(name))
        unused = not os.path.exists(path)

    return name, path



class Photo(restful.Resource):
    
    def get(self, photo_id, ext=None):
        return {'id': photo_id}


class PhotoCollection(restful.Resource):

    def get(self):
        return [{'id': os.path.splitext(path)[0]} for path in os.listdir(app.config['PHOTO_STORE'])]

    def post(self):
        for name, stream in request.files.iteritems():
            if stream.content_type == 'image/jpeg':
                name, path = safe_jpeg()
                stream.save(path)
        return {'id': name}, 201, {'Location': '/photo/{}/'.format(name)}


api.add_resource(PhotoCollection, '/photo/')
api.add_resource(Photo, '/photo/<string:photo_id>/',
                        '/photo/<string:photo_id>/.<string:ext>')
api.mediatypes = override_mediatypes(api.mediatypes)

if __name__ == '__main__':
    app.config['PHOTO_STORE'] = 'photo/'
    app.run(debug=True)
