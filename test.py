from werkzeug.security import generate_password_hash,check_password_hash

password="123"
print(password)
hash = generate_password_hash(password)
print(hash)
cp = (check_password_hash(hash,password))
print(cp)

if cp == True:
    print("Password is correct")
else:
    print("Password is incorrect")