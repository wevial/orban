import unittest
from orban import Orban

class TestRegexSyntax(unittest.TestCase):

    def test_unbalanced_parenthesis(self):
        O = Orban()
        self.assertFalse(O.regex_syntax("((a("))
        self.assertFalse(O.regex_syntax(")a))"))
        self.assertFalse(O.regex_syntax("(a))"))
        self.assertFalse(O.regex_syntax("((a)"))
        self.assertTrue(O.regex_syntax("(a)"))

    def test_kleene_op(self):
        O = Orban()
        self.assertFalse(O.regex_syntax("*"))
        self.assertFalse(O.regex_syntax("()*"))
        self.assertTrue(O.regex_syntax("a*"))

    def test_plus_op(self):
        O = Orban()
        self.assertFalse(O.regex_syntax("+"))
        self.assertFalse(O.regex_syntax("()+"))
        self.assertTrue(O.regex_syntax("a+"))

    def test_union_op(self):
        O = Orban()
        self.assertFalse(O.regex_syntax("|"))
        self.assertFalse(O.regex_syntax("()|"))
        self.assertFalse(O.regex_syntax("(|)"))
        self.assertTrue(O.regex_syntax("a|b"))

    def test_questionmark_op(self):
        O = Orban()
        self.assertFalse(O.regex_syntax("?"))
        self.assertFalse(O.regex_syntax("()?"))
        self.assertTrue(O.regex_syntax("a?"))

if __name__ == '__main__':
    unittest.main()
