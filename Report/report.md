---
title: Segurança Informática em Redes e Sistemas
author: Alameda -- Grupo 10
---

![81201 -- Tomás Cunha -- tomas.cunha\@tecnico.ulisboa.pt](81201.jpg){ width=30% } 

![81209 -- Guilherme Santos -- guilherme.j.santos\@tecnico.ulisboa.pt](81209.jpg){ width=30% }

![81703 -- Nuno Santos -- nuno.v.santos\@tecnico.ulisboa.pt](81703.jpg){ width=30% }

\newpage

# Problem

After pairing the phone with the computer, keys are generated and certain files on the computer can be encrypted when the phone is not connected to it. A phone is connected when near to the computer through the exchange of a token.

We need to ensure that:

  * the paired computer files can only be decrypted with the paired phone’s presence, so attackers can’t fake 
    the phone’s presence.

  * the phone only sends the token to the paired computer,
    so attackers can’t fake the computer’s presence. Otherwise the fake computer can get
    the token and use a fake phone to decrypt the files.

  * the key exchange (token) is secure because if the attacker is listening and gets
    the exchanged message by the phone he cannot get the keys to decrypt the files.
  * token needs to be unique to avoid replay attacks.
  * the key storage needs to be secure so that if the device keeping the keys is
    compromised the attacker cannot get the keys to decrypt the files.
 
Problem being solved:

Only those with access to both the paired phone and computer can access the encrypted files.

# Requirements

  #. Confidentiality (only the paired computer can read the token)
  #. Authentication of origin (the paired computer only accepts tokens sent by the paired phone)
  #. Fault tolerance (if the computer crashes when the computer is connected, the files cannot be left unprotected)

# Solution

During the initial pairing, the PC creates and displays its RSA public key in a QR code on the screen.
The phone scans this key, stores it, and sends its own generated RSA public key encrypted with the
PC’s public key, which is stored by the PC to be used as a Key Encryption Key. This serves as a
protection from man-in-the-middle attacks.

After this verification, the PC generates and shares an AES-256 session key. From this point on,
this key is used to secure the communication channel. The phone generates two other AES-256 keys,
one to be used for file encryption, and one to encrypt that key before sending it to the PC.
This key is stored, and the pairing process is completed.

After pairing, the phone can connect to the PC, who (after the initial session key exchange) sends the
encrypted File Encryption key, which is securely stored on the PC. The phone decrypts it and sends it
back to the PC, who uses it to decrypt the files. The phone then has to keep sending heartbeats (which
include a nonce to avoid replay attacks) so that the PC can know the phone is in range. After the phone
is disconnected, since the PC no longer receives heartbeats, it encrypts the files again and deletes
the FE key from storage, keeping only its encrypted copy. The PC maintains a log of the operations it
performs. In case of a crash, after recovery it will encrypt all the files with the decrypted FE key,
then deletes the key and waits for the phone to be reconnected.
 
Basic

:  Initial implementation without fault tolerance and secure channels.
 
Intermediate

: Implementation of confidentiality with secure channels.
 
Advanced

: Implementation of fault tolerance.
