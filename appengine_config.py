from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

from gaesessions import SessionMiddleware

# Original comments deleted ...
# Create a random string for COOKIE_KDY and the string has to
# be permanent. "os.urandom(64)" function may be used but do
# not use it *dynamically*.
# For me, I just randomly generate a string of length 64
# and paste it here, such as the following:

###
#To force all sessions to drop after a deployment, toggle the COOKIE KEY to the one that is commented out.
##


#COOKIE_KEY = "9876Ab!.djfkdfjdlajsdfkljasdfjklasf@@!@    6IKJLXAdsaywlthe9lL*^"
COOKIE_KEY = "9876Ab!.djfkdfjdlajsdfkljasdfjklasf@@!@    6IKJLXAdsaywlthe9lL****^"

remoteapi_CUSTOM_ENVIRONMENT_AUTHENTICATION = ('HTTP_X_APPENGINE_INBOUND_APPID',['npfieldapp'])

def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
    app = recording.appstats_wsgi_middleware(app)
    return app
