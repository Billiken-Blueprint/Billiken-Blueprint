with open("dev-certs/jwt.pem", "r") as f:
    JWT_PRIVATE_KEY = f.read()

with open("dev-certs/jwt.pub", "r") as f:
    JWT_PUBLIC_KEY = f.read()
