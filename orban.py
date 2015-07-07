# Orban: implementation of Thompson's construction algorithm in
#        Python. "Regular Expression Search Algorithm"

import pprint 

Node = dict
Leaf = str

# "The first stage is a syntax sieve that allows only syntactically 
#  correct regular expressions to pass. This stage also inserts the
#  operator "•" for juxtaposition of regular expressions."
def check_syntax(regex):
    """
    Check that the input regular expression is syntatically correct.
    Also adds "." as a concatenation operator where applicable.
    """
    # Accounting for ( ) | * + ? operands only, no escapes
    ops = '(+*?|' # Does not include ')' as ops may legally follow it
    paren_balance = 0
    literal_count = 0
    nonop_token_count = [0]

    for i in range(0, len(regex)): 
        if regex[i] == '(':
            paren_balance += 1
            nonop_token_count.append(0)

        elif regex[i] == ')':
            paren_balance -= 1
            if paren_balance < 0:
                # print('too many )')
                return False 
            elif nonop_token_count[-1] == 0:
                # Parenthesis contents cannot be empty
                # print('empty paren')
                return False
            nonop_token_count.pop()

        elif regex[i] in '*+?':
            if nonop_token_count[-1] == 0: # Cannot operate without tokens
                # print('op?')
                return False
            elif regex[i-1] in ops:
                # print('op2?')
                return False

        elif regex[i] == '|':
            # Must check before and after |
            # Splice regex string into two?? then make a recursive call
            # backtrack until reach '(' or beginning of string, whichever 1st
            # lookforward until ')' if applicable, else until end of string
            # if each side is valid, then union will be valid
            if nonop_token_count[-1] == 0 and literal_count == 0:
                # print('nonop token count == 0')
                # print(nonop_token_count)
                # print(regex[i])
                # print(paren_balance)
                return False

            if len(nonop_token_count) > 1:
                # print('hello')
                # backtrack to '(' >> else backtrack to ')' or beginning of str
                # Start with LHS of '|'
                re1 = ''
                re2 = ''
                inside_paren = False
                lhs_paren_count = 0
                rhs_paren_count = 0
               # print("\nREGEX: " + regex)
                # for j in range(0, i):
                #     print(str(j) + ": " + regex[i-j-1])
                #     if regex[i-j-1] == ')':
                #         lhs_paren_count += 1
                #     elif regex[i-j-1] == '(':
                #         lhs_paren_count -= 1
                #         if lhs_paren_count < 0:
                #             inside_paren = True
                #             # get sub string from '(' until '|'
                #             re1 = regex[i-j:i]
                #             break
                # print("LHS paren #: " + str(lhs_paren_count))
                # print('inside paren')
                if re1 == '':
                    # print("lhs_paren_count: " + str(lhs_paren_count))
                    # print(inside_paren)
                    # print("re1 == ''")
                    re1 = regex[:i]
                    re2 = regex[i+1:]
                elif inside_paren:
                    for j in range(i+1, len(regex)):
                        if regex[j] == ')':
                            rhs_paren_count -= 1
                            if rhs_paren_count < 0:
                                re2 = regex[i+1:j]
                                break
                        elif regex[j] == '(':
                            rhs_paren_count += 1
                    if re2 == '':
                        return False

                # print("re1: " + re1)
                # print("re2: " + re2)
                r1 = check_syntax(re1)
                r2 = check_syntax(re2)
                if (r1 and r2) == False:
                    return False
                        
                r1 = check_syntax(re1)
                r2 = check_syntax(re2)
                if (r1 and r2) == False:
                    return False


                for j in range(i+1, len(regex)):
                    pass

        else: # Non-operand character
            nonop_token_count[-1] += 1
            literal_count += 1
            # print(nonop_token_count)
            # print('add')

    if paren_balance != 0:
        return False

    return True

def add_concat(regex):
    """
    Insert infix concat operator. Assumes all input regexes
    have been checked to be syntactically correct (aka checked
    using check_syntax())
    """
    if len(regex) == 1:
        return regex
    new_regex = ''
    for i in range(0, len(regex)):
        new_regex += regex[i]
        if i == len(regex) - 1:
            break
        elif regex[i] not in '(*+?|':
            if regex[i+1] not in ')*+?|':
                new_regex += '.'
        elif regex[i] in '*+?':
            if regex[i+1] not in ')*+?|':
                new_regex += '.'
    return new_regex

