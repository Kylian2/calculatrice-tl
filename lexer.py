#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : lexer de la calculatrice
"""

import sys
import enum
import definitions as defs


# Pour lever une erreur, utiliser : raise LexerError("message décrivant l'erreur dans le lexer")
class LexerError(Exception):
    pass


#################################
# Variables et fonctions internes (privées)

# Variables privées : les trois prochains caractères de l'entrée
current_char1 = ''
current_char2 = ''
current_char3 = ''

# Initialisation : on vérifie que EOI n'est pas dans V_C et on initialise les prochains caractères
def init_char():
    global current_char1, current_char2, current_char3
    # Vérification de cohérence : EOI n'est pas dans V_C ni dans SEP
    if defs.EOI in defs.V_C:
        raise LexerError('character ' + repr(defs.EOI) + ' in V_C')
    defs.SEP = {' ', '\n', '\t'} - set(defs.EOI)
    defs.V = set(tuple(defs.V_C) + (defs.EOI,) + tuple(defs.SEP))
    current_char1 = defs.INPUT_STREAM.read(1)
    # print("@", repr(current_char1))  # decomment this line may help debugging
    if current_char1 not in defs.V:
        raise LexerError('Character ' + repr(current_char1) + ' unsupported')
    if current_char1 == defs.EOI:
        current_char2 = defs.EOI
        current_char3 = defs.EOI
    else:
        current_char2 = defs.INPUT_STREAM.read(1)
        # print("@", repr(current_char2))  # decomment this line may help debugging
        if current_char2 not in defs.V:
            raise LexerError('Character ' + repr(current_char2) + ' unsupported')
        if current_char2 == defs.EOI:
            current_char3 = defs.EOI
        else:
            current_char3 = defs.INPUT_STREAM.read(1)
            # print("@", repr(current_char3))  # decomment this line may help debugging
            if current_char3 not in defs.V:
                raise LexerError('Character ' + repr(current_char3) + ' unsupported')

    return

# Accès aux caractères de prévision
def peek_char3():
    global current_char1, current_char2, current_char3
    return (current_char1 + current_char2 + current_char3)


def peek_char1():
    """
    Renvoie le prochain caractère de l'entrée
    """
    global current_char1
    return current_char1


def consume_char():
    """
    Permet d’avancer d’un caractère et ne renvoie rien (None).
    Une fois que la lecture est terminée, faire un appel à la fonction
    renverra toujours EOI.
    """
    global current_char1, current_char2, current_char3
    if current_char2 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = defs.EOI
        return
    if current_char3 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = current_char2
        current_char2 = defs.EOI
        return
    next_char = defs.INPUT_STREAM.read(1)
    # print("@", repr(next_char))  # decommenting this line may help debugging
    if next_char in defs.V:
        current_char1 = current_char2
        current_char2 = current_char3
        current_char3 = next_char
        return
    raise LexerError('Character ' + repr(next_char) + ' unsupported')

def expected_digit_error(char):
    return LexerError('Expected a digit, but found ' + repr(char))

def unknown_token_error(char):
    return LexerError('Unknown start of token ' + repr(char))

# Initialisation de l'entrée
def reinit(stream=sys.stdin):
    global input_stream, current_char1, current_char2, current_char3
    assert stream.readable()
    defs.INPUT_STREAM = stream
    current_char1 = ''
    current_char2 = ''
    current_char3 = ''
    init_char()


#################################
## Automates pour les entiers et les flottants

def read_full_word(initial, automate, acceptant):
    """
    Lit le mot courant en entier (du premier caractère au caractère EOI).
    À la fin de l'exécution, l'entrée entière sera consommée
    """
    current_state = initial
    char = peek_char1()
    consume_char()
    # Cas de base : uniquement le EOI (dans ce cas ce n'est pas reconnu, le mot vide n'étant pas reconnu)
    if (char == defs.EOI):
        return False

    while (char != defs.EOI):
        adjacent_node = automate[current_state]
        transition = False
        # Vérifie s'il est possible de faire une transition
        for sommet, f in adjacent_node:
            if (f(char)):
                current_state = sommet
                transition = True
                break
        # Si on n'a pas réussi à faire une transition alors le mot n'est pas reconnu, on renvoie False
        # On consomme tous les caractères mais sans faire toutes les autres vérifications
        if (not transition):
            consume_char()
            while (peek_char1() != defs.EOI):
                consume_char()
            return False
        char = peek_char1()
        consume_char()

    # On vérifie que le mot se termine sur l'état acceptant
    if not (current_state in acceptant):
        return False
    return True

'''
Ancienne version avec un peak de 1 uniquement
def read_word(initial, automate, acceptant):
    """
    Lit sur l'entrée jusqu'à trouver le plus grand mot étant accepté par l'automate en paramètre

    Retourne le mot ou une exception
    """
    current_state = initial
    full_word = ""
    current_making_word = ""
    char = peek_char1()

    # Cas de base : uniquement le EOI (dans ce cas ce n'est pas reconnu, le mot vide n'étant pas reconnu)
    if (char == defs.EOI):
        return None

    while (char != defs.EOI):
        adjacent_node = automate[current_state]
        transition = False
        # Vérifie s'il est possible de faire une transition
        for sommet, f in adjacent_node:
            if (f(char)):
                current_state = sommet
                transition = True
                break
        # Si on n'a pas réussi à faire une transition alors le nouveau caractère forme un mot non reconnu.
        # Dans ce cas, on renvoie si c'est possible le mot précédant faisant partie du langage
        if (not transition):
            if (full_word == ""):
                return None
            return full_word

        current_making_word += char
        # Si on est sur un état acceptant alors le mot actuel + les nouveaux caractères sont valides
        if(current_state in acceptant):
            full_word += current_making_word
            current_making_word = ""
        consume_char()
        char = peek_char1()

    if (full_word == ""):
        return None

    return full_word
'''

def read_word(initial, automate, acceptant):
    """
    Lit sur l'entrée jusqu'à trouver le plus grand mot étant accepté par l'automate en paramètre
    Fonctionne avec un peek de 3 caractères en avant afin de dire si un mot est correct ou non.

    Retourne le mot ou une exception
    """
    current_state = initial
    full_word = ""
    current_making_word = ""
    chars = peek_char3()

    while chars:
        # On parcourt les trois caractères
        for char in chars:
            # On effectue le traitement si le caractère n'est pas le caractère de fin
            if char != defs.EOI:
                adjacent_node = automate[current_state]
                transition = False
                # Vérifie s'il est possible de faire une transition
                for sommet, f in adjacent_node:
                    if (f(char)):
                        current_state = sommet
                        transition = True
                        break
                # Si on n'a pas réussi à faire une transition alors le nouveau caractère forme un mot non reconnu.
                # Dans ce cas, on renvoie si c'est possible le mot précédant faisant partie du langage
                if (not transition):
                    if (full_word == ""):
                        return None
                    return full_word

                current_making_word += char
                # Si on est sur un état acceptant alors le mot actuel + les nouveaux caractères sont valides
                if (current_state in acceptant):
                    full_word += current_making_word
                    for i in range(len(current_making_word)):
                        consume_char()
                    current_making_word = ""
                    chars = peek_char3()
                    break
            # Si le caractère courant est le EOI alors, on a terminé de lire l'entrée et on peut retourner le dernier
            # mot reconnu par l'automate.
            else:
                if (full_word == ""):
                    return None
                return full_word
    if (full_word == ""):
        return None
    return full_word

# Représentation en dictionnaire de l'automate "integer".
# Pour chaque sommet est associé un dictionnaire de sommets adjacents,
# la fonction lambda en valeur correspond à la condition nécessaire pour passer à l'autre sommet
INT_AUTOMATE = {
    "q0": [
        ("q1", lambda x: x in defs.DIGITS)
    ],
    "q1": [
        ("q1", lambda x: x in defs.DIGITS)
    ],
}
# État initial
INT_INITIAL = "q0"
# États finaux
INT_AUTOMATE_ACCEPTANT = ["q1"]

# Automate des flottants
FLOAT_AUTOMATE = {
    "q0": [
        ("q1", lambda x: f"{x}" == "."),
        ("q2", lambda x: x in defs.DIGITS)
    ],
    "q1": [
        ("q3", lambda x: x in defs.DIGITS)
    ],
    "q2": [
        ("q2", lambda x: x in defs.DIGITS),
        ("q3", lambda x: f"{x}" == "."),
    ],
    "q3": [
        ("q3", lambda x: x in defs.DIGITS)
    ],
}
FLOAT_AUTOMATE_INITIAL = "q0"
FLOAT_AUTOMATE_ACCEPTANT = ["q3"]

# Automate des nombres
NUMBER_AUTOMATE = {
    "q0": [
        ("q1", lambda x: x == "."),
        ("q3", lambda x: x in defs.DIGITS)
    ],
    "q1": [
        ("q2", lambda x: x in defs.DIGITS)
    ],
    "q2": [
        ("q2", lambda x: x in defs.DIGITS),
        ("q4", lambda x: x in defs.EXPONENT)
    ],
    "q3": [
        ("q2", lambda x: x == "."),
        ("q3", lambda x: x in defs.DIGITS),
        ("q4", lambda x: x in defs.EXPONENT)
    ],
    "q4": [
        ("q5", lambda x: x in defs.SIGN),
        ("q6", lambda x: x in defs.DIGITS)
    ],
    "q5": [
        ("q6", lambda x: x in defs.DIGITS)
    ],
    "q6": [
        ("q6", lambda x: x in defs.DIGITS)
    ]
}
NUMBER_AUTOMATE_INITIAL = "q0"
NUMBER_AUTOMATE_ACCEPTANT = ["q2", "q3", "q6"]

def read_INT_to_EOI():
    return read_full_word(INT_INITIAL, INT_AUTOMATE, INT_AUTOMATE_ACCEPTANT)

def read_FLOAT_to_EOI():
    return read_full_word(FLOAT_AUTOMATE_INITIAL, FLOAT_AUTOMATE, FLOAT_AUTOMATE_ACCEPTANT)


#################################
## Lecture de l'entrée : entiers, nombres, tokens


# Lecture d'un chiffre, puis avancée et renvoi de sa valeur
def read_digit():
    current_char = peek_char1()
    if current_char not in defs.DIGITS:
        raise expected_digit_error(current_char)
    value = eval(current_char)
    consume_char()
    return value


# Lecture d'un entier en renvoyant sa valeur
def read_INT():
    word = read_word(INT_INITIAL, INT_AUTOMATE, INT_AUTOMATE_ACCEPTANT)
    if word :
        return int(word)
    return None


global int_value
global exp_value
global sign_value

# Lecture d'un nombre en renvoyant sa valeur
def read_NUM():
    word = read_word(NUMBER_AUTOMATE_INITIAL, NUMBER_AUTOMATE, NUMBER_AUTOMATE_ACCEPTANT)
    if not word:
        return None
    if "E" in word:
        mantisse, exposant = word.split("E", maxsplit=2)
        return float(mantisse)*(10**(float(exposant)))
    if "e" in word:
        mantisse, exposant = word.split("e", maxsplit=2)
        return float(mantisse)*(10**(float(exposant)))
    return float(word)


# Parse un lexème (sans séparateurs) de l'entrée et renvoie son token.
# Cela consomme tous les caractères du lexème lu.
def read_token_after_separators():
    char = peek_char1();
    if char == defs.PREFIX[defs.V_T.CALC.value]:
        consume_char() # Consommation du '#'
        val = read_INT()
        if val:
            return (defs.V_T.CALC, val)
    elif char in defs.PREFIX:
        consume_char()
        return (defs.TOKEN_MAP.get(char), None)
    else:
        val = read_NUM()
        if val:
            return (defs.V_T.NUM, val)
    return (defs.V_T.END, None) # par défaut, on renvoie la fin de l'entrée


# Donne le prochain token de l'entrée, en sautant les séparateurs éventuels en tête
# et en consommant les caractères du lexème reconnu.
def next_token():
    while peek_char1() in defs.SEP:
        consume_char()
    return read_token_after_separators()


#################################
## Fonctions de tests

def test_INT_to_EOI():
    print("@ Testing read_INT_to_EOI. Type a word to recognize.")
    reinit()
    if read_INT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_FLOAT_to_EOI():
    print("@ Testing read_FLOAT_to_EOI. Type a word to recognize.")
    reinit()
    if read_FLOAT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_lexer():
    print("@ Testing the lexer. Just type tokens and separators on one line")
    reinit()
    token, value = next_token()
    while token != defs.V_T.END:
        print("@", defs.str_attr_token(token, value))
        token, value = next_token()

if __name__ == "__main__":
    ## Choisir une seule ligne à décommenter
    # test_INT_to_EOI()
    # test_FLOAT_to_EOI()
    test_lexer()
