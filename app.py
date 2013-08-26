from flask import Flask, send_file, request
from flask.ext import restful
from functools import wraps
from mimetypes import types_map
from uuid import uuid1

app = Flask(__name__)
api = restful.Api(app)

@api.representation('image/jpeg')
def image(data, code, headers):
    return send_file(open('{}{}.jpg'.format(app.config['PHOTO_STORE'],
                                            data['id'])))

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

class Photo(restful.Resource):
    
    def get(self, photo_id, ext):
        return {'self': '/photo/{}/'.format(photo_id),
                'id': photo_id}

    def post(self):
        filename = uuid1()
        fh = open('{}{}.jpg'.format(app.config['PHOTO_STORE'],
                                    filename))
        fh.write(request.bytes())
        fh.close()


    def put(self):
        pass

    def delete(self):
        pass

#api.add_resource(Photo, '/photo/<int:photo_id>/')
api.add_resource(Photo, '/photo/<int:photo_id>/.<ext>')
api.mediatypes = override_mediatypes(api.mediatypes)

if __name__ == '__main__':
    app.config['PHOTO_STORE'] = 'photo/'
    app.run(debug=True)
