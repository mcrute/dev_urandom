import requests
from xmlrpc.client import Transport
from requests.models import Response
from requests.compat import urlparse
from requests.structures import CaseInsensitiveDict
from requests.utils import get_encoding_from_headers
from M2Crypto import Engine, SSL, m2, httpslib


class Adapter(requests.adapters.BaseAdapter):

    _pkcs11 = None

    def __init__(self, pin='', key_name="id_01"):
        super(Adapter, self).__init__()

        engine_path = "/usr/lib/ssl/engines/engine_pkcs11.so"
        module_path = "/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so"

        self._load_pkcs11(engine_path, module_path)

        self.cert = self._load_cert(key_name)
        self.key = self._load_key(key_name, pin)

    @classmethod
    def _load_pkcs11(cls, engine_path, module_path):
        if cls._pkcs11 is None:
            cls._pkcs11 = Engine.load_dynamic_engine("pkcs11", engine_path)
            cls._pkcs11.ctrl_cmd_string('MODULE_PATH', module_path)
            cls._pkcs11.set_default(m2.ENGINE_METHOD_RSA)

    @classmethod
    def _load_cert(cls, key_name):#key_name):
        return cls._pkcs11.load_certificate(key_name)

    @classmethod
    def _load_key(cls, key_name, pin):
        return cls._pkcs11.load_private_key(key_name, pin=pin)

    def _make_context(self):
        # Use False to prevent setting the crypto list which causes an NPE
        ctx = SSL.Context('sslv23', False)

        # Manually load the key and cert into the context because the helper
        # doesn't read from the smart card or handle DER-encoded certs
        m2.ssl_ctx_use_pkey_privkey(ctx.ctx, self.key._ptr())
        m2.ssl_ctx_use_x509(ctx.ctx, self.cert.x509)

        return ctx

    def send(self, request, **kwargs):
        url = urlparse(request.url)
        if url.scheme != 'https':
            raise Exception('Only HTTPS is supported!')

        ctx = self._make_context()

        conn = httpslib.HTTPSConnection(
                url.hostname, url.port or 443, ssl_context=ctx)
        conn.request(request.method, url.path, request.body, request.headers)

        resp = conn.getresponse()
        response = Response()

        # Fallback to None if there's no status_code, for whatever reason.
        response.status_code = getattr(resp, 'status', None)

        # Make headers case-insensitive.
        response.headers = CaseInsensitiveDict(getattr(resp, 'headers', {}))

        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason

        if isinstance(request.url, bytes):
            response.url = request.url.decode('utf-8')
        else:
            response.url = request.url

        # Give the Response some context.
        response.request = request
        response.connection = self

        return response

    def close(self):
        pass


# Unfinished xmlrpc transport that supports pkcs11
class PKCS11Transport(Transport):

    _pkcs11 = None

    @classmethod
    def get_engine(cls):
        if cls._pkcs11 is not None:
            return

        engine_path = "/usr/lib/ssl/engines/engine_pkcs11.so"
        module_path = "/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so"

        #engine_path = "/usr/local/Cellar/engine_pkcs11/0.1.8/lib/engines/engine_pkcs11.so"
        #module_path = "/Library/OpenSC/lib/opensc-pkcs11.so"

        cls._pkcs11 = Engine.load_dynamic_engine("pkcs11", engine_path)
        cls._pkcs11.ctrl_cmd_string('MODULE_PATH', module_path)
        cls._pkcs11.set_default(m2.ENGINE_METHOD_RSA)

    def __init__(self, use_datetime=0, pin='', key_name="01:01"):
        Transport.__init__(self, use_datetime=use_datetime)

        self.get_engine()
        cls = PKCS11Transport

        import getpass
        pin = getpass.getpass()

        self.cert = cls._pkcs11.load_certificate(key_name)
        self.key = cls._pkcs11.load_private_key(key_name, pin=pin)

        # Use False to prevent setting the crypto list which causes an NPE
        self.context = SSL.Context('tlsv1', False)

        # Manually load the key and cert into the context because the helper
        # doesn't read from the smart card or handle DER-encoded certs
        m2.ssl_ctx_use_pkey_privkey(self.context.ctx, self.key._ptr())
        m2.ssl_ctx_use_x509(self.context.ctx, self.cert._ptr())

        self.context.load_verify_locations("ca.pem", "")
        self.context.set_verify(SSL.verify_peer, 10)
        self.context.set_info_callback()

    def make_connection(self, host):
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        try:
            HTTPS = httpslib.HTTPSConnection
        except AttributeError:
            raise NotImplementedError(
                "your version of httplib doesn't support HTTPS")
        else:
            chost, self._extra_headers, x509 = self.get_host_info(host)
            self._connection = host, HTTPS(
                    chost, None, ssl_context=self.context)

            self._connection[1].request("GET", "/")
            kk = self._connection[1].getresponse()
            mm = kk.read()
            print mm

            import pdb; pdb.set_trace()
            return self._connection[1]
 
#        self.wiki = ServerProxy("{0}?action=xmlrpc2".format(host), transport=PKCS11Transport())
