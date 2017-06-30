import tornado.ioloop
import tornado.web
import json
import os
import time
import datetime
import glob
import shutil
import subprocess
import random
from tornado import gen
import multiprocessing
from sh import gphoto2 as gp


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
        print "SNAP"
       #### just a call to take a snap
        triggerCommand = ["--trigger-capture"]
        gp(triggerCommand)



        self.write("snap:"+searchstring)
        self.finish()

class CleanUpHandler(tornado.web.RequestHandler):

    def get(self):

        print "console hit"
        # time.sleep(10)

        ### copy down the files off the camera
        getFilesCommand = ["--get-all-files"]
        gp(getFilesCommand)


        ### make a datetime dir on the flash drive
        newSessionDirName = os.path.join(r'/media/pi/HP v125w/kikanina', datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') )
        os.makedirs(newSessionDirName)
        newSessionPlayDirName = os.path.join(newSessionDirName, 'play')
        os.makedirs(newSessionPlayDirName)

        ### copy the files to the flash subdir
        cwd = r'/media/pi/HP v125w/kikanina'
        currentDir = os.getcwd()
        for snap in glob.iglob(os.path.join(currentDir, "*.JPG")):
            os.remove(snap)
        downloadCommand = ["--get-all-files"]
        # status = subprocess.Popen("gphoto2 --get-all-files", cwd=newSessionDirName,shell=True)
        time.sleep(2)
        gp(downloadCommand)
        ### copy them to the right Dir
        for snap in glob.iglob(os.path.join(currentDir, "*.JPG")):
            shutil.copy(snap, newSessionDirName)
            shutil.copy(snap, newSessionPlayDirName)
        ### delete the photos off the camera
        clearphotos = subprocess.check_output(r"gphoto2 --folder='/store_00020001/DCIM/100CANON' -R --delete-all-files", shell=True)
        # # clearCommand = ["--folder=","/store_00020001/DCIM/100CANON" "-R", "--delete-all-files"]
        # # gp(clearCommand)
        # ### return done  (Possibly a gif?)
        mogrify = subprocess.check_output('mogrify -resize 1280x960 *.JPG', cwd=newSessionPlayDirName, shell=True)
        gifme = subprocess.check_output('convert -delay 110 -loop 0 *.JPG mygif.gif', cwd=newSessionPlayDirName, shell=True)

        ### process gif on the side
        # def target(where):
        #     mogrify = subprocess.check_output('mogrify -resize 1280x960 *.JPG', cwd=where, shell=True)
        #     gifme = subprocess.check_output('convert -delay 110 -loop 0 *.JPG mygif.gif', cwd= where, shell=True)
        #
        # mygiffile = os.path.join(newSessionDirName,'mygif.txt')
        # p = multiprocessing.Process(target=target, args=(newSessionPlayDirName,))
        # p.start()
        # p.join()




        self.write("Done")
        self.finish()



def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/snap", SnapHandler),
        (r"/cleanup", CleanUpHandler)],
        **settings)




if __name__ == "__main__":

    ### define and run a function that kills the gphoto process IF it exists

    app = make_app()
    port = int(os.environ.get("PORT", 4000))
    app.listen(port)

    tornado.ioloop.IOLoop.current().start()

