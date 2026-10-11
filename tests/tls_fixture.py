"""Throwaway certificate authority and localhost server certificate for TLS tests.

Python 3.13 verifies with VERIFY_X509_STRICT by default, so the CA and server
certificates carry the extensions a real authority would: CA constraints,
key usage, server-auth purpose and key identifiers.
"""
import pathlib,subprocess

SERVER_EXT=('basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n'
            'subjectAltName=DNS:localhost,IP:127.0.0.1\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid\n')

def make_certificates(directory):
    """Create ca.pem, server.pem and server.key in directory; returns the directory."""
    d=pathlib.Path(directory)
    run=lambda *a:subprocess.run(a,cwd=d,check=True,capture_output=True)
    (d/'server.ext').write_text(SERVER_EXT)
    run('openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','2','-subj','/CN=OmaPit test CA','-keyout','ca.key','-out','ca.pem','-extensions','v3_ca','-addext','keyUsage=critical,keyCertSign,cRLSign')
    run('openssl','req','-newkey','rsa:2048','-nodes','-subj','/CN=localhost','-keyout','server.key','-out','server.csr')
    run('openssl','x509','-req','-in','server.csr','-CA','ca.pem','-CAkey','ca.key','-CAcreateserial','-days','2','-extfile','server.ext','-out','server.pem')
    return d
