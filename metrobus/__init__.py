name = "metrobus"

import socket
import string
import time
import random
from random import randint, choice
from faker import Faker

from .metrobus import MetroStop

fake = Faker()

DOMAINS = [
  "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
  "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
  "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",
  "email.com", "fastmail.fm", "games.com" 
  , "gmx.net", "hush.com", "hushmail.com", "icloud.com",
  "iname.com", "inbox.com", "lavabit.com", "love.com" 
  "outlook.com", "pobox.com", "protonmail.com",
  "rocketmail.com" , "safe-mail.net", "wow.com" , "ygm.com"
  "ymail.com" 
  , "zoho.com", "yandex.com",
  "bellsouth.net", "charter.net", "cox.net", "earthlink.net", "juno.com",
  "btinternet.com", "virginmedia.com", "blueyonder.co.uk", "freeserve.co.uk", "live.co.uk",
  "ntlworld.com", "o2.co.uk", "orange.net", "sky.com", "talktalk.co.uk", "tiscali.co.uk",
  "virgin.net", "wanadoo.co.uk", "bt.com",
  "sina.com", "sina.cn", "qq.com", "naver.com", "hanmail.net", "daum.net", 
  "nate.com", "yahoo.co.jp", "yahoo.co.kr", "yahoo.co.id", "yahoo.co.in", 
  "yahoo.com.sg", "yahoo.com.ph", "163.com", "126.com", "aliyun.com", "foxmail.com",
  "hotmail.fr", "live.fr", "laposte.net", "yahoo.fr", "wanadoo.fr", "orange.fr", "gmx.fr", "sfr.fr", "neuf.fr", "free.fr",
  "gmx.de", "hotmail.de", "live.de", "online.de", "t-online.de" 
  "web.de", "yahoo.de",
  "libero.it", "virgilio.it", "hotmail.it", "aol.it", "tiscali.it", "alice.it", "live.it", "yahoo.it", "email.it", "tin.it", "poste.it", "teletu.it",
  "mail.ru", "rambler.ru", "yandex.ru", "ya.ru", "list.ru",
  "hotmail.be", "live.be", "skynet.be", "voo.be", "tvcablenet.be", "telenet.be",
  "hotmail.com.ar", "live.com.ar", "yahoo.com.ar", "fibertel.com.ar", "speedy.com.ar", "arnet.com.ar",
  "yahoo.com.mx", "live.com.mx", "hotmail.es", "hotmail.com.mx", "prodigy.net.mx",
  "yahoo.com.br", "hotmail.com.br", "outlook.com.br", "uol.com.br", "bol.com.br", "terra.com.br", "ig.com.br", "itelefonica.com.br", "r7.com", "zipmail.com.br", "globo.com", "globomail.com", "oi.com.br"
]

def email_generator():
  return fake.email()
  role = fake.name().replace(' ', '_')
  domain = choice(DOMAINS)
  return f'{role}@{domain}'

def wait_open(ip,port, timeout=120, sleep_time=5):
   start = time.time()
   while time.time() < (start + 120):
       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       try:
          s.connect((ip, int(port)))
          s.shutdown(2)
          return True
       except:
          time.sleep(sleep_time)
    


if __name__ == '__main__':
  for _ in range(100):
      print(email_generator())

