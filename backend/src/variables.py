with open('jwt_dev.pem', 'r') as f:
    JWT_PRIVATE_KEY = f.read()
with open('jwt_dev.pub', 'r') as f:
    JWT_PUBLIC_KEY = f.read()
