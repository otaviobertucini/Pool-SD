from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

random_seed = Random.new().read

keyPair = RSA.generate(1024, random_seed)
pubKey = keyPair.publickey() 

True_text = 'Hello Bob'
Fake_text = 'Bye Bob'

hashA = SHA256.new(True_text.encode('utf-8')).digest()
digitalSign = keyPair.sign(hashA, '')

print("HashA:" + repr(hashA) + "\n")
print("Digital signature:" + repr(digitalSign) + "\n")

#hashB = SHA256.new(True_text.encode('utf-8')).digest()
hashB = SHA256.new(Fake_text.encode('utf-8')).digest()

print("HashB:" + repr(hashB) + "\n")
#print("HashC:" + repr(hashC) + "\n")

if pubKey.verify(hashB, digitalSign):
    print("O texto autêntico é " + True_text)
    
#elif pubKey.verify(hashB, digitalSign):
 #   print("O texto autêntico é" + Fake_text)
    
else:
    print("Nenhum dos textos é autêntico")