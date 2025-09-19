import bcrypt
import sys

def generate_hash(password):
    """
    Generates a bcrypt hash for a given password.
    """
    if not password:
        print("Error: Please provide a password.")
        return
        
    # Encode the password to bytes, generate salt, and hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # Decode back to a string to print and store in the database
    print(hashed_password.decode('utf-8'))

if __name__ == '__main__':
    # Check if a password was provided as a command-line argument
    if len(sys.argv) > 1:
        password_to_hash = sys.argv[1]
        generate_hash(password_to_hash)
    else:
        print("Usage: python generate_hash.py <password_to_hash>")
