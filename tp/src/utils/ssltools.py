import os
import socket
from OpenSSL import crypto

FILE_TYPE_PEM = crypto.FILETYPE_PEM
DUMP_PKEY = crypto.dump_privatekey
DUMP_CERT = crypto.dump_certificate
DUMP_CERT_REQUEST = crypto.dump_certificate_request
LOAD_PKEY = crypto.load_privatekey
LOAD_CERT = crypto.load_certificate
LOAD_CERT_REQUEST = crypto.load_certificate_request
CLIENT_CSR_DIR = '/opt/TopPatch/var/lib/ssl/client/csr'
CLIENT_KEY_DIR = '/opt/TopPatch/var/lib/ssl/client/keys'
SERVER_KEY_DIR = '/opt/TopPatch/var/lib/ssl/server/keys'
TYPE_CSR = 1
TYPE_CERT = 2
TYPE_PKEY = 3
EXTENSION = {
    1 : '.csr',
    2 : '.cert',
    3 : '.key'
}

def generatePrivateKey(type, bits):
    pkey = crypto.PKey()
    pkey.generate_key(type, bits)
    return pkey

def saveKey(location, key, key_type, name=socket.gethostname()):
    extension = EXTENSION[key_type]
    path_to_key = os.path.join(location, name + extension)
    status = False
    if type(key) == crypto.PKeyType:
        DUMP_KEY = DUMP_PKEY
    elif type(key) == crypto.X509Type:
        DUMP_KEY = DUMP_CERT
    elif type(key) == crypto.X509ReqType:
        DUMP_KEY = DUMP_CERT_REQUEST
    try:
        os.stat(location)
    except OSError as e:
        if e.errno == 2:
            print 'The directory %s does not exist' % (location)
        elif e.errno == 13:
            print 'Do not have sufficient permission to write to %s'\
            % (location)
    try:
        file_exists = os.stat(path_to_key)
        if file_exists:
            print 'File %s already exists' % (path_to_key)
            print ' not be overwritten'
    except OSError as e:
        if e.errno == 2:
            open(path_to_key, 'w').write(\
                DUMP_KEY(FILE_TYPE_PEM, key)
            )
            status = True
        elif e.errno == 13:
            print 'Do not have sufficient permission to write to %s'\
            % (location)
    return(path_to_key, status)

def createCertRequest(pkey, (CN, O, OU, C, ST, L), digest="sha512"):
    csr = crypto.X509Req()
    csr.set_version(3)
    subj = csr.get_subject()
    subj.CN=CN
    subj.O=O
    subj.OU=OU
    subj.C=C
    subj.ST=ST
    subj.L=L
    csr.set_pubkey(pkey)
    csr.sign(pkey, digest)
    return csr

def createSignedCertificate(csr, (issuerCert, issuerKey), serial,\
        (notBefore, notAfter), digest="sha512"):
    cert = crypto.X509()
    cert.set_version(3)
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(notBefore)
    cert.gmtime_adj_notAfter(notAfter)
    cert.set_issuer(issuerCert.get_subject())
    cert.set_subject(csr.get_subject())
    cert.set_pubkey(csr.get_pubkey())
    cert.sign(issuerKey, digest)
    return cert

def createCertificateAuthority(pkey, serial,\
        (CN, O, OU, C, ST, L),\
        (notBefore, notAfter), digest="sha512"):
    ca = crypto.X509()
    ca.set_version(3)
    subj = ca.get_subject()
    subj.CN=CN
    subj.O=O
    subj.OU=OU
    subj.C=C
    subj.ST=ST
    subj.L=L
    ca.set_serial_number(serial)
    ca.gmtime_adj_notBefore(notBefore)
    ca.gmtime_adj_notAfter(notAfter)
    ca.set_issuer(ca.get_subject())
    ca.set_pubkey(pkey)
    ca.sign(pkey, digest)
    return ca

def createSigningCertificateAuthority(pkey, serial,\
        (CN, O, OU, C, ST, L),
        (notBefore, notAfter),
                                      digest="sha512"):
    ca = crypto.X509()
    ca.set_version(3)
    subj = ca.get_subject()
    subj.CN=CN
    subj.O=O
    subj.OU=OU
    subj.C=C
    subj.ST=ST
    subj.L=L
    ca.set_serial_number(serial)
    ca.gmtime_adj_notBefore(notBefore)
    ca.gmtime_adj_notAfter(notAfter)
    ca.set_issuer(ca.get_subject())
    ca.set_pubkey(pkey)
    ca.add_extensions([
        crypto.X509Extension("basicConstraints", True,"CA:TRUE, pathlen:0"),
        crypto.X509Extension("keyUsage", True,"keyCertSign, cRLSign"),
        crypto.X509Extension("subjectKeyIdentifier", False, "hash",subject=ca),
        ])
    ca.sign(pkey, digest)
    return ca

def verifyValidFormat(data, ssl_type):
    verified = True
    error = None
    if ssl_type == TYPE_CSR:
        try:
            LOAD_CERT_REQUEST(FILE_TYPE_PEM, data)
        except Exception as e:
            error =  'INVALID CSR'
            verified = False
    if ssl_type == TYPE_CERT:
        try:
            LOAD_CERT(FILE_TYPE_PEM, data)
        except Exception as e:
            error =  'INVALID CERT'
            verified = False
    if ssl_type == TYPE_PKEY:
        try:
            LOAD_PKEY(FILE_TYPE_PEM, data)
        except Exception as e:
            error =  'INVALID PKEY'
            verified = False
    return(verified, error)