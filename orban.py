# Orban: implementation of Thompson's construction algorithm in
#        Python. "Regular Expression Search Algorithm"

class OrbanHelper:
    def __init__(self):
        pass

    def simulate_states(self, nfa_list, token):
        visited = set()
        next_states = []
        for state in nfa_list:
            (new_states, visited) = self.sim_state(state, token, visited)
            next_states += new_states
        return next_states

    def sim_state(self, curr_state, token, visited):
        if curr_state in visited:
            return ([], visited)
        else:
            visited.add(curr_state)
            if isinstance(curr_state, Consume):
                if curr_state.literal == token:
                    return ([curr_state.out], visited)
                else:
                    return ([], visited)
            elif isinstance(curr_state, Split):
                (s1, visited) = self.sim_state(curr_state.out1, token, visited)
                (s2, visited) = self.sim_state(curr_state.out2, token, visited)
                return (s1 + s2, visited)
            elif isinstance(curr_state, Placeholder):
                return self.sim_state(curr_state.pointing_to, token, visited)
            else: # type == Match
                return ([] if token != None else [curr_state], visited)

    def match_state_exists(self, states):
        for state in states:
            if isinstance(state, Match):
                return True
        return False

class Split:
    """
    Represent different splitting states of the NFA, needed
    for alternation '|' and zero-or-one '?' operand.
    """
    def __init__(self, out1, out2):
        self.out1 = out1
        self.out2 = out2

    def __repr__(self):
        return "Split -> " + str(id(self.out1)) + " | ->" + str(id(self.out2))

class Match:
    """ If you've reached this state, you have found a match! """
    def __repr__(self):
        return "Match"

class Consume:
    """ Represents the "edges" of the NFA that consume tokens. """
    def __init__(self, literal, out):
        self.literal = literal 
        self.out = out # State which Consume points to

    def __repr__(self):
        return "Consume '" + str(self.literal) + "' -> " + str(id(self.out))

class Placeholder:
    """ Represent a placeholder state. Needed for empty string processing. """
    def __init__(self, pointing_to):
        self.pointing_to = pointing_to

    def __repr__(self):
        return "Placeholder -> " + str(id(self.pointing_to))

class State:
    def __init__(self, kind, **dict):
        self.kind = kind
        for key, val in dict.items():
            if key == "edges":
                self.edges = val
            elif key == "char":
                self.char = val
            elif key == "elipson":
                self.elipson = val


def check_syntax(regex):
    """
    Check that the input regular expression is syntatically correct.
    Also adds "." as a concatenation operator where applicable.
    ( ) | * + ? are the only operands allowed, no escapes.
    """
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
                return False 
            elif nonop_token_count[-1] == 0:
                # Parenthesis contents cannot be empty
                return False
            nonop_token_count.pop()

        elif regex[i] in '*+?':
            if nonop_token_count[-1] == 0 and literal_count == 0: # Cannot operate without tokens
                return False
            elif regex[i-1] in ops:
                return False

        elif regex[i] == '|':
            # Must check string before and after '|'. LHS: backtrack until reaching '(' or the
            # start of the string, whichever is first. RHS: look forward until ')' if applicable
            # otherwise just go until the end of the string. If both sides have correct syntax,
            # then the alternation is valid.
            if nonop_token_count[-1] == 0 and literal_count == 0:
                return False
            if len(nonop_token_count) > 1:
                re1, re2 = '', ''
                inside_paren = False
                lhs_paren_count, rhs_paren_count = 0, 0
                for j in range(0, i):
                    if regex[i-j-1] == ')':
                        lhs_paren_count += 1
                    elif regex[i-j-1] == '(':
                        lhs_paren_count -= 1
                        if lhs_paren_count < 0:
                            inside_paren = True
                            re1 = regex[i-j:i]
                            break
                if re1 == '':
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
                r1 = check_syntax(re1)
                r2 = check_syntax(re2)
                if (r1 and r2) == False:
                    return False
                        
        else: # Non-operand character
            nonop_token_count[-1] += 1
            literal_count += 1

    if paren_balance != 0:
        return False
    return True

