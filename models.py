from google.appengine.ext import db


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
        return cls.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        user = cls.all().filter('username = ', name).get()
        return user

    @classmethod
    def register(cls, username, password, email=None):
        return cls(username=username,
                    password=password,
                    email=email)

    @classmethod
    def login(cls, name, password):
        user = cls.by_name(name)
        if user and user.password == password:
            return user


class Revision(db.Model):
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

    @classmethod
    def by_page_name(cls, page_name):
        '''Returns all revisions for Page page_name'''
        page = Page.by_name(page_name)
        if not page:
            return None
        return cls.all().ancestor(page)

    @classmethod
    def by_id(cls, id, page):
        '''Returns revision of id for Page page'''
        id = int(id)  # in case a string was passed.
        if isinstance(page, str):  # if passed a page name, rather than page.
            page = Page.by_name(page)
        return cls.get_by_id(id, page)


class Page(db.Model):
    '''
    The Page class.
    title - the name of the page and its url.
    current_edit - a reference to the current revision.
    '''
    title = db.StringProperty(required=True)
    revision = db.ReferenceProperty(Revision)

    @classmethod
    def by_name(cls, name):
        page = cls.all().filter('title = ', name).get()
        return page
