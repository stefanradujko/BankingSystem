from random import randint
from math import floor
import sqlite3


def napravi_bazu():
    global conn
    global cur
    conn = sqlite3.connect('card.s3db', uri=True)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER)")
    conn.commit()


def luhn_algorithm(broj):
    checksum = broj % 10
    broj = str(floor(broj / 10))
    brojac = 1
    za_dodavanje = 0
    for c in broj:
        if brojac % 2 == 0:
            if int(c) > 9:
                za_dodavanje += (int(c) - 9)
            else:
                za_dodavanje += int(c)
        else:
            if (int(c) * 2) > 9:
                za_dodavanje += (int(c) * 2 - 9)
            else:
                za_dodavanje += (int(c) * 2)
        brojac += 1
    za_dodavanje += checksum
    if za_dodavanje % 10 == 0:
        return True
    return False


def generisi_pin():
    pin = ''
    for i in range(0, 4):
        pin += str(randint(0, 9))
    return pin


def nadji_id():
    cur.execute('SELECT MAX(id) FROM card')
    broj_red = cur.fetchone()
    if broj_red[0] is None:
        return 0
    return broj_red[0]


def sacuvaj_u_bazi(kartica):
    id = nadji_id() + 1
    cur.execute(f"INSERT INTO card VALUES({id}, {str(kartica[0])}, {kartica[1]}, {0})")
    conn.commit()


def napravi_karticu():
    print('Your card has been created')
    broj_kartice = randint(4000000000000000, 4000009999999999)
    while not (luhn_algorithm(broj_kartice)):
        broj_kartice = randint(4000000000000000, 4000009999999999)
    pin = generisi_pin()
    print(f'Your card number:\n{broj_kartice}')
    print(f'Your card PIN:\n{pin}')
    sacuvaj_u_bazi([broj_kartice, pin])


def proveri_karticu(b, p):
    cur.execute(f'SELECT * FROM card where number = {b} AND pin = {p}')
    id = cur.fetchone()
    if id is None:
        return False
    return True


def prijavi_se():
    b = (input('Enter your card number:\n'))
    p = (input('Enter your PIN:\n'))
    global kartica_prijavljena
    kartica_prijavljena = b
    return proveri_karticu(b, p)


def dodaj_kes(broj, kes):
    cur.execute(f'UPDATE card SET balance = balance + {kes} WHERE number = {broj}')
    conn.commit()


def proveri_karticu_za_transfer(broj):
    if broj == kartica_prijavljena:
        print("You can't transfer money to the same account!")
        return
    if not (luhn_algorithm(int(broj))):
        print('Probably you made a mistake in the card number. Please try again!')
        return False
    cur.execute(f'SELECT * FROM card WHERE number = {broj}')
    if cur.fetchone() is None:
        print('Such a card does not exist.')
        return False
    return True


def proveri_stanje():
    cur.execute(f'SELECT balance FROM card WHERE number = {kartica_prijavljena}')
    stanje = cur.fetchone()
    return stanje[0]


def azuriraj_stanje(kes):
    cur.execute(f'UPDATE card SET balance = balance - {kes} WHERE number = {kartica_prijavljena}')
    conn.commit()


def obavi_transfer():
    print('Transfer')
    broj = input('Enter card number:\n')
    if not (proveri_karticu_za_transfer(broj)):
        return
    kes = int(input('Enter how much money you want to transfer:'))
    stanje = proveri_stanje()
    if stanje < kes:
        print('Not enough money!')
        return
    dodaj_kes(broj, kes)
    azuriraj_stanje(kes)
    print('Success!')


def zatvori_nalog():
    cur.execute(f'DELETE FROM card WHERE number = {kartica_prijavljena}')
    conn.commit()
    print('The account has been closed!')


def meni_za_prijavljenje():
    while True:
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')
        unos = input()
        if unos == '1':
            print(f'Balance: {proveri_stanje()}')
        elif unos == '2':
            kes = int(input('Enter income:\n'))
            dodaj_kes(str(kartica_prijavljena), kes)
            print('Income was added!')
        elif unos == '3':
            obavi_transfer()
        elif unos == '4':
            zatvori_nalog()
            return '-1'
        elif unos == '5':
            print('You have successfully logged out!')
            return '-1'
        elif unos == '0':
            return '0'


def meni():
    while True:
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')
        unos = input()
        if unos == '1':
            napravi_karticu()
        elif unos == '2':
            if prijavi_se():
                print('You have successfully logged in!')
                rad = meni_za_prijavljenje()
                if rad == '0':
                    print('Bye')
                    break
            else:
                print('Wrong card number or PIN!')
        elif unos == '0':
            print('Bye')
            break


napravi_bazu()
meni()