def regex2tree(regex):
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

    def infix_to_postfix(regex):
        """
        Convert input regular expression to postfix notation
        using the Shunting-Yard algorithm. Eg. a(b|c)*d => abc|*.d.
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

        ops_stack = []
        postfix_regex = ''

        for token in regex:
            if token not in '()*+?|.':
                postfix_regex += token
            elif token == '(':
                ops_stack.append(token)
            elif token == ')':
                while len(ops_stack) > 0 and ops_stack[-1] != '(':
                    postfix_regex += ops_stack.pop()
                ops_stack.pop() # Pop off '(' from stack
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
        while ops_stack:
            if ops_stack[-1] in '()': # Mismatched parenthesis
                return postfix_regex
            postfix_regex += ops_stack.pop()
        return postfix_regex

    def build_tree(regex):
        """
        Input is a regular expression in postfix form. The function
        constructs a syntax tree that corresponds to the regex.
        """
        def binary_op(regex):
            # Right hand side is processed first due to postfix notation
            (rhs, re1) = build_tree(regex[:-1])
            (lhs, re2) = build_tree(re1)
            label = 'Concat' if regex[-1] == '.' else 'Or' 
            return ({label: [lhs, rhs]}, re2)

        def unary_op(regex):
            (child, re) = build_tree(regex[:-1])
            label = ''
            if regex[-1] == '+':
                # A+ is equivalent to (AA)*. Converting the plus operator
                # to {Concat: [{Kleene: A}, A]} makes it simpler to construct
                # the NFA. 
                label = 'Plus'
                k = {'Kleene': [child]}
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

    if not check_syntax(regex):
        print("Regex syntax is incorrect")
        return None
    regex = add_concat(regex)
    regex = infix_to_postfix(regex)
    (re_tree, t) = build_tree(regex)
    return re_tree

def tree2nfa(regex, next_states=None):
    """
    Takes in a regular expression in the form of a syntax tree
    and converts it into a NFA.
    """
    if next_states == None:
        return tree2nfa(regex, Match())

    for label in regex:
        if label == 'Literal':
            return Consume(regex[label][0], next_states)
        elif label == 'Concat':
            lhs = regex[label][0]
            rhs = regex[label][1]
            return tree2nfa(lhs, tree2nfa(rhs, next_states))
        elif label == 'Or':
            lhs = regex[label][0]
            rhs = regex[label][1]
            r1 = tree2nfa(lhs, next_states)
            r2 = tree2nfa(rhs, next_states)
            return Split(r1, r2)
        elif label == 'Kleene':
            placeholder = Placeholder(None)
            re = regex[label][0]
            split = Split(tree2nfa(re, placeholder), next_states)
            placeholder.pointing_to = split
            return placeholder
        elif label == 'Question':
            placeholder = Placeholder(None)
            re = regex[label][0] # val of '?'
            split = Split(tree2nfa(re, placeholder), next_states)
            placeholder.pointing_to = next_states
            return split

def regex2nfa(regex):
    re_tree = regex2tree(regex)
    return None if re_tree == None else tree2nfa(re_tree)

def nfa_states(nfa):
    """
    Use BFS to retrieve all states in the NFA. This is more for bug
    checking than for anything else. Maybe I could visualize the NFA, idk.
    """
    stack = [nfa]
    states, visited = set(), set()
    while stack:
        state = stack.pop()
        if state not in visited:
            visited.add(state)
            if isinstance(state, Consume):
                stack.append(state.out)
                states.add(("Consume", state.literal, id(state)))
            elif isinstance(state, Split):
                stack.append(state.out1)
                stack.append(state.out2)
                states.add(("Split", id(state.out1), id(state.out2), id(state)))
            elif isinstance(state, Placeholder):
                stack.append(state.pointing_to)
                states.add(("Placeholder", id(state)))
            else: # isinstance(state, Match)
                states.add(("Match", id(state)))
    return (states, visited)

def match(nfa, string):
    O = OrbanHelper()

    if isinstance(nfa, str):
        nfa = regex2nfa(nfa)
        return None if nfa == None else match([nfa], string) 
    elif not isinstance(nfa, list):
        return match([nfa], string)
        
    if string == '':
        states = O.simulate_states(nfa, None)
        return O.match_state_exists(states)
    else: # Non-empty string
        # get set of possible states for next token in string
        next_states = O.simulate_states(nfa, string[0])
        return match(next_states, string[1:])

def substring(nfa, string, start=None, end=None):
    def substring_helper(nfa, string):
        if string == '':
            states = O.simulate_states(nfa, None)
            return O.match_state_exists(states)
        else:
            states = O.simulate_states(nfa, string[0])
            if O.match_state_exists(states):
                return True
            else:
                return substring_helper(states, string[1:])

    O = OrbanHelper()

    # Truncate string to desired start/end points
    if start != None and end != None:
        string = string[start:end]
    elif state != None:
        string = string[state:]
    elif end != None:
        string = string[:end]

    if isinstance(nfa, str):
        nfa = regex2nfa(nfa)
        return None if nfa == None else substring([nfa], string) 
    elif not isinstance(nfa, list):
        nfa = [nfa]
    
    while len(string) > 0:
        if substring_helper(nfa, string):
           return True
        string = string[1:]

    return False
# EOF #

def nfa2dfa(nfa):
    output = set(nfa)

    while True:
        states_to_add = set()
        for state in output:
            if isinstance(state, Split):
                pass
            elif isinstance(state, Consume):
                pass
            elif isinstance(state, Placeholder):
                pass
            else: # Match state
                break
