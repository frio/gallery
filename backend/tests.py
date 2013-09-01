"""
Acceptance tests
================
Ensure the ReST API is working.
"""

import gallery
import unittest
import json
import os
import tempfile
import shutil

class GalleryTests(unittest.TestCase):

    def setUp(self):
        gallery.app.config['PHOTO_STORE'] = tempfile.mkdtemp()
        gallery.app.debug = True
        self.app = gallery.app.test_client()

    def tearDown(self):
        shutil.rmtree(gallery.app.config['PHOTO_STORE'])

    def test_can_generate_unused_uuids(self):
        """
        This is a bit of a dumb test, but I kept getting 500s for some
        bad code I wrote inside the actual function.  So here's something
        which will exercise it.
        """
        name, path = gallery.safe_jpeg()
        self.assertEquals(path, os.path.join(gallery.app.config['PHOTO_STORE'],
                                             '{}.jpg'.format(name)))


    def test_we_can_post(self):
        with open('test/resources/cat.jpg') as image:
            resp = self.app.post('/photo/', data={'cat.jpg': image})
            self.assertEqual(resp.status_code, 201)
            self.assertIn('Location', resp.headers.keys())
            print resp.headers['Location'] # TODO move to after the id check, ensure Location includes id
            contents = json.loads(resp.data)
            self.assertIn('id', contents.keys())


class AcceptanceTest(unittest.TestCase):
    """
    Attempts to exercise the app fully: POSTs a photo, checks that it is listed
    in the full list of photos, and that when retrieved individually, the server
    returns it.
    """

    def setUp(self):
        gallery.app.config['PHOTO_STORE'] = tempfile.mkdtemp()
        gallery.app.debug = True
        self.app = gallery.app.test_client()

    def tearDown(self):
        shutil.rmtree(gallery.app.config['PHOTO_STORE'])
    
    def test_full_stack(self):
        with open('test/resources/cat.jpg') as image:
            self.app.post('/photo/', data={'cat.jpg': image})
        with open('test/resources/cat.jpg') as image:
            self.app.post('/photo/', data={'cat.jpg': image})

        # Assume from earlier cases that the responses are valid
        # We don't explicitly test them here.

        list_response = self.app.get('/photo/')
        self.assertEquals(list_response.status_code, 200)

        pictures = json.loads(list_response.data)
        self.assertEquals(len(pictures), 2)

        wanted_id = pictures[0]['id']
        image_response = self.app.get('/photo/{}/'.format(wanted_id))
        self.assertEquals(image_response.status_code, 200)
        self.assertEquals(image_response.content_type, 'application/json')

        image_metadata = json.loads(image_response.data)
        self.assertEquals(image_metadata, pictures[0])

        # And finally...
        binary_response = self.app.get('/photo/{}/.jpg'.format(wanted_id))
        self.assertEquals(binary_response.status_code, 200)
        self.assertTrue(binary_response.is_streamed)
        self.assertEquals(binary_response.content_type, 'image/jpeg')
        with open('test/resources/cat.jpg') as image:
            self.assertEquals(binary_response.data, image.read())


if __name__ == '__main__':
    unittest.main()
