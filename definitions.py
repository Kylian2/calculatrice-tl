#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : définition des caractères et tokens
"""

import enum
import sys
assert sys.version_info >= (3, 10), "Use Python 3.10 or newer !"


INPUT_STREAM = sys.stdin # où lire les caractères d'entrée


#######################################
# Definition des caractères d'entrées

EOI = '\n' # ATTENTION: certains tests peuvent modifier la valeur de EOI
SEP = {' ', '\n', '\t'} - set(EOI)

DIGITS = frozenset(repr(digit) for digit in range(10))

V_C = set(tuple(DIGITS) + ('.', 'e', 'E', '+', '-', '*', '/', '^', '!', '(', ')', '#', ';'))
V = set(tuple(V_C) + (EOI,) + tuple(SEP))


#########################
# Definition des tokens

V_T = enum.Enum('Token', ['NUM', 'ADD', 'SUB', 'MUL', 'DIV', 'POW', 'FACT',
                          'OPAR', 'CPAR', 'CALC', 'SEQ', 'END'], start=0)

# Les premiers caractères de chaque token (excepté NUM)
PREFIX = ('', '+', '-', '*', '/', '^', '!', '(', ')', '#', ';', EOI)

assert len(V_T)==len(PREFIX)

# Un dictionnaire faisant le lien entre un caractère et le token dont il est préfixe, sauf pour NUM
TOKEN_MAP = { PREFIX[t.value]: t  for t in V_T }

#######
# Affichage d'un token avec attribut éventuel

def str_attr_token(tok:V_T, attr):
    s = tok.name
    match tok:
        case V_T.NUM:
            assert isinstance(attr, int) or isinstance(attr, float)
            s += ":" + str(attr)
        case V_T.CALC:
            assert isinstance(attr, int) and attr >= 0
            s += ":" + str(attr)
        case _:
            assert attr is None
    return s
