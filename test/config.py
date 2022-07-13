import sys
import os
import random
import string

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)))

from api import create_app,db
from api.config import TestConfig

app = create_app(TestConfig)
client = app.test_client()



