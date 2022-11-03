import webapp2
import os
#import base64
#import calendar
import cloudstorage as gcs
#from datetime import date
from bs4 import *
from datetime import date
from datetime import datetime
from datetime import timedelta
import string
import time
import urllib
import base64
import zlib
import logging
#import urllib2
import hashlib
#import cgi
#import base64
import json
import sys

#from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import app_identity
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import images
from google.appengine.api import search
from gaesessions import get_current_session
from uuid import uuid4
#from google.appengine.api import files

from combined import *

app_identity.get_default_gcs_bucket_name = get_default_gcs_bucket_name
