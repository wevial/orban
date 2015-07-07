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
        self.assertEqual(O.insert_concat("a(bb)+a"), "a.(b.b)+.a")
        self.assertEqual(O.insert_concat("a(b|c)*d"), "a.(b|c)*.d")

    def test_infix_to_postfix(self):
        O = Orban()
        self.assertEqual(O.infix_to_postfix("a*"), "a*")
        self.assertEqual(O.infix_to_postfix("a|b"), "ab|")
        self.assertEqual(O.infix_to_postfix("a.(b|c)*.d"), "abc|*.d.")
        self.assertEqual(O.infix_to_postfix("a.(b.b)+.a"), "abb.+.a.")

    def test_insert_concat_to_postfix(self):
        O = Orban()
        regex = 'a(b|c)*d'
        syntax = O.insert_concat(regex)
        self.assertEqual(syntax, 'a.(b|c)*.d')
        self.assertEqual(O.infix_to_postfix(syntax), 'abc|*.d.')

if __name__ == '__main__':
    unittest.main()
