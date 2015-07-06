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

    def test_concat_single_char_nonop(self):
        O = Orban()
        self.assertEqual(O.insert_concat("a"), "a")

    def test_concat_between_chars_nonop(self):
        O = Orban()
        self.assertEqual(O.insert_concat("ab"), "a.b")

    def test_concat_with_ops(self):
        O = Orban()
        self.assertEqual(O.insert_concat("a*"), "a*")
        self.assertEqual(O.insert_concat("aa*"), "a.a*")
        self.assertEqual(O.insert_concat("a(a)*"), "a.(a)*")


if __name__ == '__main__':
    unittest.main()
