from MoinMoin import user
from MoinMoin import log
from MoinMoin.auth import GivenAuth


logging = log.getLogger(__name__)


class SSLAuth(GivenAuth):

    def __init__(self):
        GivenAuth.__init__(self, env_var="HTTP_X_FORWARDED_USER")

    def transform_username(self, name):
        return name[4:]

    def request(self, request, user_obj, **kw):
        u = None
        _ = request.getText
        # always revalidate auth
        if user_obj and user_obj.auth_method == self.name:
            user_obj = None
        # something else authenticated before us
        if user_obj:
            logging.debug("already authenticated, doing nothing")
            return user_obj, True
 
        if self.user_name is not None:
            auth_username = self.user_name
        elif self.env_var is None:
            auth_username = request.remote_user
        else:
            auth_username = request.environ.get(self.env_var)
 
        logging.debug("auth_username = %r" % auth_username)
        if auth_username:
            auth_username = self.decode_username(auth_username)
            auth_username = self.transform_username(auth_username)
            logging.debug("auth_username (after decode/transform) = %r" % auth_username)

        uid = user._getUserIdByKey(request, 'aliasname', auth_username)
        if uid is not None:
                u = user.User(request, uid,
                          auth_method=self.name, auth_attribs=('name', 'password'))
 
        logging.debug("u: %r" % u)
        if u and self.autocreate:
            logging.debug("autocreating user")
            u.create_or_update()
        if u and u.valid:
            logging.debug("returning valid user %r" % u)
            return u, True # True to get other methods called, too
        else:
            logging.debug("returning %r" % user_obj)
            return user_obj, True
