

#### objective is to once the files have been downloaded locally and copied into
#### specified dir, this server gets passed the handle to that dir path and deals with the emailing / mogrifying / gifing /gifmov






# ### return done  (Possibly a gif?)
        #MAKE This NOT ASYNC!

        #### use from sh import convert
        #### use from sh import mogrify
        mogrify = subprocess.check_output('mogrify -resize 1280x960 *.JPG', cwd=newSessionDirName, shell=True)
        time.sleep(10)
        gifme = subprocess.check_output('convert -delay 100 -loop 0 *.JPG mygif.gif', cwd=newSessionDirName, shell=True)
        time.sleep(10)


        giffile = os.path.join(newSessionDirName, 'mygif.gif')
        gifmovfile = os.path.join(newSessionDirName, 'mygif.mp4')

        # clip = mp.VideoFileClip(giffile)
        # clip.write_videofile(gifmovfile, codec='mpeg4')

        sending_email = EmailMixin()
        toaddrs = [emailaddress]
        fromaddr = 'kika.nina.wedding@gmail.com'
        subject = 'Kika and Nina Wedding Photo Booth July 1st 2017'
        bodytext = None
        html = "<html><body><h3>KIKA and NINA Wedding July 1st 2017</h3></body></html>"
        attachmentFilePaths = [__file__]
        the_file_22 = giffile

        self.write(json.dumps("Email Sent!"))
        sending_email._email_(subject, bodytext, [the_file_22], fromaddr, toaddrs, html=html)
