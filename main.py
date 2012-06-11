
import os
from webapp2 import WSGIApplication, Route

#Jinja2 template directory
root_dir = os.path.dirname(__file__)
template_dir = os.path.join(root_dir, 'templates')

#Cookie hashing secret.
SECRET = '''Bg0xqIhKPlUA99WZ3$z!8,/UNq}vLYY^o5L>ExWJ#n4n}j,rXN6GMyF<K:jm<Eo_Mc\
            Oyy(WV^kPZjV&Q7>!Iy#5B;G>TN[^BPpmKAD),rE1(Gx.62SCg<k5PpiPg/'''

#Check if running on dev server.
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')


PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = WSGIApplication([
    Route('/signup',
        handler='handlers.wiki.Signup',
        name='signup'),
    Route('/login',
        handler='handlers.wiki.Login',
        name='login'),
    Route('/logout',
        handler='handlers.wiki.Logout',
        name='logout'),
    Route('/_index',
        handler='handlers.wiki.Index',
        name='Index'),
    Route('/_search',
        handler='handlers.wiki.Search',
        name='Search'),
    Route('/_recent',
        handler='handlers.wiki.RecentRevisions',
        name='_recent'),
    Route('/_edit<page_name:' + PAGE_RE + '>',
        handler='handlers.wiki.EditPage',
        name='_edit'),
    Route('/_history<page_name:' + PAGE_RE + '>',
        handler='handlers.wiki.HistoryPage',
        name='_history'),
    Route('<page_name:' + PAGE_RE + '>',
        handler='handlers.wiki.WikiPage',
        name='WikiPage'),
    ],
    debug=debug)
