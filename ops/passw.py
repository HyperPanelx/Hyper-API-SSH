from password_generator import PasswordGenerator
pwo = PasswordGenerator()
def passgen():
    pwo.minlen = 5 # (Optional)
    pwo.maxlen = 8 # (Optional)
    pwo.minuchars = 1 # (Optional)
    pwo.minlchars = 5 # (Optional)
    pwo.minnumbers = 1 # (Optional)
    pwo.minschars = 0 # (Optional)
    passgen=pwo.generate()
    return passgen