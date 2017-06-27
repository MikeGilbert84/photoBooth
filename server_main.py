import tornado.ioloop
import tornado.web
import json
import os
import time
import subprocess
import random
from tornado import gen
# from sh import gphoto2 as gp


PATH = os.path.join(os.path.dirname(__file__), "static")
settings = {'debug': True,
            'static_path': PATH}




class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        print settings
        self.render("main.html")

class SnapHandler(tornado.web.RequestHandler):
    ### Receives the hash and the JSON object of the search
    ### checks the DB is the hash is in the column, if yes return cached data response
    ### else make the DB query and caches the response before sending back to frontend

    def get(self):

        searchstring = self.get_argument("search")

        print searchstring

       #### just a call to take a snap
        triggerCommand = ["--trigger-capture"]
        # gp(triggerCommand)

        time.sleep(5)

        self.write("snap:"+searchstring)
        self.finish()

class CleanUpHandler(tornado.web.RequestHandler):

    def get(self):

        pass
        ### make a datetime dir on the flash drive

        ### copy down the files off the camera
        ### delete the photos off the camera
        ### resize photos? generate gif?
        ### copy the files to the flash subdir
        ### return done  (Possibly a gif?)




def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/snap", SnapHandler)],
        **settings)




if __name__ == "__main__":



    app = make_app()
    port = int(os.environ.get("PORT", 4000))
    app.listen(port)

    tornado.ioloop.IOLoop.current().start()

