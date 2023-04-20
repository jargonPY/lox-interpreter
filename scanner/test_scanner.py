import pytest
from scanner.scanner import Scanner
from data_types.error_messages import *
from test_utils.build_tokens import BuildTokens
from test_utils.error_reporter import TestErrorReporter


# ! Instead of the fixture context being passed as a parameter just use a regular setup function.
def setup_scanner() -> Scanner:
    return Scanner(TestErrorReporter())


def test_scan_integer_number():
    text = "1234;"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().num(1234).build()
    assert tokens == expected


def test_scan_decimal_number():
    text = "4.124414;"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().num(4.124414).build()
    assert tokens == expected


def test_scan_single_digit_arithmetic_expression():
    text = "2 + 3 * 4 - 5 / 2;"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().num(2).add().num(3).mult().num(4).sub().num(5).div().num(2).build()
    assert tokens == expected


def test_scan_multi_digit_arithmetic_expression():
    text = "2124 + 1344 * 12344 - 414145 / 1412342;"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().num(2124).add().num(1344).mult().num(12344).sub().num(414145).div().num(1412342).build()
    assert tokens == expected


def test_scan_decimal_arithmetic_expression():
    text = "2124.1001 * 12344 - 414145.01 / 1412342;"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().num(2124.1001).mult().num(12344).sub().num(414145.01).div().num(1412342).build()
    assert tokens == expected


def test_scan_string():
    text = '"Today is the day.";'
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().string("Today is the day.").build()
    assert tokens == expected


def test_scan_string_concatenation():
    text = '"For Example: " + "Today is the day.";'
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().string("For Example: ").add().string("Today is the day.").build()
    assert tokens == expected


""" ========================= Test Scanning Single Character Lexemes ========================= """

""" ========================= Test Scanning Single or Double Character Lexemes ========================= """

# todo given the large possible number of inputs, use parameterization tests
def test_scan_negation_operator():
    text = "!variable"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().negate().identifier("variable").build(include_semicolon=False)
    assert tokens == expected


def test_scan_not_equal_operator():
    text = "!=variable"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().not_equal().identifier("variable").build(include_semicolon=False)
    assert tokens == expected


""" ========================= Test Scanning Identifier and Reserved Words ========================= """


def test_scan_single_identifier():
    text = "ifall"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().identifier("ifall").build(include_semicolon=False)
    assert tokens == expected


def test_scan_alpha_numeric_identifier():
    text = "if1234all"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().identifier("if1234all").build(include_semicolon=False)
    assert tokens == expected


# todo implement support for underscores for identifiers
# def test_scan_identifier_with_underscore():
#     text = "if_1234_all"
#     scanner = setup_scanner()

#     tokens = scanner.scan(text)

#     expected = BuildTokens().identifier("if_1234_all").build(include_semicolon=False)
#     assert tokens == expected


def test_scan_single_keyword():
    text = "if"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().keyword("if").build(include_semicolon=False)
    assert tokens == expected


""" ========================= Test Scanning Special Characters ========================= """


""" ========================= Error Reporting Tests ========================= """


def test_scan_unterminated_string():
    text = '"Today is the day.;'
    scanner = setup_scanner()

    scanner.scan(text)

    # * this tests the inner state of 'scanner'
    # todo factor out into helper function so its easy to change
    # todo factor out hardcoded error messages
    assert scanner.error_reporter.message == UNTERMINATED_STRING


def test_scan_single_invalid_character():
    text = "@"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().build(include_semicolon=False)
    assert tokens == expected
    assert scanner.error_reporter.message == INVALID_CHAR


def test_scan_invalid_character_in_expression():
    text = "42 + @"
    scanner = setup_scanner()

    tokens = scanner.scan(text)

    expected = BuildTokens().num(42).add().build(include_semicolon=False)
    assert tokens == expected
    assert scanner.error_reporter.message == INVALID_CHAR
