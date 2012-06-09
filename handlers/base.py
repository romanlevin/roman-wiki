import jinja2
import webapp2
import hmac
from models import User

from main import template_dir, SECRET

#Sets jinja2 environment.
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True,
                               extensions=['jinja2.ext.autoescape'])


#TODO: Make use of security features in webapp2_extra.

def make_secure_value(value, secret=SECRET):
    '''Returns a secure hashed cookie value.'''
    return '%s|%s' % (value, hmac.new(secret, value).hexdigest())


def check_if_secure(secure_value):
    '''Check if cookie is securely hashed.'''
    value = secure_value.split('|')[0]
    if secure_value == make_secure_value(value):
        return value


class WikiHandler(webapp2.RequestHandler):
    '''Superclass for all page handlers in the wiki'''
    def write(self, *a, **kw):
        '''A shortcut for self.response.out.write()'''
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        '''jinja2 render through template with params'''
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        '''Write out a render through jinja2'''
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, value):
        '''Sets a hashed cookie'''
        cookie_value = make_secure_value(value)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_value))

    def read_secure_cookie(self, name):
        '''Reads a hashed cookie'''
        cookie_value = self.request.cookies.get(name)
        return cookie_value and check_if_secure(cookie_value)

    def login(self, user):
        '''Sets a login cookie for user.'''
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        '''Removes login cookie.'''
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        '''Initializes handler.
        If login cookie exists, set user attribute to hold a user object.'''
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def redirect_to(self, name, *args, **kwargs):
        """Redirect to a URI that corresponds to a route name."""
        self.redirect(self.uri_for(name, *args, **kwargs))
