import bcrypt
import scrypt

import random


class Crypto():
    """ Helper functions to create, and verify, bcrypt and scrypt encrypted strings. """


    @staticmethod
    def hash_bcrypt(password):
        return bcrypt.hashpw(password, bcrypt.gensalt())


    @staticmethod
    def hash_scrypt(password, salt_length=64, max_time=0.5):
        return scrypt.encrypt(Crypto._random_salt(salt_length), password, max_time)

    @staticmethod
    def verify_bcrypt_hash(password, hash):
        if bcrypt.hashpw(password, hash) == hash:
            return True
        else:
            return False

    @staticmethod
    def verify_scrypt_hash(password, hash):
        try:
            scrypt.decrypt(hash, password, maxtime=0.5)
            return True
        except scrypt.error:
            return False

    @staticmethod
    def _random_salt(length):
        """ Random string to 'salt' up the hash. b/scrypt already do this but just in case.
        'length' shouldn't be > 255 because thats the size limit in the database where it's stored.
        """
        if length > 255:
            length = 200    # Just in case, limited a bit more to save room for the hashes.

        return ''.join(chr(random.randint(0,255)) for i in range(length))