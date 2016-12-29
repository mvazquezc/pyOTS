import json
import string
import random
import base64
import datetime
import hashlib
import mysql.connector
from Crypto.Cipher import AES
from Crypto import Random

class Database(object):
    """Class to provide database interaction methods"""

    def __init__(self, host, port, username, password, database):
        self.conn = False
        self.db_host = host
        self.db_port = port
        self.db_user = username
        self.db_password = password
        self.db_name = database

    def connect(self):
        """Creates a connection to the database"""
        self.conn = mysql.connector.connect(pool_name="ots", user=self.db_user,
                                            password=self.db_password, host=self.db_host,
                                            port=self.db_port, database=self.db_name)
        return self.conn

    def disconnect(self):
        """Release the database connection"""
        self.conn.close()

class Password(object):
    """Class to work with passwords"""

    def __init__(self, salt):
        self.salt = salt

    def hash_password(self, password):
        """Hash the input password and adds the salt to the hash"""
        hashed_password = hashlib.sha256(password + self.salt).hexdigest()
        return hashed_password

    def verify_hash(self, password, hashed_password):
        """Verify the user input"""
        hashed_input = self.hash_password(password)
        output = False
        if hashed_input == hashed_password:
            output = True
        return output


class OTS(object):
    """Main class"""

    def __init__(self, config_json):
        try:
            config_file = open(config_json, 'r')
            config = json.load(config_file)
            self.db_host = config['db_host']
            self.db_port = config['db_port']
            self.db_user = config['db_user']
            self.db_password = config['db_password']
            self.db_name = config['db_name']
            self.token_length = config['token_length']
            self.password_length = config['password_length']
            self.password_salt = config['password_salt']
            self.secret_key = config['secret_key']
            self.default_ttl = config["default_ttl"]
            self.passwd = Password(self.password_salt)
        except IOError:
            print 'Config file config.json not found or could not be loaded'
            raise
        try:
            self.database = Database(self.db_host, self.db_port, self.db_user, self.db_password,
                                     self.db_name)
            # Test connectivity
            self.database.connect()
        except RuntimeError:
            print 'Unable to connect to the database'
            raise
        print 'OTS started'
        print '-----------'
        print 'DB host: ' + self.db_host + ':' + self.db_port
        print 'DB Connection: ' + self.db_user + '@' + self.db_name
        print 'Token Length: ' + self.token_length
        print 'Password Length: ' + self.password_length
        print 'Default TTL: ' + self.default_ttl

    def generate_password(self):
        """Generate a random password for you"""
        try:
            random_pass = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                                  for _ in range(int(self.password_length)))
        except RuntimeWarning:
            random_pass = "Password not generated"
        return random_pass

    def encrypt_message(self, message):
        """Encrypts and hash the message using the secret key"""
        block_size = 16
        pad = lambda s: s + (block_size - len(s) % block_size) * chr(block_size - len(s)
                                                                     % block_size)
        message = pad(message)
        init_vector = Random.new().read(AES.block_size)
        crypto = AES.new(self.secret_key, AES.MODE_CBC, init_vector)
        hashed_message = base64.b64encode(
            init_vector + crypto.encrypt(message))
        return hashed_message

    def decrypt_message(self, encrypted_message):
        """Decrypts the hashed message using the secret key"""
        block_size = 16
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        hashed_message = base64.b64decode(encrypted_message)
        init_vector = hashed_message[:block_size]
        crypto = AES.new(self.secret_key, AES.MODE_CBC, init_vector)
        message = unpad(crypto.decrypt(hashed_message[block_size:]))
        return message

    def generate_token(self):
        """Generates a new token that will be assigned to a secret"""
        token_in_use = True
        conn = self.database.connect()
        while token_in_use:
            token = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                            for _ in range(int(16)))
            cursor = conn.cursor()
            query = "SELECT token FROM tokens WHERE token = %s"
            cursor.execute(query, (token,))
            rows = cursor.fetchall()
            if len(rows) < 1:
                token_in_use = False
                query = "INSERT INTO tokens (token) VALUES (%s)"
                cursor.execute(query, (token,))
                conn.commit()
        self.database.disconnect()
        return token

    def create_secret(self, message, password, ttl):
        """Create the secret in the database"""
        response = []
        if not ttl:
            ttl = self.default_ttl
        if password:
            hashed_password = self.passwd.hash_password(password)
        else:
            hashed_password = ""
        token = self.generate_token()
        date = datetime.datetime.now().replace(microsecond=0)
        expiration_date = date + datetime.timedelta(days=int(ttl))
        encrypted_message = self.encrypt_message(message)
        try:
            conn = self.database.connect()
            cursor = conn.cursor()
            query = "INSERT INTO data (token, secret, password, timetolive) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (token, encrypted_message, hashed_password, expiration_date))
            conn.commit()
            self.database.disconnect()
            response.append({'Message': 'Secret created', 'token': str(token), 'status': 'ok'})
        except RuntimeWarning:
            print 'Error creating the secret'
            response.append({'token': str(token), 'Message': 'Secret not created', 'status': 'ko'})
        json_response = '{"secret":' + json.dumps(response, indent=4) + '}'
        return json_response

    def delete_secret(self, token):
        """Deletes a secret, even if a non existing token is passed the output will say it has been deleted"""
        response = []
        try:
            conn = self.database.connect()
            cursor = conn.cursor()
            query = "DELETE FROM data WHERE token = %s"
            cursor.execute(query, (token,))
            query = "DELETE FROM tokens WHERE token = %s"
            cursor.execute(query, (token,))
            conn.commit()
            self.database.disconnect()
            response.append({'Message': 'Secret deleted', 'token': str(token), 'status': 'ok'})
        except RuntimeWarning:
            print 'Error deleting the secret'
            response.append({'token': str(token), 'Message': 'Secret not deleted', 'status': 'ko'})
        json_response = '{"secret":' + json.dumps(response, indent=4) + '}'
        return json_response

    def view_secret(self, token):
        """Returns some information about the secret"""
        response = []
        secret_exists = False
        secret_password_protected = False
        try:
            conn = self.database.connect()
            cursor = conn.cursor()
            query = "SELECT token, password FROM data WHERE token = %s"
            cursor.execute(query, (token,))
            rows = cursor.fetchall()
            self.database.disconnect()
            if len(rows) > 0:
                secret_exists = True
                if len(rows[0][1]) > 1:
                    secret_password_protected = True
                response.append({'token': str(token), 'secret_exists': str(secret_exists),
                                 'secret_password_protected': str(secret_password_protected)})
            else:
                print 'Secret does not exist or has been already opened'
                response.append({'token': str(token), 'secret_exists': str(secret_exists),
                                 'secret_password_protected': str(secret_password_protected)})
        except RuntimeWarning:
            print 'Error getting data about the secret'
        json_response = '{"secret":' + json.dumps(response, indent=4) + '}'
        return json_response

    def open_secret(self, token, password):
        """Returns the secret"""
        response = []
        date = datetime.datetime.now().replace(microsecond=0)
        secret = None
        if not password:
            password = ""
        try:
            conn = self.database.connect()
            cursor = conn.cursor()
            query = "SELECT token, password, secret, timetolive FROM data WHERE token = %s"
            cursor.execute(query, (token,))
            rows = cursor.fetchall()
            self.database.disconnect()
            if len(rows) > 0:
                time_to_live = rows[0][3]
                if date > time_to_live:
                    response.append({'token': str(token), 'message': 'Secret has expired'})
                    print "Secret has expired"
                else:
                    if len(rows[0][1]) > 1:
                        password_is_ok = self.passwd.verify_hash(password, str(rows[0][1]))
                        if password_is_ok:
                            secret = self.decrypt_message(str(rows[0][2]))
                            response.append({'token': str(token), 'message': str(secret)})
                            self.delete_secret(token)
                        else:
                            response.append({'token': str(token), 'message': 'Wrong password'})
                    else:
                        secret = self.decrypt_message(str(rows[0][2]))
                        response.append({'token': str(token), 'message': str(secret)})
                        self.delete_secret(token)
        except RuntimeWarning:
            print 'Error opening the secret'
            response.append({'token': str(token), 'Message': 'Error opening the secret'})
        json_response = '{"secret":' + json.dumps(response, indent=4) + '}'
        return json_response
