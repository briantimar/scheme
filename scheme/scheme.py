import re

class Lambda:
    """ represents a lambda function """
    
    def __init__(self, args, expression):
        """ `args`: a list of arguments to the function. Each is a string
            `expression`: a valid scheme expression which defines the action of the function. eg `(+ x 2)` """
        self.args = args
        self.expression = expression

    def evaluate(self, arg_values, env):
        """ Evaluates the function at the argument values provided, in the environment provided. 
            `env`: the parent environment
            `arg_values`: list of argument values.
        """
        if len(arg_values) != len(self.args):
            raise ValueError(f"Expected {len(self.args)} args, received {len(arg_values)}")
        args_to_values = { arg: val for arg, val in zip(self.args, arg_values)}
        # build a local environment
        local_env = {**env}
        local_env.update(args_to_values)
        return evaluate(self.expression, local_env)

    def __call__(self, arg_values, env):
        return self.evaluate(arg_values, env)

def sweep_for(expression, seeking, incr):
    """ Sweeps the expression searching for the given char.
        `expression`: a string
        `seeking`: target character
        incr: +1 or -1, which way to step through the expression.

        Returns: index of the first instance of char if found; if not found, raises ValueError

        """
    if incr == 1:
        return expression.index(seeking)
    elif incr == -1:
        return len(expression) - 1 - expression[::-1].index(seeking)
    raise ValueError

def strip(expression):
    """Removes the outermost parentheses."""
    try:
        i_open = sweep_for(expression, '(', +1)
    except ValueError:
        raise SyntaxError("Expecting (")
    try:
        i_close = sweep_for(expression, ')', -1)
    except ValueError:
        raise SyntaxError("Expecting )")
    return expression[i_open+1:i_close]

def is_potential_compound(exp):
    return '(' in exp and ')' in exp

def is_numeric_literal(expression):
    if len(expression) == 0:
        return False
    if re.match(r"[^.0-9]", expression):
        return False
    if re.match(r"^\s*\.\s*$", expression):
        return False
    if re.match(r"^\s*\d*(\.)?\d*\s*$", expression):
        return True
    return False

def add(args, env):
    return sum(args)
def sub(args, env):
    return args[0] - sum(args[1:])
def mul(args, env):
    p = 1
    for a in args:
        p *= a
    return p

def define(args, env):
    name, val = args
    env[name] = val
    return val

BUILTIN_OPS = {'+': add, 
               '-': sub, 
               '*': mul,
               'define': define}

def is_builtin(exp):
    return exp in BUILTIN_OPS.keys()

def get_builtin(exp):
    return BUILTIN_OPS[exp]

def is_string_literal(expression):
    if len(expression) < 2:
        return False
    return expression[0] == '"' and expression[-1] == '"'

def is_primitive(expression):
    return is_numeric_literal(expression) or is_string_literal(expression) or len(expression) == 0

def is_function(obj):
    return hasattr(obj, "__call__")

def evaluate_numeric_literal(exp):
    if '.' in exp:
        return float(exp)
    return int(exp)

def evaluate_string_literal(exp):
    return exp[1:-1]

def evaluate_primitive(expression):
    """ Evaluates a primitive expression:
        numeric literal
        string literal
        variable name
    """
    if len(expression) == 0:
        return None
    if is_numeric_literal(expression):
        return evaluate_numeric_literal(expression)
    elif is_string_literal(expression):
        return evaluate_string_literal(expression)
    raise SyntaxError(f"Invalid primitive expression: {expression}")

def lookup_variable(exp, env):
    """ Look up the value variable <exp> is bound to. 
        If not present, raise SyntaxError"""
    try:
        return env[exp]
    except KeyError:
        raise SyntaxError(f"Name {exp} is not defined!")

def check_simple(expression):
    if '(' in expression or ')' in expression:
        raise SyntaxError("Imbalanced parentheses")
  
def evaluate_simple(exp, env):
    """Evaluate a simple (non-compound) expression"""
    if is_primitive(exp):
        return evaluate_primitive(exp)
    elif is_builtin(exp):
        return get_builtin(exp)
    return lookup_variable(exp, env)

def parse(expression):
    """Break an expression into words (sub-expressions).
    Returns: list of words"""

    if len(expression) == 0:
        return [expression]

    # token which indicates the start of a new compound expression
    start_token = '('
    end_token = ')'
    # chars to ignore
    skip_chars = [' ', '\t', '\n']
    delimiters = (*skip_chars, start_token, end_token)
    words = []
    word = ''
    depth = 0
    next_depth = 0
    for i in range(len(expression)):
        t = expression[i]

        if t == start_token:
            next_depth += 1
        elif t == end_token:
            depth -= 1
            next_depth = depth

        if depth > 0 or t not in skip_chars:
            word += t
        if depth == 0:
            next_terminates = i== (len(expression)-1) or expression[i+1] in delimiters
            if t == end_token or t not in delimiters and next_terminates:
                words.append(word)
                word = ''

        depth = next_depth

    if depth != 0:
        raise SyntaxError("Imbalanced parentheses")
        
    return words

def combine(results, env):
    """ Combine a list of sub-results to produce a single value.
        If the first item is a function, that is applied to the rest of the results.
        Otherwise, the final element is returned."""
    if len(results) == 1:
        return results[0]
    else:
        op, args = results[0], results[1:]
        if is_function(op):
            return op(args, env)
        return args[-1]

def is_valid_variable_name(name):
    if is_builtin(name):
        return False
    if re.match(r"^\w*$", name):
        return True
    return False

def evaluate_words(expression, env):
    """Evaluate the words in the expression provided."""

    words = parse(expression)
    if len(words) == 0:
        return []
    elif len(words) == 1:
        return [evaluate_simple(expression, env)]
    #special case -- if we're defining a variable, there's no need to evaluate whatever comes next
    if words[0] == 'define':
        if len(words) != 3:
            raise SyntaxError(f"The 'define' keyword takes two args")
        name = words[1]
        # a function is being defined
        if is_function_call(name):
            # pull out the function name and its args
            # leave the final subexpression unevaluated
            name = strip(name)
            name_words = parse(name)
            name, args = name_words[0], name_words[1:]
            val = Lambda(args, words[2])
        else:
            if not is_valid_variable_name(name):
                raise SyntaxError(f"{name} is not a valid variable name")
            #evaluate final subexpression and assign
            val = evaluate(words[2], env)
        define = evaluate(words[0], env)
        return [define, name, val]
    
    results = [evaluate(subexp, env) for subexp in words]
    return results

def is_function_call(expression):
    return expression[0] == '(' and expression[-1] == ')'

def evaluate(expression, env):
    """ Evaluate expression in the given environment
    """
    
    if is_function_call(expression):
        expression = strip(expression)
        inner_words = evaluate_words(expression, env)
        return combine(inner_words, env)
    
    results = evaluate_words(expression, env)
    if len(results) == 0:
        return []
    return results[-1]