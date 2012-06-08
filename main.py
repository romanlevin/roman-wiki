
import os
from webapp2 import WSGIApplication, Route
import handlers

#Jinja2 template directory
root_dir = os.path.dirname(__file__)
template_dir = os.path.join(root_dir, 'templates')

#Cookie hashing secret.
SECRET = ''''fajs;lk4j50fa432ja;'v'd//bv'casdf.'z-3k123$%&SAtR#$ASCfds'''


PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = WSGIApplication([Route('/signup', handler='handlers.wiki.Signup', name='signup'),
                       Route('/login', handler='handlers.wiki.Login', name='login'),
                       Route('/logout', handler='handlers.wiki.Logout', name= 'logout'),
                       Route('/_edit<page_name:' + PAGE_RE + '>', handler = 'handlers.wiki.EditPage', name='_edit'),
                       Route('/_history<page_name:' + PAGE_RE + '>', handler = 'handlers.wiki.HistoryPage', name='_history'),
                       Route('<page_name:' + PAGE_RE + '>', handler='handlers.wiki.WikiPage', name='WikiPage'),
                       ],
                      debug=True)
