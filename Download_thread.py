from queue import Queue
import threading
from urllib.parse import urljoin
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import time
import urllib3
import os
import re
from PIL import Image
import config
import random

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

#多线程下载图片，在spider_thread.py中使用到
class ThreadWrite(threading.Thread):
    def __init__(self, threadName, imageQueue):
        super(ThreadWrite, self).__init__()
        self.threadName = threadName
        self.imageQueue = imageQueue
        self.THREAD_EXIT = False

    def run(self):
        print(self.threadName + ' begin.')
        while not self.THREAD_EXIT or not self.imageQueue.empty():
            try:
                if self.imageQueue.empty():
                    time.sleep(0.1)
                    continue
                img_name, img_link = self.imageQueue.get(block=False)
                self.writeImage(img_name, img_link)
            except Exception as e:
                print('some error.')
                pass
            # time.sleep(0.3)
            time.sleep(random.uniform(0, 1))
        print(self.threadName + ' finish.')

    def getSaveFileName(self, saved_files, filename, idx=1):
        names = filename.split('.')
        filename_gif = names[0] +'_'+str(idx)+'.'+ '.gif'  # 从img_name中解析   [隶书]->人,徐伯清.gif
        filename_png = names[0] +'_'+str(idx)+'.'+ '.png'
        if filename_gif not in saved_files and filename_png not in saved_files:   # 减少重复下载图片的开销
            return filename_gif
        else:
            idx += 1
            return self.getSaveFileName(saved_files, filename, idx)

    #将gif图片转成PNG图片
    def gif2png(self, filepath):
        im = Image.open(filepath)
        def iter_frames(im):
            try:
                i= 0
                while 1:
                    im.seek(i)
                    imframe = im.copy()
                    if i == 0:
                        palette = imframe.getpalette()
                    else:
                        imframe.putpalette(palette)
                    yield imframe
                    i += 1
            except EOFError:
                pass
        for i, frame in enumerate(iter_frames(im)):
            filepath2 = filepath.replace('.gif', '.png')
            frame.save(filepath2, **frame.info)

    def writeImage(self, img_name, img_link):
        # 华山神庙碑 - 隶书 - “人”
        names = [name.strip().replace("“", "").replace("”", "") for name in img_name.split('-')]
        # 华山神庙碑 隶书 人
        save_dir = os.path.join(config.save_path, names[1], names[2])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        filename = names[0] + '_'+str(round(random.random(),3)) + '.gif'   # 从img_name中解析   [隶书]->人,徐伯清.gif
        # filename_png = names[0] + '.png'
        # saved_files = os.listdir(save_dir)
        # if filename in saved_files or filename_png in saved_files:
        #     filename = self.getSaveFileName(saved_files, filename)

        try:
            r = requests.get(img_link, stream=False, headers=headers, verify=False)
        except requests.exceptions.RequestException as e:
            print(e)
            print('img requests error')
            return

        try:
            if len(r.content) / 1024 < config.img_size_threld:
                return
            with open(os.path.join(save_dir, filename), 'wb') as f:
                #print('response size: ', len(r.content)/1024, 'KB')
                f.write(r.content)
            self.gif2png(os.path.join(save_dir, filename))
            os.remove(os.path.join(save_dir, filename))

        except Exception as e:
            print(repr(e))
            print('img save error:', os.path.join(save_dir, filename))
            return
