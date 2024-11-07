#!/usr/bin/env python3
import os
from gtts import gTTS
from datetime import datetime
import time
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
from pydub import AudioSegment

load_dotenv()

SERVER_ADDR = os.getenv('SERVER_ADDRESS')
SERVER_PORT = int(os.getenv('SERVER_PORT'))
PARENT_PATH = os.getenv('PARENT_PATH')
BIT_RATE = os.getenv('BIT_RATE_MP3')
PORTAL_APP = os.getenv('PORTAL_APP')

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        path = self.path
        print(f"Request path: {path}")
        if '/checkfile' in path:
            filename = path.replace('/checkfile/','')
            elemt = filename.split('-')
            datelm = elemt[0]
            channelid = elemt[1]
            detaildate = datelm.split('_')
            yearpath = detaildate[0]
            monthpath = detaildate[1]
            datepath = detaildate[2]
            try:
                paging = elemt[3]
            except IndexError:
                paging = 0

            if paging == 0:
                fullpathfile = PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath+'/'+datepath+'/'+channelid+'/'+elemt[2]
            else:
                fullpathfile = PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath+'/'+datepath+'/'+channelid+'/'+elemt[2]+'-'+paging

            if not os.path.exists(fullpathfile+".mp3"):
                self.send_response(404)
                outputweb = bytes("0", "utf8")
                self.wfile.write(outputweb)
            else:
                self.send_response(200)
                outputweb = bytes("1", "utf8")
                self.wfile.write(outputweb)

        else:
            self.send_response(404)
            outputweb = bytes('invalid path', "utf8")
            self.wfile.write(outputweb)


    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self._set_headers()
        path = self.path
        current_date_and_time = datetime.now()
        st = time.time()
        print("Start convert text to speech : ", current_date_and_time)
        post_data_str = post_data.decode('utf-8')
        clean_text_1 = remove_html_tags(post_data_str)
        cleanlower = clean_text_1.lower()
        clean_text_2 = cleanlower.replace('\\"','').replace('\"','').replace('\\n', '').replace('\\r', '').replace('&nbsp;',' ')
        text = clean_text_2

        self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        pathfile = path
        pathfiletmp = pathfile.replace("/","")
        pathfile2=createPath(pathfiletmp)
        bahasa = "id"
        file = gTTS(text = text, lang=bahasa)
        file.save(pathfile2+".mp3")

        # Load the MP3 file
        audio = AudioSegment.from_mp3(pathfile2+".mp3")

        # Set the export parameters (bitrate, codec, etc.)
        # Compress by lowering the bitrate
        audio.export(pathfile2+".mp3", format="mp3", bitrate=BIT_RATE)

        end_date_and_time = datetime.now()
        print("Finish convert text to speech : ", end_date_and_time)
        # get the end time
        et = time.time()

        # get the execution time
        elapsed_time = et - st
        # print(post_data)
        outputstring = "cleaned : <br>"+text+"</br> file output : "+pathfile2+".mp3</br> duration : "+str(elapsed_time)+" seconds"
        outputweb = bytes(outputstring, "utf8")
        self.wfile.write(outputweb)

def createPath(filename):
    elemt = filename.split('-')
    datelm = elemt[0]
    channelid = elemt[1]
    detaildate = datelm.split('_')
    yearpath = detaildate[0]
    monthpath = detaildate[1]
    datepath = detaildate[2]
    try:
        paging = elemt[3]
    except IndexError:
        paging = 0

    if not os.path.exists(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath):
       os.makedirs(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath)
    if not os.path.exists(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath):
       os.makedirs(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath)
    if not os.path.exists(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath+'/'+datepath):
       os.makedirs(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath+'/'+datepath)
    if not os.path.exists(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath+'/'+datepath+'/'+channelid):
       os.makedirs(PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath+'/'+datepath+'/'+channelid)

    fullpathfile = PARENT_PATH+'/'+PORTAL_APP+'/'+yearpath+'/'+monthpath+'/'+datepath+'/'+channelid

    if paging == 0:
       return fullpathfile+'/'+elemt[2]
    else:
       return fullpathfile+'/'+elemt[2]+'-'+paging

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def run(server_class=HTTPServer, handler_class=S, port=SERVER_PORT):
    server_address = (SERVER_ADDR, port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
