"""Configuration module for JWT keys and other settings."""

with open("jwt_dev.pem", "r") as f:
    JWT_PRIVATE_KEY = f.read()
    
with open("jwt_dev.pub", "r") as f:
    JWT_PUBLIC_KEY = f.read()

SECRET_KEY = "27e7a5811fabc16a334ba2aaca332a8d3319506e8dcc0e9724cf7c28109065c6"
