from handlers.base import WikiHandler
from models import Page, User, Revision


def current_revision(page_name):
    page = Page.by_name(page_name)
    if page: return Revision.all().ancestor(page).get()
    else: return None

class WikiPage(WikiHandler):
    '''Handles regular page requests.'''
    def get(self, page_name):
        revision = current_revision(page_name)
        if revision:
            self.render('page.html', title=page_name,
                        revision=revision,
                        user=self.user)
        else:
            self.redirect_to('_edit', page_name=page_name)

class EditPage(WikiHandler):    
    '''Handles /_edit requests.'''
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
        revision = Revision(body=body, user=self.user, parent=page)
        revision.put()
        page.revision = revision
        page.put()
        self.redirect(page_name)

class HistoryPage(WikiHandler):
    '''Handles /_history requests.'''
    def get(self, page_name):
        page = Page.by_name(page_name)
        revisions = Revision.all().ancestor(page)
        self.render('history.html',
                    title=page_name,
                    revisions=revisions)

class Signup(WikiHandler):
    '''Handles /signup requests.'''
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
    '''Handles /login requests.'''
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
    '''Handles /logout requests.'''
    def get(self):
        self.logout()
        self.redirect('/')