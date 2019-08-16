import unittest

class TestEvaluatePrimitives(unittest.TestCase):

    def test_is_potential_compound(self):
        from .scheme import is_potential_compound
        exprs = ['', '(a )', '( a']
        targets = [False, True, False]
        for e, t in zip(exprs, targets):
            self.assertEqual(is_potential_compound(e), t)

    def test_is_numeric_literal(self):
        from .scheme import is_numeric_literal
        exprs = ['a', '.', '', '2', '2a', '2.B', '75.603', '3.4.5']
        targets = [False, False, False, True, False, False, True, False]
        for e, t in zip(exprs, targets):
            self.assertEqual(is_numeric_literal(e), t)

    def test_is_string_literal(self):
        from .scheme import is_string_literal
        tests = [('"hello"', True), ('"incomplete', False), 
                ('2', False), ('a', False), ('', False)]
        for inp, out in tests:
            self.assertEqual(is_string_literal(inp), out)

    def test_evaluate_primitive(self):
        from .scheme import evaluate_primitive
        tests = [('23', 23), ('2.3', 2.3), ('"bob"', "bob")]
        for inp, out in tests:
            self.assertEqual(evaluate_primitive(inp), out)

class TestStrip(unittest.TestCase):

    def test_sweep_for(self):
        from .scheme import sweep_for
        expr = "aabdowm"
        i = sweep_for(expr, 'b', 1)
        self.assertEqual(i, 2)
        i = sweep_for(expr, 'a', 1)
        self.assertEqual(i, 0)
        i = sweep_for(expr, 'a', -1)
        self.assertEqual(i, 1)
        i = sweep_for(expr, 'd', -1)
        self.assertEqual(i, 3)

    def test_strip(self):
        from .scheme import strip
        exp = '(+ 2 5)'
        self.assertEqual(strip(exp), '+ 2 5')
        exp = '(( 4 ) )'
        self.assertEqual(strip(exp), '( 4 ) ')
        with self.assertRaises(SyntaxError):
            strip('+ 2 5)')
        with self.assertRaises(SyntaxError):
            strip('(')

class TestParse(unittest.TestCase):

    def test_parse(self):
        from .scheme import parse
        tests = [('', ['']), ('2', ['2']), ('( 2)', ['2']), 
                 ('((3) (4))', ['(3)', '(4)']), 
                 ('( 4 5 5)', ['4', '5', '5']), 
                 ('( define a (+ 3 2))', ['define', 'a', '(+ 3 2)']), 
                 ('(- 4 5)', ['-', '4', '5'])
                 ]
        for exp, words in tests:
            self.assertEqual(parse(exp), words)
        
        bad_expressions = ['(', ')', '()(2']
        for e in bad_expressions:
            with self.assertRaises(SyntaxError):
                print(e,parse(e))
                parse(e)


class TestEvaluate(unittest.TestCase):

    def test_is_valid_variable_name(self):
        from .scheme import is_valid_variable_name
        good_names = ("a", "asd5", "5_a")
        bad_names = ("?", "(a", "define", "+")
        for name in good_names:
            self.assertTrue(is_valid_variable_name(name))
        for name in bad_names:
            self.assertFalse(is_valid_variable_name(name))
        

    def test_evaluate_primitive(self):
        from .scheme import evaluate_simple
        env = {"jim": 4}
        tests = [('', None), ('2', 2), ('"bob"', "bob"), 
                ("jim", 4)]
        for input, output in tests:
            self.assertEqual(evaluate_simple(input, env), output)

    def test_evaluate_words(self):
        from .scheme import evaluate_words
        from .scheme import define
        env = {"a" : 3}
        tests = [("(2)", [2]), 
                  ("((2) (3))", [2, 3] ), 
                  ("( 1 (2) 4)", [1, 2, 4] ),
                  ('(a)', [3]), 
                  ]
        for expr, res in tests:
            self.assertEqual(evaluate_words(expr, env), res)

    def test_evaluate(self):
        from .scheme import evaluate
        env = {"a" : 3}
        tests = [("(2)", 2), 
                  ("(+ 2 3)", 5), 
                  ("(- 1 4)", -3), 
                  ("( + 1 (+ 3 (4)))", 8), 
                  ("(+ a 5)", 8)]

        for expr, res in tests:
            self.assertEqual(evaluate(expr, env), res)

        r = evaluate("(define b 5)", env)
        self.assertEqual(r, 5)
        r = evaluate("(b)", env)
        self.assertEqual(r, 5)

        __ = evaluate("(define a 7)", env)
        r = evaluate("(+ a b)", env)
        self.assertEqual(r, 12)

if __name__ == "__main__":
    unittest.main()