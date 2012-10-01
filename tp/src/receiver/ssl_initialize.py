import os
import logging
import shutil

from OpenSSL import SSL, crypto
from tools.ssl import *

LOG_DIR = '/opt/TopPatch/var/log'
LOG_FILE = 'server_ssl.log'
TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA
SERVER_KEY_DIR = '/opt/TopPatch/var/lib/ssl/server/keys/'
CLIENT_KEY_DIR = '/opt/TopPatch/var/lib/ssl/client/keys/'
SERVER_PRIVKEY_NAME  = 'server.key'
SERVER_PUBKEY_NAME   = 'server.cert'
CLIENT_PRIVKEY_NAME  = 'client.key'
CLIENT_PUBKEY_NAME   = 'client.cert'
#CA_PRIVKEY_NAME  = 'CA.key'
#CA_PUBKEY_NAME   = 'CA.cert'
#TOPPATCH_CA = ('TopPatch Certficate Authority', 'TopPatch',
#               'Remediation Vault', 'US', 'NY', 'NYC')
TOPPATCH_SERVER = ('TopPatch Server', 'TopPatch',
                   'Remediation Vault', 'US', 'NY', 'NYC')
TOPPATCH_CLIENT = ('TopPatch Client', 'TopPatch',
                   'Remediation Vault', 'US', 'NY', 'NYC')
EXPIRATION = (0, 60*60*24*365*10)

SERVER_PRIVKEY = SERVER_KEY_DIR + SERVER_PRIVKEY_NAME
SERVER_PUBKEY = SERVER_KEY_DIR + SERVER_PUBKEY_NAME
CLIENT_PRIVKEY = CLIENT_KEY_DIR + CLIENT_PRIVKEY_NAME
CLIENT_PUBKEY = CLIENT_KEY_DIR + CLIENT_PUBKEY_NAME
#CA_PRIVKEY = SERVER_KEY_DIR + CA_PRIVKEY_NAME
#CA_PUBKEY = SERVER_KEY_DIR + CA_PUBKEY_NAME

if not os.path.exists(LOG_DIR):
    logging.warning('directory %s does not exist. Creating the %s directory now' % (LOG_DIR, LOG_DIR))
    shutil.os.makedirs(LOG_DIR, mode=0755)
    if os.path.exists(LOG_DIR):
        logging.warning('%s was created' % (LOG_DIR))
    else:
        logging.warning('Failed to create %s' % (LOG_DIR))

logger = logging.getLogger('SSL Initialization')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(LOG_DIR+'/'+LOG_FILE, mode='a', encoding=None, delay=False)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)
if not os.path.exists(SERVER_KEY_DIR):
    logger.info('directory %s does not exist. Creating the %s directory now' % (SERVER_KEY_DIR, SERVER_KEY_DIR))
    shutil.os.makedirs(SERVER_KEY_DIR, mode=0755)
    if os.path.exists(SERVER_KEY_DIR):
        logger.info('%s was created' % (SERVER_KEY_DIR))
    else:
        logger.info('Failed to create %s' % (SERVER_KEY_DIR))
    shutil.os.makedirs(CLIENT_KEY_DIR, mode=0755)
    if os.path.exists(CLIENT_KEY_DIR):
        logger.info('%s was created' % (CLIENT_KEY_DIR))
    else:
        logger.info('Failed to create %s' % (CLIENT_KEY_DIR))
file_exists = os.path.exists(SERVER_PRIVKEY)

keys_written = []
if not file_exists:
    logger.info('Creating Certificate Authority and Server Keys')
    #ca_pkey = generatePrivateKey(TYPE_RSA, 4098)
    #ca_cert = createSigningCertificateAuthority(ca_pkey, 1,
    #    TOPPATCH_CA, EXPIRATION
    #)
    server_pkey = generatePrivateKey(TYPE_RSA, 2048)
    server_cert = createSigningCertificateAuthority(server_pkey, 1,
        TOPPATCH_SERVER, EXPIRATION
    )
    client_pkey = generatePrivateKey(TYPE_RSA, 2048)
    client_csr = createCertRequest(client_pkey, TOPPATCH_CLIENT)
    client_cert = createSignedCertificate(client_csr, (server_cert, server_pkey), 1, EXPIRATION, digest="sha512")
    #keys_written.append(saveKey(SERVER_KEY_DIR, ca_pkey, '.key', name='CA'))
    #keys_written.append(saveKey(SERVER_KEY_DIR, ca_cert, '.cert', name='CA'))
    keys_written.append(saveKey(SERVER_KEY_DIR, server_pkey, TYPE_PKEY, name='server'))
    #keys_written.append(saveKey(SERVER_KEY_DIR, server_csr, '.csr', name='server'))
    keys_written.append(saveKey(SERVER_KEY_DIR, server_cert, TYPE_CERT, name='server'))
    keys_written.append(saveKey(CLIENT_KEY_DIR, client_pkey, TYPE_PKEY, name='client'))
    keys_written.append(saveKey(CLIENT_KEY_DIR, client_csr, TYPE_CSR, name='client'))
    keys_written.append(saveKey(CLIENT_KEY_DIR, client_cert, TYPE_CERT, name='client'))

for certs in keys_written:
    logger.info('%s has been created' % (certs[0]))
logger.info('Server and CA certs have been generated')
