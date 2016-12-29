testing = True
if testing:
message = "this is a message"
messagecrypt = self.encrypt_message(message)
print messagecrypt
messagedecrypt = self.decrypt_message(messagecrypt)
print messagedecrypt
