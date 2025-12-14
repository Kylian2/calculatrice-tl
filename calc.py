#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : parser - requires Python version >= 3.10
"""
import math
import sys
from math import factorial

from lexer import next_token

assert sys.version_info >= (3, 10), "Use Python 3.10 or newer !"

import lexer
from definitions import V_T, str_attr_token

#####
# Variables internes (à ne pas utiliser directement)

_current_token = V_T.END
_value = None  # attribut du token renvoyé par le lexer

#####
# Fonctions génériques

class ParserError(Exception):
    pass

def unexpected_token(expected):
    return ParserError("Found token '" + str_attr_token(_current_token, _value) + "' but expected " + expected)

def get_current():
    return _current_token

def get_value():
    return _value

def init_parser(stream):
    global _current_token, _value
    lexer.reinit(stream)
    _current_token, _value = lexer.next_token()
    # print("@ init parser on",  repr(str_attr_token(_current, _value)))  # for DEBUGGING

def consume_token(tok):
    # Vérifie que le prochain token est tok ;
    # si oui, le consomme et renvoie son attribut ; si non, lève une exception
    global _current_token, _value
    if _current_token != tok:
        raise unexpected_token(tok.name)
    if _current_token != V_T.END:
        old = _value
        _current_token, _value = lexer.next_token()
        return old

#########################
## Définition des méthodes de parsing pour les non terminaux

def parse_exp5(l):
    tok = get_current()
    if tok in [V_T.SUB, V_T.OPAR, V_T.NUM, V_T.CALC]:
        n_1 = parse_exp4(l)
        n = parse_exp5_p(l, n_1)
        return n
    else:
        raise ParserError("Impossible de parser dans parse_exp5")

def parse_exp5_p(l, n_1):
    tok = get_current()
    if tok  == V_T.ADD:
        consume_token(V_T.ADD)
        n_0 = parse_exp4(l)
        n = parse_exp5_p(l, n_1 + n_0)
        return n
    elif tok == V_T.SUB:
        consume_token(V_T.SUB)
        n_0 = parse_exp4(l)
        n = parse_exp5_p(l, n_1 - n_0)
        return n
    elif tok in [V_T.CPAR, V_T.SEQ]:
        return n_1
    else:
        raise ParserError("Impossible de parser dans parse_exp5_p")

def parse_exp4(l):
    tok = get_current()
    if tok in [V_T.SUB, V_T.OPAR, V_T.NUM, V_T.CALC]:
        n_1 = parse_exp3(l)
        n = parse_exp4_p(l, n_1)
        return n
    else:
        raise ParserError("Impossible de parser dans parse_exp4")

def parse_exp4_p(l, n_1):
    tok = get_current()
    if tok == V_T.MUL:
        consume_token(V_T.MUL)
        n_0 = parse_exp3(l)
        n = parse_exp4_p(l, n_1 * n_0)
        return n
    elif tok == V_T.DIV:
        consume_token(V_T.DIV)
        n_0 = parse_exp3(l)
        n = parse_exp4_p(l, n_1 / n_0)
        return n
    elif tok in [V_T.ADD, V_T.SUB, V_T.CPAR, V_T.SEQ]:
        return n_1
    else:
        raise ParserError("Impossible de parser dans parse_exp4_p")

def parse_exp3(l):
    tok = get_current()
    if tok == V_T.SUB:
        consume_token(V_T.SUB)
        n_0 = parse_exp3(l)
        return -n_0
    elif tok in [V_T.OPAR, V_T.NUM, V_T.CALC]:
        n_0 = parse_exp2(l)
        return n_0
    else:
        raise ParserError("Impossible de parser dans parse3")

def parse_exp2(l):
    tok = get_current()
    if tok in [ V_T.OPAR, V_T.NUM, V_T.CALC]:
        n_1 = parse_exp1(l)
        n = parse_exp2_p(l, n_1)
        return n
    else:
        raise ParserError("Impossible de parser dans parse_exp2")

def parse_exp2_p(l, n_1):
    tok = get_current()
    if tok == V_T.FACT:
        consume_token(V_T.FACT)
        n = parse_exp2_p(l, math.factorial(int(n_1)))
        return n
    elif tok in [V_T.MUL, V_T.DIV, V_T.ADD, V_T.SUB, V_T.CPAR, V_T.SEQ]:
        return n_1
    else:
        raise ParserError("Impossible de parser dans parse_exp2_p")

def parse_exp1(l):
    tok = get_current()
    if tok in [V_T.OPAR, V_T.NUM, V_T.CALC]:
        n_1 = parse_exp0(l)
        n = parse_exp1_p(l, n_1)
        return n
    else:
        raise ParserError("Impossible de parser dans parse_exp1")

def parse_exp1_p(l, n_1):
    tok = get_current()
    if tok == V_T.POW:
        consume_token(V_T.POW)
        n_2 = parse_exp1(l)
        return math.pow(n_1, n_2)
    elif tok in [V_T.FACT, V_T.MUL, V_T.DIV, V_T.ADD, V_T.SUB, V_T.CPAR, V_T.SEQ]:
        return n_1
    else:
        raise ParserError("Impossible de parser dans parse_exp1_p")

def parse_exp0(l):
    tok = get_current()
    if tok == V_T.OPAR:
        consume_token(V_T.OPAR)
        n = parse_exp5(l)
        consume_token(V_T.CPAR)
        return n
    elif tok == V_T.NUM:
        val = consume_token(V_T.NUM)
        return val
    elif tok == V_T.CALC:
        i = consume_token(V_T.CALC)
        if not i:
            raise ParserError("Erreur dans parse_exp0: i n'a pas de valeur")
        return l[i-1]
    else:
        raise ParserError("Impossible de parser dans parse_exp0")

#########################
## Parsing de input

def parse_input_p(l):
    tok = get_current()
    if tok in [V_T.SUB, V_T.OPAR, V_T.NUM, V_T.CALC]:
        n = parse_exp5(l)
        consume_token(V_T.SEQ)
        l_0 = parse_input_p(l + [n])
        return l_0
    elif tok == V_T.END:
        return l
    else:
        raise ParserError("Impossible de parser dans parse_input")

def parse_input():
    tok = get_current()
    if tok in [V_T.SUB, V_T.OPAR, V_T.NUM, V_T.CALC, V_T.END]:
        l = parse_input_p([])
        return l
    else:
        raise ParserError("Impossible de parser dans parse_input")

#####################################
## Fonction principale de la calculatrice
## Appelle l'analyseur grammatical et retourne
## - None sans les attributs
## - la liste des valeurs des calculs avec les attributs

def parse(stream=sys.stdin):
    init_parser(stream)
    l = parse_input()
    consume_token(V_T.END)
    return l

#####################################
## Test depuis la ligne de commande

def test_manuel():
    print("@ Testing the calculator in infix syntax.")

    result = parse()
    print(result)
    if result is None:
        print("@ Input OK ")
    else:
        print("@ result = ", repr(result))
    return

if __name__ == "__main__":
    test_manuel()
