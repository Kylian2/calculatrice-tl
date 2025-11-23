#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : parser - requires Python version >= 3.10
"""

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

def parse_exp5():
    tok = get_current()
    if tok in [V_T.SUB, V_T.OPAR, V_T.NUM, V_T.CALC]:
        parse_exp4()
        parse_exp5_p()
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp5")

def parse_exp5_p():
    tok = get_current()
    if tok  == V_T.ADD:
        consume_token(V_T.ADD)
        parse_exp4()
        parse_exp5_p()
        return
    elif tok == V_T.SUB:
        consume_token(V_T.SUB)
        parse_exp4()
        parse_exp5_p()
        return
    elif tok in [V_T.CPAR, V_T.SEQ]:
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp5_p")

def parse_exp4():
    tok = get_current()
    if tok in [V_T.SUB, V_T.OPAR, V_T.NUM, V_T.CALC]:
        parse_exp3()
        parse_exp4_p()
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp4")

def parse_exp4_p():
    tok = get_current()
    if tok == V_T.MUL:
        consume_token(V_T.MUL)
        parse_exp3()
        parse_exp4_p()
        return
    elif tok == V_T.DIV:
        consume_token(V_T.DIV)
        parse_exp3()
        parse_exp4_p()
        return
    elif tok in [V_T.ADD, V_T.SUB, V_T.CPAR, V_T.SEQ]:
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp4_p")

def parse_exp3():
    tok = get_current()
    if tok == V_T.SUB:
        consume_token(V_T.SUB)
        parse_exp3()
        return
    elif tok in [V_T.OPAR, V_T.NUM, V_T.CALC]:
        parse_exp2()
        return
    else:
        raise ParserError("Impossible de parser dans parse3")

def parse_exp2():
    tok = get_current()
    if tok in [ V_T.OPAR, V_T.NUM, V_T.CALC]:
        parse_exp1()
        parse_exp2_p()
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp2")

def parse_exp2_p():
    tok = get_current()
    if tok == V_T.FACT:
        consume_token(V_T.FACT)
        parse_exp2_p()
        return
    elif tok in [V_T.MUL, V_T.DIV, V_T.ADD, V_T.SUB, V_T.CPAR, V_T.SEQ]:
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp2_p")

def parse_exp1():
    tok = get_current()
    if tok in [V_T.OPAR, V_T.NUM, V_T.CALC]:
        parse_exp0()
        parse_exp1_p()
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp1")

def parse_exp1_p():
    tok = get_current()
    if tok == V_T.POW:
        consume_token(V_T.POW)
        parse_exp1()
        return
    elif tok in [V_T.FACT, V_T.MUL, V_T.DIV, V_T.ADD, V_T.SUB, V_T.CPAR, V_T.SEQ]:
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp1_p")

def parse_exp0():
    tok = get_current()
    if tok == V_T.OPAR:
        consume_token(V_T.OPAR)
        parse_exp5()
        consume_token(V_T.CPAR)
        return
    elif tok == V_T.NUM:
        consume_token(V_T.NUM)
        return
    elif tok == V_T.CALC:
        consume_token(V_T.CALC)
        return
    else:
        raise ParserError("Impossible de parser dans parse_exp0")

#########################
## Parsing de input et exp

def parse_input():
    tok = get_current()
    if tok in [V_T.SUB, V_T.OPAR, V_T.NUM, V_T.CALC]:
        parse_exp5()
        consume_token(V_T.SEQ)
        parse_input()
        return
    elif tok == V_T.END:
        return
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
    if result is None:
        print("@ Input OK ")
    else:
        print("@ result = ", repr(result))
    return

if __name__ == "__main__":
    test_manuel()
