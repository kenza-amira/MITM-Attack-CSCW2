# Man in the Middle Attack

You are asked to mount a (wo)Man-in-the-Middle (MitM) attack against the toy implementation of an encrypted chat between terminals.

## 3.1 High-level overview

When Alice and Bob hear about encryption, they immediately set out to implement an encrypted chat client so that they are sure no one eavesdrops their intimate discussions. They decide to use AES6 to encrypt their messages, since
everyone says it’s the best. They also hear of the Diffie-Hellman key exchange (DHKE) and figure it would be cool to use a new secret key for AES every time they connect.

### 3.1.1 AES

Just like every symmetric encryption scheme, AES consists of two algorithms:

• The encryption algorithm takes a key K1 and a message M1 as input and returns a ciphertext C1 as output:
C1 = Enc(K1, M1)
• The decryption algorithm takes a key K2 and a ciphertext C2 as input and returns a message M2 as output:
M2 = Dec(K2, M2)

If a message M is encrypted with key K and the resulting ciphertext C is decrypted with the same key K, the result of the decryption will be the original message M: ∀K∀M, M = Dec(K,Enc(K, M))
A simple library for encrypting and decrypting using pyaes is provided in symmetric.py.

### 3.1.2 Diffie-Hellman Key Exchange

This is a protocol between two parties (say Alice and Bob) that want to obtain a common key that is unknown to anybody else. Their communication takes place over an insecure channel that anyone can eavesdrop.
A physical-world equivalent is the following: A group of people sit around a table and two of them want to speak in private. They can have a brief exchange (of very long numbers) which everybody hears. After that they will possess a common secret that no one else knows. 
They can use this secret as the key for encrypting, sending and decrypting private messages in plain sight.
We assume that both parties have agreed beforehand on a finite cyclic group G and a generator g of G. For production software, these parameters are standardised by cryptographers and hardcoded in the implementation by the developers.

These are the steps of the protocol:
• Alice chooses a random number x and calculates a = g x
• Alice sends a to Bob.
• Bob chooses a random number y and calculates b = g y
• Bob sends b to Alice.

– Now all eavesdroppers know a and b, but not x and y.
• Alice derives the common secret b x
• Bob derives the common secret a y

Given that (g x)y = (g y) x, both Alice and Bob have derived the same common secret. Assuming that an eavesdropper cannot find x from a or y from b, we conclude that no one else can derive the common secret.
A simple library for doing the necessary steps of DHKE is provided in diffie hellman.py. You can see how to use it in the do Diffie Hellman() function in util.py.

### 3.1.3 Putting it all together

The entire process of chatting is then as follows:
1. Alice and Bob establish a communication socket
2. They do DHKE over this socket
3. Bob encrypts his message under the derived key (with AES)
4. Bob sends the resulting ciphertext through the socket
5. Alice decrypts the ciphertext using the derived key
6. Alice reads the message
Steps 3–6 can be repeated as many times as desired, possibly with changed roles. (In our implementation, the process is repeated only twice, so Bob sends first, then Alice, then both parties terminate.)

### 3.1.4 MitM attack

The described approach sounds very reasonable. Unfortunately Alice and Bob overlooked a fatal flaw: When communicating over the internet (or even locally), one cannot know with certainty that they are speaking to the intended
party, at least not without using some form of cryptographic authentication.
Going back to our round-table example, consider the case where every member of the group wears a different mask, uses a voice jammer and sits at random seats. Alice would be unable to recognize Bob. In an even worse scenario, 
if Bob happens to be missing from the table, someone with a good disguise could impersonate him and fool Alice into performing DHKE with him. This is why Alice and Bob should have agreed to only speak to each other after authenticating themselves.
Given that no authentication takes place, Eve the attacker is now able to do the following: After Alice opens his end of the socket and before Bob connects, Eve connects and performs a DHKE with Alice. Eve then opens a new
socket and waits for Bob to connect. When Bob and Eve connect, they perform another DHKE. Now Eve can decrypt messages from one party, read them and reencrypt them for the other party. If she so wishes she can even send arbitrary
messages, completely unrelated to the original ones. In short, she has complete control of the channel while Alice and Bob think they communicate with each other privately.

## 3.2 Implementation details

### 3.2.1 How to use the provided code

Open two terminals and navigate to the directory with the scripts. First run python3 alice.py in one and then python3 bob.py in the other (the order is important). You should see secure channel establishment, a couple of
messages being exchanged and finally the channel closing.

## 3.3 Code overview

Open both aforementioned scripts with your favourite editor. Each of the two scripts calls setup() with its name and the name of the pre-agreed buffer file over which communication happens. This name is set in const.py. Then
Alice waits for a message, while Bob sends it. Alice then prints the message and the roles are reversed. Finally both parties close their sockets.
Familiarise yourself with the scripts and understand which lines correspond to each of the steps above. You can optionally dive in the code of the various supporting sources as well.

## 3.4 Exercise

You will have to implement and submit eve.py. The attack should execute correctly when first alice.py is started in one terminal, then eve.py in a second and last bob.py in a third. eve.py should be followed by exactly one of the following three flags: --relay, --break-heart or --custom.
• If the flag is --relay, Eve should just relay the two messages from Alice to Bob and from Bob to Alice. In this case, the outputs of both alice.py and bob.py in the terminals should be identical to the case when the MitM attack isn’t executed.
• With the --break-heart flag, Eve should change the messages so that Alice receives the message ”I hate you!” and Bob receives ”You broke my heart...”. Remember, Eve still has to encrypt both messages correctly.
• As for the --custom flag, after receiving Bob’s messsage, Eve must prompt the user to input a message to the terminal and then must send this message to Alice instead. The same should happen for Alice’s message; Eve must prompt the user for a second message and this time send it to Bob.

Hint: Your solution will have to use the buffer file somehow. The function os.rename() will prove helpful.

Note: It may happen that a script dies without closing its socket gracefully. In that case, you should manually remove
the remaining buffer file (by default called buffer) before restarting the scripts.
