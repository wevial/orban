# Orban: implementation of Thompson's construction algorithm in
#        Python. "Regular Expression Search Algorithm"

class Split:
    """ Represent different states of the NFA """
    def __init__(self, out1, out2):
        self.out1 = out1
        self.out2 = out2

    def __repr__(self):
        # return "Split: out1 -> " + str(type(self.out1)) + " || out2 -> " + str(type(self.out2))
        return "Split -> " + str(id(self.out1)) + " | ->" + str(id(self.out2))

class Match:
    """ If you've reached this state, you have found a match! """
    def __repr__(self):
        return "Match"

class Consume:
    """ Represents the "edges" of the NFA which consume tokens """
    def __init__(self, literal, out):
        self.literal = literal 
        self.out = out # State which Consume points to

    def __repr__(self):
        return "Consume '" + str(self.literal) + "' -> " + str(id(self.out))
        # return "Consume '" + str(self.literal) + "' -> " + str(self.out)

class Placeholder:
    """ Represent a placeholder state """
    def __init__(self, pointing_to):
        self.pointing_to = pointing_to

    def __repr__(self):
        return "Placeholder -> " + str(id(self.pointing_to))


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
            if nonop_token_count[-1] == 0 and literal_count == 0: # Cannot operate without tokens
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
                for j in range(0, i):
                    # print(str(j) + ": " + regex[i-j-1])
                    if regex[i-j-1] == ')':
                        lhs_paren_count += 1
                    elif regex[i-j-1] == '(':
                        lhs_paren_count -= 1
                        if lhs_paren_count < 0:
                            inside_paren = True
                            # get sub string from '(' until '|'
                            re1 = regex[i-j:i]
                            break
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

def re_to_tree(regex):
    if not check_syntax(regex):
        print("Regex syntax is incorrect")
        return None
    regex = add_concat(regex)
    regex = infix_to_postfix(regex)
    (re_tree, t) = build_tree(regex)
    return re_tree

def to_nfa(regex, and_then=None):
    """
    Takes in a regular expression in the form of a syntax tree
    and converts it into a NFA.
    """
    if and_then == None:
        return to_nfa(regex, Match())

    for label in regex:
        if label == 'Literal':
            return Consume(regex[label][0], and_then)
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
            re = regex[label][0]
            # res = to_nfa(r, placeholder)
            # print(res)
            # print()
            split = Split(to_nfa(re, placeholder), and_then)
            placeholder.pointing_to = split
            # print("Split:\t" + str(split))
            # print("PH:\t" + str(placeholder))
            # print("And then:\t" + str(and_then))
            # P.pprint(re)
            return placeholder
        elif label == 'Question':
            placeholder = Placeholder(None)
            re = regex[label][0] # val of '?'
            split = Split(to_nfa(re, placeholder), and_then)
            placeholder.pointing_to = and_then
            return split

def nfa_states(nfa):
    """
    Use BFS to retrieve all states in the NFA. This is more for bug
    checking than for anything else. Maybe I could visualize the NFA, idk.
    """
    stack = [nfa]
    states = set()
    visited = set()
    while stack:
        state = stack.pop()
        if state not in visited:
            visited.add(state)
            if type(state) == Consume:
                stack.append(state.out)
                states.add(("Consume", state.literal, id(state)))
            elif type(state) == Split:
                stack.append(state.out1)
                stack.append(state.out2)
                states.add(("Split", id(state.out1), id(state.out2), id(state)))
            elif type(state) == Placeholder:
                stack.append(state.pointing_to)
                states.add(("Placeholder", id(state)))
            else: # type(state) == Match:
                states.add(("Match", id(state)))
    # print(len(states))
    return (states, visited)


    # while type(nfa) != type(Match()):

# def evaluate_nfa(nfa, string):
    def eval_states(nfa, char):
        stateStates = nfa_states(nfa)[0]
        return {eval_state(state, char, stateStates) for state in stateStates}

    def eval_state(curr_state, char, stateStates):
        if curr_state in stateStates:
            return set()
        else:
            stateStates.add(curr_state)
            if type(curr_state) == Placeholder:
                return eval_state(curr_state.pointing_to, char, stateStates)
            elif type(curr_state) == Consume:
                if curr_state.literal == char:
                    return Set(curr_state.out)
                else:
                    return set()
            elif type(curr_state) == Split:
                r1 = eval_state(curr_state.out1, char, stateStates)
                r2 = eval_state(curr_state.out2, char, stateStates)
                return r1.union(r2)
            elif type(curr_state) == Match:
                return set() if char != None else set(Match())
            
    if type(nfa) != set:
        return evaluate_nfa({nfa}, string)

    if string == '' or string == None:
        return eval_states(nfa, None)
    else: # Non-empty string
        return evaluate_nfa(
            eval_states(nfa, string[0]), # Get set of states for that char
            string[1:] # recursive call eval to check for the rest of the string
            )

def match(nfa, string):
    def simulate_states(nfa_list, token):
        visited = set()
        next_states = []
        for state in nfa_list:
            (new_states, visited) = sim_state(state, token, visited)
            next_states += new_states
            # print(token + " NEW: " + str(new_states))
        # print(next_states)
        return next_states

    def sim_state(curr_state, token, visited):
        nope = ([], visited)
        if curr_state in visited:
            return nope
        else:
            visited.add(curr_state)
            # ty = type(curr_state) DRY!
            if isinstance(curr_state, Consume):
                if curr_state.literal == token:
                    return ([curr_state.out], visited)
                else:
                    return nope
            elif isinstance(curr_state, Split):
                (s1, visited) = sim_state(curr_state.out1, token, visited)
                (s2, visited) = sim_state(curr_state.out2, token, visited)
                return (s1 + s2, visited)
            elif isinstance(curr_state, Placeholder):
                return sim_state(curr_state.pointing_to, token, visited)
            else: # type == Match
                # return [] if token != None else [Match()]
                return ([] if token != None else [curr_state], visited)
                # return nope

    if isinstance(nfa, str):
        return match([to_nfa(re_to_tree(nfa))], string)
    elif not isinstance(nfa, list):
        return match([nfa], string)
        
    if string == '':
        states = simulate_states(nfa, None)
        for state in states:
            if isinstance(state, Match):
                return True
        else:
            return False
        # x = simulate_states(nfas, None)
        # if match is in the result, then there's a match
    else: # Non-empty string
        # get set of possible states for next token in string
        next_states = simulate_states(nfa, string[0])
        # return next_states
        return match(next_states, string[1:])



# EOF #