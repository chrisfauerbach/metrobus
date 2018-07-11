from __future__ import print_function
from  metrobus import email_generator
import random
from random import randint
import sys

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


x = 1000000
counter = 0 
while x < 1999999:
  eml = email_generator()
  counter += 1
  print(f"{x},{eml}")
  if counter % 1000 == 0:
      eprint(f"Up to {counter}")
  x += randint(1,5)

