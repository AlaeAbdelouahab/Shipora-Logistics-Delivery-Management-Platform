from security import get_password_hash

password = "Admin123"
hashed = get_password_hash(password)
print(hashed)
