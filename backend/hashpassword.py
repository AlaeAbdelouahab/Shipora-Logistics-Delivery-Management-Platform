import bcrypt

# mot de passe en clair
password = "livreur1depot3"

# génération du hash
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

print('livreur 1 depot 3: '+ hashed.decode()) 
print('\n')

password = "livreur2depot3"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

print('livreur 2 depot 3: '+ hashed.decode()) 
print('\n')

password = "livreur3depot3"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

print('livreur 3 depot 3: '+ hashed.decode()) 
print('\n')
