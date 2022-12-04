# "THE BEER-WARE LICENSE" (Revision 42):
# <flal@melix.net> wrote this file. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return

# read a json describing people do the magic to pick two different people to send
# gifts to so that you don't have to gift yourself, or your partner and send a mail to tell you, so that no-one know.
#
# expects SMTP config by environment variables (SMTP_HOST, SMTP_LOGIN, SMTP_PASS)
# usage : main.py data.json
#
# ex json 
# [
#   {"nom":"Alice",
#    "blacklist": ["Bob"],
#    "email": "alice@corp.com"},
#   {"nom":"Bob",
#    "blacklist": ["Alice", "Floflo"],
#    "email": "alice@corp.com"},
# ..]

import itertools
import random
import smtplib
import sys, os
import json


with open(sys.argv[1], 'br') as input_data :
    raw_dat = json.load(input_data)
    persons = [d["nom"] for d in raw_dat]
    persons_set = set(persons)
    email_addresses = {}
    blacklist = {}
    for p in raw_dat :
        email_addresses[p["nom"]] = p["email"]
        bll = p["blacklist"]
        for blacklisted_person in bll :
            if not blacklisted_person in persons_set :
                print(f"{blacklisted_person} est blacklistée pour {p} mais n'existe pas")
                exit(-1)
        blacklist[p["nom"]] = bll
 
        
tentatives = 0
while tentatives < 1000 :
    # generate a list of all possible binomes, excluding blacklisted combinations
    binomes = list(itertools.combinations(persons, 2))
    random.shuffle(binomes)
    result = {}
    has_present = set()
    for p in persons :
        try :
            # find the first pair NOT containing this person
            not_me = filter(lambda b: not p in b, binomes)
            not_blacklist = filter(lambda b: not b[0] in blacklist[p], not_me)
            not_blacklist = filter(lambda b: not b[1] in blacklist[p], not_blacklist)
            binome = next(not_blacklist)
        except StopIteration :
            # no solution
            break

        for target in binome :
            if target in has_present :
                # this one has 2 presents, remove all possible couple
                # containing this person.
                binomes = list(filter(lambda c: not target in c, binomes))
            else :
                has_present.add(target)
        result[p] = binome
        try :
            binomes.remove(binome)
        except ValueError:
            # binome already removed
            pass
    if len(result) == len(persons):
        break
    print("tentatives ", tentatives, " --> retry")
    tentatives += 1


print("dumping result to : result_kdo.json")
with open("result_kdo.json", 'w') as f :
    f.write(json.dumps(result, ensure_ascii=False))

# check
counts = {k:0 for k in persons}
for k,(a,b) in result.items() :
    counts[a] += 1
    counts[b] += 1
    assert(a != k)
    assert(b != k)
    assert(not a in blacklist[k])
    assert(not b in blacklist[k])
    
for c in counts.values() :
    assert(c == 2)

    
SMTP_HOST = os.environ['SMTP_HOST']
SMTP_PORT = 587
SMTP_LOGIN = os.environ['SMTP_LOGIN']
SMTP_PASS = os.environ['SMTP_PASS']

print("SMTP :", SMTP_HOST, SMTP_LOGIN)
# sending emails
s = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
s.starttls()

s.login(SMTP_LOGIN, SMTP_PASS)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

message_template = "Salut {name}!\n\nTu as l'honneur et le privilège d'offrir un truc à {gift_one} et {gift_two} ! Chic.\n\nGros bisous\nLe robot super content de Noël ( https://github.com/flo-dhalluin/tirage-kdo-bot )"

for name, gifts in result.items():
    print("sending mail to :", name, "->", email_addresses[name])
    msg = MIMEMultipart()
    msg["From"] = "SuperContent <no-reply@flal.net>"
    msg["To"] = email_addresses[name]
    msg["Subject"] = "[Cadeaux Famille D'halluin] A qui va tu faire un cadeau à Noël ?"
    msg.attach(MIMEText(message_template.format(name=name, gift_one=gifts[0], gift_two=gifts[1]), 'plain'))
    s.send_message(msg)
