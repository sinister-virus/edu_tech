from werkzeug.security import generate_password_hash,check_password_hash

password="qwerty"
print(password)
hash = generate_password_hash(password)
print(hash)
cp = "scrypt:32768:8:1$taGrXC3Sc4B9YwcK$3c026730969a1ddcf2471a558e1e3a487496a085de048f88071784b4bc7d138ebc8b54c8ffee4894aad4f908db598e94ec9cf7a423d8821bfad0ca71ecb93039"
print(cp)

if cp == hash :
    print("Password is correct")
else:
    print("Password is incorrect")