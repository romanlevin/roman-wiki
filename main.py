#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
import hmac
from datetime import datetime


from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates') #directory for Jinja2 templates.
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True,
                               extensions=['jinja2.ext.autoescape'])

SECRET = 'secret'
def make_secure_value(value, secret=SECRET):
    return '%s|%s' % (value, hmac.new(secret, value).hexdigest())

def check_if_secure(secure_value):
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
        cookie_value = make_secure_value(value)
        self.response.headers.add_header('Set-Cookie',
                                         '%s=%s; Path=/' % (name, cookie_value))
    def read_secure_cookie(self, name):
        cookie_value = self.request.cookies.get(name)
        return cookie_value and check_if_secure(cookie_value)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
    def initialize (self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

class User(db.Model):
    '''
    The user class.
    username and password_hash are required strings.
    email is optional.
    '''
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        user = User.all().filter('username = ', name).get()
        return user

    @classmethod
    def register(cls, username, password, email=None):
        return User(username=username,
                    password=password,
                    email=email)

    @classmethod
    def login(cls, name, password):
        user = cls.by_name(name)
        if user and user.password == password:
            return user

class Edit(db.Model):
    '''
    The revision class.
    date - a datetime of revision creation.
    body - the revision body.
    user - a reference to thecreator of the revision.
    page - a reference to the page this edit belongs to.
    '''
    date = db.DateTimeProperty(auto_now_add=True)
    body = db.TextProperty(required=True)
    user = db.ReferenceProperty(User, required=True)

class Page(db.Model):
    '''
    The Page class.
    title - the name of the page and its url.
    current_edit - a reference to the current revision.
    '''
    title = db.StringProperty(required=True)
    revision = db.ReferenceProperty(Edit)

    @classmethod
    def by_name(cls, name):
        page = cls.all().filter('title = ', name).get()
        return page

def current_revision(page_name):
    page = Page.by_name(page_name)
    if page: return Edit.all().ancestor(page).get()
    else: return None

class WikiPage(WikiHandler):
    def get(self, page_name):
        revision = current_revision(page_name)
        if revision:
            self.render('page.html', title=page_name,
                        revision=revision,
                        user=self.user)
        else:
            self.redirect('/_edit' + page_name)

class EditPage(WikiHandler):
    def get(self, page_name):
        page = Page.by_name(page_name)
        self.render('edit.html', page=page, user=self.user)
    def post(self, page_name):
        page = Page.by_name(page_name)
        if self.user:
            body = self.request.get('content')
        else:
            self.write('ERROR: not logged in.')
            self.abort()
        if not page:
            page = Page(title=page_name)
            page.put()
        revision = Edit(body=body, user=self.user, parent=page)
        revision.put()
        page.revision = revision
        page.put()
        self.redirect(page_name)

        

class HistoryPage(WikiHandler):
    def get(self, page_name):
        page = Page.by_name(page_name)
        revisions = Edit.all().ancestor(page)
        self.render('history.html',
                    title=page_name,
                    revisions=revisions)

class Signup(WikiHandler):
    def get(self):
        self.render("signup.html")
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        error = ""
        if not username:
            error += "We need a username! "
        if password and not password == verify:
            error += "We need a verified password! "
        if User.by_name(username):
            error = 'That user already exists.'
        if error:
            self.render("signup.html", username=username, email=email, error=error)
        else:
            user = User.register(username, password, email)
            user.put()
            self.login(user)
            self.redirect("/")

class Login(WikiHandler):
    def get(self):
        self.render('login.html')
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        user = User.login(username, password)
        if not user:
            error = 'Invalid login.'
            self.render('login.html', username=username,error=user)
        else:
            self.login(user)
            self.redirect('/')

class Logout(WikiHandler):
    def get(self):
        self.logout()
        self.redirect('/')



PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/_edit' + PAGE_RE, EditPage),
                               ('/_history' + PAGE_RE, HistoryPage),
                               (PAGE_RE, WikiPage),
                               ],
                              debug=True)
