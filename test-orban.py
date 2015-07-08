import unittest
import orban as O

class TestRegexSyntax(unittest.TestCase):

    def test_unbalanced_parenthesis(self):
        self.assertFalse(O.check_syntax("((a("))
        self.assertFalse(O.check_syntax(")a))"))
        self.assertFalse(O.check_syntax("(a))"))
        self.assertFalse(O.check_syntax("((a)"))
        self.assertTrue(O.check_syntax("(a)"))

    def test_kleene_op(self):
        self.assertFalse(O.check_syntax("*"))
        self.assertFalse(O.check_syntax("()*"))
        self.assertTrue(O.check_syntax("a*"))

    def test_plus_op(self):
        self.assertFalse(O.check_syntax("+"))
        self.assertFalse(O.check_syntax("()+"))
        self.assertTrue(O.check_syntax("a+"))

    def test_union_op(self):
        self.assertFalse(O.check_syntax("|"))
        self.assertFalse(O.check_syntax("()|"))
        self.assertFalse(O.check_syntax("(|)"))
        self.assertTrue(O.check_syntax("a|b"))
        self.assertTrue(O.check_syntax("(aa)|b"))

    def test_questionmark_op(self):
        self.assertFalse(O.check_syntax("?"))
        self.assertFalse(O.check_syntax("()?"))
        self.assertTrue(O.check_syntax("a?"))

    def test_concat_single_char_nonop(self):
        self.assertEqual(O.add_concat("a"), "a")

    def test_concat_between_chars_nonop(self):
        self.assertEqual(O.add_concat("ab"), "a.b")

    def test_concat_with_ops(self):
        self.assertEqual(O.add_concat("a*"), "a*")
        self.assertEqual(O.add_concat("aa*"), "a.a*")
        self.assertEqual(O.add_concat("a(a)*"), "a.(a)*")
        self.assertEqual(O.add_concat("a(bb)+a"), "a.(b.b)+.a")
        self.assertEqual(O.add_concat("a(b|c)*d"), "a.(b|c)*.d")

    def test_infix_to_postfix(self):
        self.assertEqual(O.infix_to_postfix("a*"), "a*")
        self.assertEqual(O.infix_to_postfix("a|b"), "ab|")
        self.assertEqual(O.infix_to_postfix("a.(b|c)*.d"), "abc|*.d.")
        self.assertEqual(O.infix_to_postfix("a.(b.b)+.a"), "abb.+.a.")

    def test_add_concat_to_postfix(self):
        regex = 'a(b|c)*d'
        syntax = O.add_concat(regex)
        self.assertEqual(syntax, 'a.(b|c)*.d')
        self.assertEqual(O.infix_to_postfix(syntax), 'abc|*.d.')

class TestRegexSimulation(unittest.TestCase):
    def test_single_character(self):
        nfa = O.to_nfa(O.re_to_tree('a'))
        self.assertTrue(O.simulate(nfa, 'a'))
        self.assertFalse(O.simulate(nfa, ''))
        self.assertFalse(O.simulate(nfa, 'aa'))
        self.assertFalse(O.simulate(nfa, 'ab'))

    def test_empty_string(self):
        nfa1 = O.to_nfa(O.re_to_tree('a*'))
        nfa2 = O.to_nfa(O.re_to_tree('a'))
        self.assertTrue(O.simulate(nfa1, ''))
        self.assertFalse(O.simulate(nfa2, ''))

    def test_kleene_op(self):
        nfa = O.to_nfa(O.re_to_tree('a*'))
        self.assertTrue(O.simulate(nfa, ''))
        self.assertTrue(O.simulate(nfa, 'a'))
        self.assertTrue(O.simulate(nfa, 'aa'))
        self.assertTrue(O.simulate(nfa, 'aaaaaaaaa'))
        self.assertFalse(O.simulate(nfa, 'aaaaabbbbaaaa'))
        self.assertFalse(O.simulate(nfa, 'bbba'))
                


if __name__ == '__main__':
    unittest.main()





