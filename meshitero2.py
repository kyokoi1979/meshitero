#!/usr/bin/env python
__author__ = 'kyokoi'

import requests
import xml.dom.minidom as md
from twitter import *

import random
import os.path
import datetime
import configparser

class Flickr(object):
    def __init__(self, api_key):
        self.api_url = 'https://api.flickr.com/services/rest/'
        self.api_key = api_key

    def get_photoset_ids_from_user_id(self, user_id):
        u"""
        ユーザー(user_id)が所有するアルバムidの一覧(photset_idのリスト)を返す
        今回の目的には必要ない
        """
        # requestの送信
        r = requests.post(self.api_url, {'api_key': self.api_key,
                                         'method': 'flickr.photosets.getList',
                                         'user_id': user_id
                                         })

        # xmlをパースしてdomオブジェクトにする
        dom = md.parseString(r.text.encode('utf-8'))

        # domオブジェクトからphotoset_idを探し出す
        result = []
        for elem in dom.getElementsByTagName('photoset'):
            result.append(elem.getAttribute('id'))
        return result

    def get_photos_from_photoset_id(self, photoset_id):
        u"""
        アルバムid(photset_id)内の写真一覧(photo_idのリスト)を返す
        """
        # requestの送信
        r = requests.post(self.api_url, {'api_key': self.api_key,
                                         'method': 'flickr.photosets.getPhotos',
                                         'photoset_id': photoset_id
                                         })
        # xmlをパースしてdomオブジェクトにする
        dom = md.parseString(r.text.encode('utf-8'))

        # domオブジェクトからphoto_idを探し出す
        global title
        title  = []
        result = []
        for elem in dom.getElementsByTagName('photo'):
            title.append(elem.getAttribute('title'))
            result.append(elem.getAttribute('id'))
        return result

    def get_url_from_photo_id(self, photo_id):
        u"""
        写真(photo_id)が実際に格納されているURLを返す
        """
        # requestの送信
        r = requests.post(self.api_url, {'api_key': self.api_key,
                                         'method': 'flickr.photos.getSizes',
                                         'photo_id': photo_id
                                         })
        # xmlをパースしてdomオブジェクトにする
        dom = md.parseString(r.text.encode('utf-8'))
        # domオブジェクトからURLを探し出す
        result = None
        for elem in dom.getElementsByTagName('size'):
            # オリジナルのサイズのもののみにする
            if elem.getAttribute('label') == 'Original':
                result = elem.getAttribute('source')
                # オリジナルは1個だと考えて他はスキップ
                break
            else:
                # 何もない場合はNone
                pass
        return result

if __name__ == '__main__':
    os.chdir( os.path.abspath(os.path.dirname(__file__)) )
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 動作確認
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    starttime = datetime.datetime.today()
    print("Start: ",starttime)

    # config読み込み
    imgdir = "./images"
    API_KEY     = config['Flickr']['API_KEY']
    PHOTOSET_ID = config['Flickr']['PHOTOSET_ID']

    CONSUMER_KEY    = config['Twitter']['CONSUMER_KEY'] 
    CONSUMER_SECRET = config['Twitter']['CONSUMER_SECRET'] 
    OAUTH_TOKEN     = config['Twitter']['OAUTH_TOKEN']
    OAUTH_SECRET    = config['Twitter']['OAUTH_SECRET']

    f      = Flickr(API_KEY)

    d      = f.get_photos_from_photoset_id(PHOTOSET_ID)
    get_id = random.randint(1,len(d))

    image  = d[get_id]
    comment= title[get_id]

    url    = f.get_url_from_photo_id(image)

    if not os.path.exists(imgdir):
        os.mkdir(imgdir)

    r = requests.get(url)

    with open("{0}/{1}".format(imgdir, url.split("/")[-1]), 'wb') as g:
        g.write(r.content)

    t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

    image = g.name

    status = comment
    with open(image, "rb") as imagefile:
        params = {"media[]": imagefile.read(), "status": status}

    t.statuses.update_with_media(**params)

    endtime = datetime.datetime.today()

    print("End: ", endtime)
    print("Duration: ", endtime - starttime)
    print("URL: ", url)
    print("Comment: ", comment, file = utf8stdout)
