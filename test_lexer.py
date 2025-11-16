#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du lexer du projet de TL
"""

import io
import math
import definitions as defs
import lexer

# Prints each test
verbose_test = True

# Stop testing on the first encountered error
stop_on_first_error = True

# Le caractère de fin est $, et non \n
defs.EOI = '$'
defs.PREFIX = ('', '+', '-', '*', '/', '^', '!', '(', ')', '#', ';', defs.EOI)
assert len(defs.V_T)==len(defs.PREFIX)
defs.TOKEN_MAP = { defs.PREFIX[t.value]: t  for t in defs.V_T }


# DRIVERS de tests avec et sans valeur calculée

def test(input_descr, expr, msg):
    """Perform a test.
       Raise an exception if it fails and stop_on_first_error == True"""
    if stop_on_first_error:
        #assert expr, msg
        if not expr:
            print(msg)
            exit(1)
    else:
        if verbose_test:
            print(input_descr)
        if not expr:
            print(msg)
    return

def test_single_wo_val(function_to_test, expected_result, test_input):
    """function_to_test = name of the function to test
       expected_result = True or False or None (where None means LexerError expected)
       test_input = string in input"""
    input_descr = "@ " + repr(function_to_test) + " on " + repr(test_input) + " expect: " + repr(expected_result)
    if verbose_test:
        print(input_descr)
    try:
        lexer.reinit(io.StringIO(test_input+defs.EOI))
        found_result = eval(function_to_test+"()")
        test(input_descr, expected_result != None, "an exception is expected instead of normally returning " + repr(found_result))
        test(input_descr, expected_result == found_result, "found " + repr(found_result))
    except lexer.LexerError as e:
        test(input_descr, expected_result == None, "unexpected " + repr(e))
    except TypeError as e:
        if not stop_on_first_error:
            print("Type error for " + repr(function_to_test)+"("+test_input+"): " + repr(e))
        else:
            raise e from None
    except Exception as exn:
        if not stop_on_first_error:
            print(input_descr)
            print("ERROR: uncaught exception " + repr(exn))
        else:
            raise exn from None

def test_all_wo_val(function_to_test, expected_result, test_inputs):
    for i in test_inputs:
        test_single_wo_val(function_to_test, expected_result, i)
    print("@---- ", function_to_test, "=>", expected_result, " PASSED!")
    print()

def float_eq(n1, n2, precision=10**-10):
    return abs(n1 - n2) <= abs(precision*n1)

def test_single(function_to_test, test_input, expected_result="aucun"):
    """function_to_test = name of the function to test
       expected_result = value or None (where None means LexerError expected)
       test_input = string in input"""
    if expected_result == "aucun":
        expected_result=float(test_input)
    input_descr = "@ " + repr(function_to_test) + " on " + repr(test_input) + " expect: " +  repr(expected_result)
    if verbose_test:
        print(input_descr)
    if isinstance(expected_result, float):
        assert math.isfinite(expected_result),\
            ("please remove this irrelevant test ('{0}' is float '{1}' which is not finite)".format(test_input, expected_result))
    try:
        lexer.reinit(io.StringIO(test_input+defs.EOI))
        result = eval(function_to_test+"()")
        if expected_result is None:
            test(input_descr,
                 result is None,
                 "an exception is expected instead of normally return " + repr(result))
        else:
            test(input_descr,
                 float_eq(float(result), expected_result),
                 "found " + repr(result))
    except lexer.LexerError as e:
        test(input_descr, expected_result == None, "unexpected " + repr(e))
    except TypeError as e:
        if not stop_on_first_error:
            print("Type error for " + repr(function_to_test)+"("+test_input+"): " + repr(e))
        else:
            raise e from None
            result = eval(function_to_test+"()")
    except Exception as exn:
        if not stop_on_first_error:
            print(input_descr)
            print("ERROR: uncaught exception " + repr(exn))
        else:
            raise exn from None

def test_all_ok(function_to_test, test_inputs):
    print("@---- ", function_to_test)
    for i in test_inputs:
        test_single(function_to_test, i)
    print()

def test_all_w_result(function_to_test, test_inputs):
    print("@---- ", function_to_test)
    for (i, v) in test_inputs:
        test_single(function_to_test, i, v)
    print()

def test_token_sequence_ok(function_to_test, test_input, expected_results):
    input_descr = "@ " + repr(function_to_test) + " on " + repr(test_input) + " expect: " +  repr(expected_results)
    if verbose_test:
        print(input_descr)
    try:
        lexer.reinit(io.StringIO(test_input+defs.EOI))
        for expected_result in expected_results:
            found_result = eval(function_to_test+"()")
            test(input_descr,
                 expected_result[0] == found_result[0] and
                   (float_eq(float(found_result[1]), expected_result[1])
                      if isinstance(expected_result[1], float) else
                    found_result[1] == expected_result[1]),
                 "found " + repr(found_result) + " instead of " + repr(expected_result))
    except Exception as exn:
        if not stop_on_first_error:
            print(input_descr)
            print("ERROR: uncaught exception " + repr(exn))
        else:
            raise exn from None

def test_all_token_sequence_ok(function_to_test, test_inputs):
    print("@---- ", function_to_test)
    for (i, r) in test_inputs:
        test_token_sequence_ok(function_to_test, i, r)
    print("("+str(len(test_inputs))+" tests in total)")




# Les tests proprement dits.

# D'abord, sans valeurs
def exec_test_INT_to_EOI():
    test_all_wo_val("lexer.read_INT_to_EOI", True,
                    ["1234567890098700", "203", "0000",
                     "0", "1","2","3","4","5","6","7","8","9"])
    test_all_wo_val("lexer.read_INT_to_EOI", False,
                    ["","123e","000e","2.5",".5","0.0","3.", "1e5", "2e+5", "1e-5", "-25"])
    test_all_wo_val("lexer.read_INT_to_EOI", None, ["a2","0a0","1a0"])

def exec_test_FLOAT_to_EOI():
    test_all_wo_val("lexer.read_FLOAT_to_EOI", True,
                    ["4.", "5.4", ".5", "0123.", ".123", "678.876",
                     "0.", "000.000", ".0"])
    test_all_wo_val("lexer.read_FLOAT_to_EOI", False,
                    ["123", "0", "1", ".", ".123e5", "1.e+5", "2e5", "1.5e+6", "",
                     "-.5"])
    test_all_wo_val("lexer.read_FLOAT_to_EOI", None, ["1.a2","0.a0","1a."])

# Ensuite, avec valeurs
def exec_test_INT():
    test_all_ok("lexer.read_INT",
                ["1234567890098700", "203", "0000",
                 "0", "1","2","3","4","5","6","7","8","9"])
    test_all_w_result("lexer.read_INT",
                      [("01", 1),
                       ("123e", 123),
                       ("000e", 0),
                       ("2.5", 2),
                       ("0.0", 0),
                       ("3.", 3),
                       ("1e5", 1),
                       ("2e+5", 2),
                       ("1e-5", 1),
                       ("", None),
                       (".5", None),
                       ("-25", None),
                       ("a2", None),
                       ("0a0", None),
                       ("1a0", None)])

def exec_test_NUM():
    test_all_ok("lexer.read_NUM",
                ["1.5e+2", "1234567890098700", "203", "0000",
                 "0", "1","2","3","4","5","6","7","8","9",
                 "4.", "5.4", ".5", "0123.", ".123", "678.876",
                 "0.", "000.000", ".0",
                 "1e5", "1e+5", "1e-5", "1234567890098700e-1234567890098700",
                 "1234567890098700e123",
                 "203E203", "000e+125", "0e-3", "1E+4","2e0","3E0","4e6",
                 "5e-5","6e7","7e8","8E+9","9e-1", "4.e+43", "5.4E-67",
                 ".5e0", ".3e5", "0123.e-0", ".123E+0", "678.876E-0", "0.e+124",
                 "000.000E+12", ".0e-98500"])
    test_all_w_result("lexer.read_NUM",
                      [("1ee5", 1),
                       ("1e-", 1),
                       ("2.E+", 2.),
                       ("1e", 1),
                       ("1e+-5", 1),
                       ("1e+", 1),
                       ("e", None),
                       ("+", None),
                       ("-", None),
                       ("e5", None),
                       ("e+5", None),
                       ("+1e5", None),
                       ("-1e5", None),
                       (".e5", None),
                       ("", None),
                       ("a2", None),
                       ("0a0", None),
                       ("1a0", None),
                       ("1.a2", None),
                       ("0.a0", None),
                       ("1a.", None),
                       ("2e+a0", None),
                       ("1e1a0", None)])

def exec_test_next_token():
    test_all_token_sequence_ok("lexer.next_token", [
        ("1 2.0 3e-1 .4", [
            (defs.V_T.NUM, 1),
            (defs.V_T.NUM, 2.0),
            (defs.V_T.NUM, 3e-1),
            (defs.V_T.NUM, .4),
            (defs.V_T.END, None)
         ]),
        ("1 + 2^3! / (4*5-6)", [
            (defs.V_T.NUM,  1),
            (defs.V_T.ADD,  None),
            (defs.V_T.NUM,  2),
            (defs.V_T.POW,  None),
            (defs.V_T.NUM,  3),
            (defs.V_T.FACT, None),
            (defs.V_T.DIV,  None),
            (defs.V_T.OPAR, None),
            (defs.V_T.NUM,  4),
            (defs.V_T.MUL,  None),
            (defs.V_T.NUM,  5),
            (defs.V_T.SUB,  None),
            (defs.V_T.NUM,  6),
            (defs.V_T.CPAR, None),
            (defs.V_T.END,  None)
         ])
    ])

# Si ce fichier est lancé directement, on exécute les tests
if __name__ == '__main__':
    exec_test_INT_to_EOI()
    exec_test_FLOAT_to_EOI()
    exec_test_INT()
    exec_test_NUM()
    exec_test_next_token()
    print("\n@ all tests OK !")
