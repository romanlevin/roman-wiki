from handlers.base import WikiHandler
from models import Page, User, Revision



class WikiPage(WikiHandler):
    '''Handles regular page requests.'''
    def get(self, page_name):
        revision_id = self.request.get('v')
        revision = None
        if revision_id:
            revision = Revision.by_id(revision_id, page_name)
        else:
            revisions = Revision.by_page_name(page_name)
            if revisions:
                revision = revisions.order('-date').get()
        if revision:
            self.render('page.jinja', page_name=page_name,
                        revision=revision,
                        user=self.user)
        else:
            self.redirect_to('_edit', page_name=page_name)


class EditPage(WikiHandler):
    '''Handles /_edit requests.'''
    def get(self, page_name):
        page = Page.by_name(page_name)
        revision = None
        revision_id = self.request.get('v')
        if revision_id:  # if a specific revision is requested
            revision = Revision.by_id(revision_id, page)
        self.render(
            'edit.jinja',
            page_name=page_name,
            revision=revision,
            user=self.user)

    def post(self, page_name):
        page = Page.by_name(page_name)
        if self.user:
            body = self.request.get('content')
        else:  # if posted while not logged in.
            self.write('ERROR: not logged in.')
            self.abort()
        if not page:  # For creatubg a new page.
            page = Page(title=page_name)
            page.put()
        revision = Revision(body=body, user=self.user, parent=page)
        revision.put()
        page.revision = revision
        page.put()
        self.redirect_to('WikiPage', page_name=page_name)


class HistoryPage(WikiHandler):
    '''Handles /_history requests.'''
    def get(self, page_name):
        revisions = Revision.by_page_name(page_name)
        if revisions:
            revisions = revisions.order('-date')
        self.render('history.jinja',
                    page_name=page_name,
                    revisions=revisions)


class Signup(WikiHandler):
    '''Handles /signup requests.'''
    def get(self):
        self.render("signup.jinja")

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
            self.render("signup.jinja",
                        username=username,
                        email=email,
                        error=error)
        else:
            user = User.register(username, password, email)
            user.put()
            self.login(user)
            self.redirect_to('WikiPage', page_name='/')


class Login(WikiHandler):
    '''Handles /login requests.'''
    def get(self):
        self.render('login.jinja')

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        user = User.login(username, password)
        if not user:
            error = 'Invalid login.'
            self.render('login.jinja', username=username, error=error)
        else:
            self.login(user)
            self.redirect_to('WikiPage', page_name='/')


class Logout(WikiHandler):
    '''Handles /logout requests.'''
    def get(self):
        self.logout()
        self.redirect_to('WikiPage', page_name='/')


class Search(WikiHandler):
    '''Handles searches from the search box'''
    def get(self):
        self.redirect_to('WikiPage', page_name='/')

    def post(self):
        page_name = '/' + str(self.request.get('page'))
        self.redirect_to('WikiPage', page_name=page_name)