# "The second stage converts the regular expressions to reverse Polish
#  form."
# "The regular expression a(b|c)*d is translated into abc|*•d• by the
#  first two stages."
def infix_to_postfix(regex):
    """
    Convert input regular expression to postfix notation
    using the Shunting-Yard algorithm.
    """

    def cmp_precedence(top_op, op):
        """
        Compares operator precedence.
        True: pop off top_op
        False: don't pop it
        """
        if top_op in '()':
            return False
        precedence = {
                '*': (3, 'r'),
                '+': (3, 'r'),
                '?': (3, 'r'),
                '.': (2, 'l'),
                '|': (1, 'l'),
                }
        (top_op, top_op_assoc) = precedence[top_op]
        (op, op_assoc) = precedence[op]
        if op_assoc == 'l': # operator is left associative
            # precdence is op <= to top_op, then pop top_op to queue
            return True if op <= top_op else False
        else: # op_assoc is right associative
            # precdence is op < to top_op, then pop top_op to queue
            return True if op < top_op else False

    def print_stuff(ops_stack, regex, token):
        print("token: " + token)
        print("ops: " + str(ops_stack))
        print("regex: " + regex + "\n")

    ops_stack = []
    postfix_regex = ''

    for token in regex:
        if token not in '()*+?|.':
            postfix_regex += token
        elif token == '(':
            ops_stack.append(token)
            # print_stuff(ops_stack, postfix_regex, token)
        elif token == ')':
            while len(ops_stack) > 0 and ops_stack[-1] != '(':
                postfix_regex += ops_stack.pop()
            ops_stack.pop() # Pop off '(' from stack
            # print_stuff(ops_stack, postfix_regex, token)
        else:
            if len(ops_stack) <= 0:
                ops_stack.append(token)
            else:
                while ops_stack:
                    top_op = ops_stack[-1]
                    r = cmp_precedence(top_op, token)
                    if r:
                        postfix_regex += ops_stack.pop()
                    else:
                        break
                ops_stack.append(token)
            # print_stuff(ops_stack, postfix_regex, token)
    while ops_stack:
        if ops_stack[-1] in '()':
            # Mismatched parenthesis
            return postfix_regex
        postfix_regex += ops_stack.pop()
        # print_stuff(ops_stack, postfix_regex, token)
    return postfix_regex

def build_tree(regex):
    """
    Input is a regular expression in postfix form. The function
    constructs a syntax tree that corresponds to the regex.
    """
    def binary_op(regex):
        (lhs, re1) = build_tree(regex[:-1])
        (rhs, re2) = build_tree(re1)
        label = 'Concat' if regex[-1] == '.' else 'Or' 
        return ({label: [lhs, rhs]}, re2)

    def unary_op(regex):
        (child, re) = build_tree(regex[:-1])
        label = ''
        if regex[-1] == '+':
            label = 'Plus'
            k = {'Kleene': child}
            return ({'Concat': [k, child]}, re)
        elif regex[-1] == '*':
            label = 'Kleene'
        else:
            label = 'Question'
        return ({label: [child]}, re)

    def literal(regex):
        return ({"Literal": [regex[-1]]}, regex[:-1])

    syntax_tree = {}
    if regex[-1] in '.|':
        syntax_tree = binary_op(regex)
    elif regex[-1] in '*+?':
        syntax_tree = unary_op(regex)
    else:
        syntax_tree = literal(regex)

    return syntax_tree

def re_to_tree(regex):
    if not check_syntax(regex):
        print("Regex syntax is incorrect")
        return None
    regex = add_concat(regex)
    regex = infix_to_postfix(regex)
    (re_tree, t) = build_tree(regex)
    return re_tree


class Split:
    """ Represent different states of the NFA """
    def __init__(self, out1, out2):
        self.out1 = out1
        self.out2 = out2

    def __repr__(self):
        return "Split: -> " + str(self.out1) + "\n->" + str(self.out2)

class Match:
    """ If you've reached this state, you have found a match! """
    def __init__(self):
        pass

    def __repr__(self):
        return "Matching state"

class Edge:
    """ Represent different edges of the NFA """
    def __init__(self, literal, out):
        self.literal = literal 
        self.out = out # State which edge points to

    def __repr__(self):
        return "Edge '" + str(self.literal) + "' -> " + str(self.out)

class Placeholder:
    """ Represent a placeholder state """
    def __init__(self, pointing_to):
        self.pointing_to = pointing_to

    def __repr__(self):
        return "Placeholder -> " + str(self.pointing_to)

def to_nfa(regex, and_then=None):
    """
    Takes in a regular expression in the form of a syntax tree
    and converts it into a NFA
    """
    if and_then == None:
        return to_nfa(regex, Match())

    for label in regex:
        if label == 'Literal':
            return Edge(regex[label][0], and_then)
        elif label == 'Concat':
            lhs = regex[label][0]
            rhs = regex[label][1]
            return to_nfa(lhs, to_nfa(rhs, and_then))
        elif label == 'Or':
            lhs = regex[label][0]
            rhs = regex[label][1]
            r1 = to_nfa(lhs, and_then)
            r2 = to_nfa(rhs, and_then)
            return Split(r1, r2)
        elif label == 'Kleene':
            placeholder = Placeholder(None)
            r = regex[label]
            split = Split(to_nfa(r, placeholder), and_then)
            placeholder.pointing_to = split
            return placeholder










# "The third stage is the object code producer. It expects a syntactically
#  correct reverse Polish regular expression as input."

# "The heard of the third stage is a pushdown stack. Each entry in the
#  stack is a pointer to the compiled code of an operand. When a binary
#  operator ("|" or "•") is compiled, the top (most recent) two entries
#  on the stack are combined and a resultant point for the operation
#  replaces the two stack entries. The result of the binary operator is
#  then available as an operand in another operation. Similarly a unary
#  operator ("*") operates on the top entry of the stack and creates an
#  operand to replace that entry. When the entire regular expression is
#  compiled, there is just one entry in the stack, and that is a pointer
#  to the code for the regular expression."
