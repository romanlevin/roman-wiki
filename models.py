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