# read a json describing people do the magic to pick two different people to send
# gifts to so that you don't have to gift yourself, or your partner and send a mail to tell you, so that no-one know.
#
# expects SMTP config by environment variables (SMTP_HOST, SMTP_LOGIN, SMTP_PASS)
# usage : main.py data.json
#
# ex json 
# [
#   {"nom":"Alice",
#    "partner": "Bob",
#    "email": "alice@corp.com"},
#   {"nom":"Bob",
#    "partner": "Alice",
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
    couples = []
    has_partner = set()
    for p in raw_dat :
        email_addresses[p["nom"]] = p["email"]
        if "partner" in p and not p["nom"] in has_partner :
            couples.append(set((p["nom"], p["partner"])))
            has_partner.add(p["nom"])
            has_partner.add(p["partner"])
            

    
conjoints = {}
for a,b in couples :
    conjoints[a] = b
    conjoints[b] = a
print(conjoints)

def not_a_couple(binome) :
    a,b = binome
    if a in conjoints :
        return b != conjoints[a]
    return False

def is_gift_possible(person, binome) :
    is_in_binome = p in binome
    is_conjoint = p in conjoints and conjoints[p] in binome
    return not ( is_in_binome or is_conjoint)

tentatives = 0
while tentatives < 100 :
    # generate a list of all possible binomes, excluding couples
    binomes = list(filter(not_a_couple, itertools.combinations(persons, 2)))
    random.shuffle(binomes)
    result = {}
    has_present = set()
    for p in persons :
        try :
            binome = next(filter(lambda b: is_gift_possible(p, b), binomes))
        except StopIteration :
            # no solution
            break
        binomes.remove(binome)
        result[p] = binome
        for o in binome :
            if o in has_present :
                # this one has 2 presents, remove all possible couple
                # containing this person.
                binomes = list(filter(lambda c: not o in c, binomes))
            else :
                has_present.add(o)
    if(len(result) == len(persons)):
        # we have a solution !!
        break
    print("failed", tentatives)
    tentatives += 1

with open("result_kdo.json", 'w') as f :
    f.write(json.dumps(result))

# check
counts = {k:0 for k in persons}
for k,(a,b) in result.items() :
    counts[a] += 1
    counts[b] += 1
    assert(a != k)
    assert(b != k)

    
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
