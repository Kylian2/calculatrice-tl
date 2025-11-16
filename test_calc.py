#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test the calculator in infix syntax
"""

import io
import definitions as defs
from calc import parse, ParserError

PARSER_NAME = 'calc'
PARSER_UNDER_TEST = parse

#################################
## Fonctions génériques de test

def run(string):
    stream = io.StringIO(string)
    try:
        return PARSER_UNDER_TEST(io.StringIO(string+defs.EOI))
    except Exception as e:
        stream.close()
        raise e

def test_result(calc_input, expected):
    print("@ test {0} on input:".format(PARSER_NAME), repr(calc_input))
    print("@ result expected:", repr(expected))
    found = run(calc_input)
    assert found == expected, "found {0} vs {1} expected".format(found, expected)
    print("@ => OK")
    print()

def test_parsing_error(calc_input):
    print("@ test {0} on input:".format(PARSER_NAME), repr(calc_input))
    print("@ parsing error expected")
    try:
        result=run(calc_input)
        print("@ unexpected result:", result)
        assert False
    except ParserError as e:
        print("@ parsing error found:", e)
        pass
    print("@ => OK")
    print()


#################################
## Fonctions génériques de test

# Exemples basiques
test_result("  \n \n  ",[])
test_result("7;",[7])
test_result("123+321;",[444])
test_result("1-2;",[-1])
test_result("12*3;",[36])
test_result("12/3;",[4])
test_result("12^3;",[1728])
test_result("5!;",[120])

test_result("3 * 4 + 1 - 3 ; #1 * (#1 / 2) ;", [10, 50])
test_result("1 + 2 * 3 ; -4 + #1 * #1 ;", [7, 45])
test_result("2*3 + 1 ; #1 * #1 - 4 ;", [7, 45])
test_result("1 - 1 - 1 ; 1 - (1 - 1) ;", [-1, 1])
test_result("1 - - 1 - 1 ; 1 - (-1 - 1) ; 1 - -(1 - 1) ;", [1, 3, 1])
test_result("60 / 10 / 2 ; 60 / (10 / 2) ;", [3, 12])
test_result("- ((1 + 2) * - ((3 - 5))) ; ", [-6])
test_result("2^1^3^2;",[2])
test_result("(2^1)^3^2;",[512])

# Tests autour de n*(n+1)/2
N1 = 20
test_result("1;" + "".join(["{0}+#{1};".format(i,i-1) for i in range(2,N1)]),
            [i * (i+1)//2 for i in range(1,N1)])

r = [i for i in range(1,N1)]
r.append((N1-1)*N1//2)
l = [str(i)+";" for i in range(1,N1)]
for i in range(1, N1-1):
    l.append("#{0}+".format(i))
l.append("#{0};".format(N1-1))
test_result("".join(l), r)

# Tests de k parmi n
k_parmi_n="#2-#1;#1!;#2!;#3!;#5/#4/#6;"
test_result("1;2;"+k_parmi_n, [1, 2, 1, 1, 2, 1, 2])
test_result("1;3;"+k_parmi_n, [1, 3, 2, 1, 6, 2, 3])
test_result("2;3;"+k_parmi_n, [2, 3, 1, 2, 6, 1, 3])
test_result("1;4;"+k_parmi_n, [1, 4, 3, 1, 24, 6, 4])
test_result("2;4;"+k_parmi_n, [2, 4, 2, 2, 24, 2, 6])
test_result("3;6;"+k_parmi_n, [3, 6, 3, 6, 720, 6, 20])

# Tests avec erreurs
test_parsing_error(";")
test_parsing_error("123+321")
test_parsing_error("123+321; 1")
test_parsing_error("3 * 4 + 1 - 3 ; #1 (#1 / 2) ;")
test_parsing_error("3 * / 1 - 3 ; #1 * (#1 / 2) ;")
test_parsing_error("3 * 4 + 1 - 3 #1 * (#1 / 2) ;")
test_parsing_error("(1 2 ;")
test_parsing_error("- ((1 + 2 * - ((3 - 5))) ; ")
test_parsing_error("- (1 + 2)) * - ((3 - 5)) ; ")
test_parsing_error("!5;")
test_parsing_error("5! / ;")
