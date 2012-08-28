#########################################################################################################

#How to generate a CA certificate
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)
ca = crypto.X509()
ca.set_version(3)
ca.set_serial_number(1)
ca.get_subject().CN = "ca.example.com"
ca.gmtime_adj_notBefore(0)
ca.gmtime_adj_notAfter(24 * 60 * 60)
ca.set_issuer(ca.get_subject())
ca.set_pubkey(key)
ca.add_extensions([
    crypto.X509Extension("basicConstraints", True,"CA:TRUE, pathlen:0"),
    crypto.X509Extension("keyUsage", True,"keyCertSign, cRLSign"),
    crypto.X509Extension("subjectKeyIdentifier", False, "hash",subject=ca),
    ])
ca.sign(key, "sha1")
##########################################################################################################

#How to sign an X509 certificate using a CA
ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,"ca.pem")
ca_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM,"ca.pem")

key = OpenSSL.crypto.PKey()
key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

cert = OpenSSL.crypto.X509()
cert.get_subject().CN = "node1.example.com"
cert.set_serial_number(1)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(24 * 60 * 60)
cert.set_issuer(ca_cert.get_subject())
cert.set_pubkey(key)
cert.sign(ca_key, "sha1")
###########################################################################################################

#How to generate an X509 Certificate Request (CSR)
key = OpenSSL.crypto.PKey()
key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
req = OpenSSL.crypto.X509Req()
req.get_subject().CN = "node1.example.com"
req.set_pubkey(key)
req.sign(key, "sha1")
# Write private key
print OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
# Write request
print OpenSSL.crypto.dump_certificate_request(OpenSSL.crypto.FILETYPE_PEM, req)
###########################################################################################################

#How to create an X509 certificate from a Certificate Signing Request and sign it with a CA
ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
ca_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM,"ca.pem")
req = OpenSSL.crypto.load_certificate_request(OpenSSL.crypto.FILETYPE_PEM,open("req.csr").read())
cert = OpenSSL.crypto.X509()
cert.set_subject(req.get_subject())
cert.set_serial_number(1)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(24 * 60 * 60)
cert.set_issuer(ca_cert.get_subject())
cert.set_pubkey(req.get_pubkey())
cert.sign(ca_key, "sha1")
print OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
###########################################################################################################


#The code sample below shows how to check whether a certificate matches with a certain private key.
#OpenSSL has a function for this, X509_check_private_key, but pyOpenSSL provides no access to it
ctx = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)
ctx.use_privatekey(key)
ctx.use_certificate(cert)
try:
  ctx.check_privatekey()
except OpenSSL.SSL.Error:
  print "Incorrect key"
else:
  print "Key matches certificate"
############################################################################################################

