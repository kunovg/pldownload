import bcrypt

def hash(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    plain_text_password = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt()).decode()

def check(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    if bcrypt.hashpw(str.encode(plain_text_password), str.encode(hashed_password)) == str.encode(hashed_password):
        return True
    return False
