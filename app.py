from flask import Flask, send_file, request
from flask.ext import restful
from functools import wraps

app = Flask(__name__)
api = restful.Api(app)

@api.representation('image/jpg')
def image(data, code, headers):
    return send_file(open(data['self'][1:-1] + '.jpg'))

EXTENSION_MAPPING = {'.jpg': 'image/jpg'}

def override_mediatypes(f):
    """Specifically overrides the mediatypes requested from the browser's
    Accept: header, if the URL includes one.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        extension = request.path.split('/')[-1]
        if extension in EXTENSION_MAPPING:
            return [EXTENSION_MAPPING[extension]]
        return f(*args, **kwargs)
    return wrapper

class Photo(restful.Resource):
    
    def get(self, photo_id, ext):
        return {'self': '/photo/{}/'.format(photo_id)}

#api.add_resource(Photo, '/photo/<int:photo_id>/')
api.add_resource(Photo, '/photo/<int:photo_id>/.<ext>')
api.mediatypes = override_mediatypes(api.mediatypes)

if __name__ == '__main__':
    app.run(debug=True)
