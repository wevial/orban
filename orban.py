# Orban: implementation of Thompson's construction algorithm in
#        Python. "Regular Expression Search Algorithm"

class Orban():

# "The first stage is a syntax sieve that allows only syntactically 
#  correct regular expressions to pass. This stage also inserts the
#  operator "•" for juxtaposition of regular expressions."

    def regex_syntax(self, regex):
        """
        Check that the input regular expression is syntatically correct.
        Also adds "•" as a concatenation operator where applicable.
        """
        # Accounting for ( ) | * + ? operands only, no escapes

        ops = '(+*?|' # Does not include ')' as ops may legally follow it
        paren_balance = 0
        nonop_char_count = [0]

        for i in range(0, len(regex)): 
            if regex[i] == '(':
                paren_balance += 1
                nonop_char_count.append(0)

            elif regex[i] == ')':
                paren_balance -= 1
                if paren_balance < 0:
                    return False 
                elif nonop_char_count[-1] == 0:
                    # Parenthesis contents cannot be empty
                    return False
                nonop_char_count.pop()

            elif regex[i] in '*+?':
                if nonop_char_count[-1] == 0: # Cannot operate without chars
                    return False
                elif regex[i-1] in ops:
                    return False

            elif regex[i] == '|':
                # Must check before and after |
                # Splice regex string into two?? then make a recursive call
                # backtrack until reach '(' or beginning of string, whichever 1st
                # lookforward until ')' if applicable, else until end of string
                # if each side is valid, then union will be valid
                if nonop_char_count[-1] == 0:
                    return False

                if len(nonop_char_count) > 1:
                    # backtrack to '(' >> else backtrack to ')' or beginning of str
                    # Start with LHS of '|'
                    re1 = ''
                    re2 = ''
                    #right_paren_found = False
                    inside_paren = False
                    lhs_paren_count = 0
                    rhs_paren_count = 0
#                    print("\nREGEX: " + regex)
                    for j in range(0, i):
#                        print(str(j) + ": " + regex[i-j-1])
                        if regex[i-j-1] == ')':
                            lhs_paren_count += 1
                        elif regex[i-j-1] == '(':
                            lhs_paren_count -= 1
                            if lhs_paren_count < 0:
                                inside_paren = True
                                # get sub string from '(' until '|'
                                re1 = regex[i-j:i]
                                break
#                    print("LHS paren #: " + str(lhs_paren_count))
                    if re1 == '':
#                        print("lhs_paren_count: " + str(lhs_paren_count))
#                        print(inside_paren)
#                        print("re1 == ''")
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

#                    print("re1: " + re1)
#                    print("re2: " + re2)
                    r1 = self.regex_syntax(re1)
                    r2 = self.regex_syntax(re2)
                    if (r1 and r2) == False:
                        return False
                            
                    r1 = self.regex_syntax(re1)
                    r2 = self.regex_syntax(re2)
                    if (r1 and r2) == False:
                        return False


                    for j in range(i+1, len(regex)):
                        pass

            else: # Non-operand character
                nonop_char_count[-1] += 1

        if paren_balance != 0:
            return False

        return True

# "The second stage converts the regular expressions to reverse Polish
#  form."

    def regex_to_postfix(self, regex):
        """ Convert input regular expression to postfix notation """
        pass

# "The regular expression a(b|c)*d is translated into abc|*•d• by the
#  first two stages."


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
