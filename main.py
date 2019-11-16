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
    email_addresses = {}
    blacklist = {}
    for p in raw_dat :
        email_addresses[p["nom"]] = p["email"]
        blacklist[p["nom"]] = p["blacklist"]
 

def filter_first_in_blacklist(c):
    """ this to avoid aving a couple """
    return not c[0] == blacklist[c[1]][0] or not c[1] == blacklist[c[0]][0]
        
tentatives = 0
while tentatives < 1000 :
    # generate a list of all possible binomes, excluding blacklisted combinations
    binomes = list(filter(filter_first_in_blacklist,  itertools.combinations(persons, 2)))
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
    if len(result) == len(persons):
        break
    print("failed", tentatives)
    tentatives += 1

    
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


# sending emails
s = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
s.starttls()

s.login(SMTP_LOGIN, SMTP_PASS)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

message_template = "Salut {name}!\n\nTu as l'honneur et le privilège d'offrir un truc à {gift_one} et {gift_two} ! Chic.\n\nGros bisous\nLe robot super content de Noël ( https://github.com/flo-dhalluin/tirage-kdo-bot )"

for name, gifts in result.items():
    msg = MIMEMultipart()
    msg["From"] = "SuperContent <no-reply@flal.net>"
    msg["To"] = email_addresses[name]
    msg["Subject"] = "[Cadeaux Famille D'halluin] A qui va tu faire un cadeau à Noël ?"
    msg.attach(MIMEText(message_template.format(name=name, gift_one=gifts[0], gift_two=gifts[1]), 'plain'))
    s.send_message(msg)
