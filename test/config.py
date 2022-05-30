import sys
import os
import random
import string
import pytest
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)))

from api import create_app
from api.config import TestConfig

app = create_app(TestConfig)
client = app.test_client()

    
random_email = ''.join(random.choice(string.ascii_letters) for x in range(7)) + "@gmail.com"



