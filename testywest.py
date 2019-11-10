cwd: C:\Users\Drew\Desktop\Code Projects\DrewLangPlayground\DrewLang
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
program:	[ '*' -> [ statement, end!=EOF_TYPE,  ],  ]
statement:	[ 'SUB_RULE' -> [ '|' -> [ printstat, blockstat, ifstat, whilestat, assignstat,  ],  ],  ]
assignstat:	[ NAME, '=', expr, ';',  ]
printstat:	[ 'print', '(', 'SUB_RULE' -> [ '|' -> [ NAME, expr,  ],  ], ')', ';',  ]
ifstat:		[ 'if', '(', test, ')', statement,  ]
whilestat:	[ 'while', '(', test, ')', statement,  ]
blockstat:	[ '{', '*' -> [ statement, end!=RCURBRACK,  ], '}',  ]
expr:		[ 'SUB_RULE' -> [ '|' -> [ NUMBER, string,  ],  ], '*' -> [ 'SUB_RULE' -> [ add_op, expr,  ], end==PLUS,  ],  ]
test:		[ 'SUB_RULE' -> [ '|' -> [ NAME, expr,  ],  ], cmp_op, 'SUB_RULE' -> [ '|' -> [ NAME, expr,  ],  ],  ]
string:		[ '"', '*' -> [ 'SUB_RULE' -> [ '|' -> [ NAME, NUMBER,  ],  ], end==NAME,NUMBER,  ], '"',  ]
NAME:		[ 'SUB_RULE' -> [ '|' -> [ 'a'..'z', 'A'..'Z',  ],  ],  ]
NUMBER:		[ ('0'..'9'),  ]
cmp_op:		[ 'SUB_RULE' -> [ '|' -> [ DEQUALS, GE, LE, '>', '<',  ],  ],  ]
add_op:		[ 'SUB_RULE' -> [ '|' -> [ '+', '-',  ],  ],  ]
DEQUALS:	[ '=', '=',  ]
GE:		[ '>', '=',  ]
LE:		[ '<', '=',  ]

    def program(self):
        while self.LA(1) != self.input.EOF_TYPE:
            self.statement()

    def statement(self):
        if self.LA(1) == self.input.PRINT:
            self.printstat()
        elif self.LA(1) == self.input.LCURBRACK:
            self.blockstat()
        elif self.LA(1) == self.input.IF:
            self.ifstat()
        elif self.LA(1) == self.input.WHILE:
            self.whilestat()
        elif self.LA(1) == self.input.NAME:
            self.assignstat()

    def assignstat(self):
        self.NAME()
        self.match('=')
        self.expr()
        self.match(';')

    def printstat(self):
        self.match('print')
        self.match('(')
        if self.LA(1) == self.input.NAME:
            self.NAME()
        elif self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.DQUOTE:
            self.expr()
        self.match(')')
        self.match(';')

    def ifstat(self):
        self.match('if')
        self.match('(')
        self.test()
        self.match(')')
        self.statement()

    def whilestat(self):
        self.match('while')
        self.match('(')
        self.test()
        self.match(')')
        self.statement()

    def blockstat(self):
        self.match('{')
        while self.LA(1) != self.input.RCURBRACK:
            self.statement()
        self.match('}')

    def expr(self):
        if self.LA(1) == self.input.NUMBER:
            self.NUMBER()
        elif self.LA(1) == self.input.DQUOTE:
            self.string()
        while self.LA(1) == self.input.PLUS:
            self.add_op()
            self.expr()

    def test(self):
        if self.LA(1) == self.input.NAME:
            self.NAME()
        elif self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.DQUOTE:
            self.expr()
        self.cmp_op()
        if self.LA(1) == self.input.NAME:
            self.NAME()
        elif self.LA(1) == self.input.NUMBER or self.LA(1) == self.input.DQUOTE:
            self.expr()

    def string(self):
        self.match('"')
        while self.LA(1) == self.input.NAME or self.LA(1) == self.input.NUMBER:
            if self.LA(1) == self.input.NAME:
                self.NAME()
            elif self.LA(1) == self.input.NUMBER:
                self.NUMBER()
        self.match('"')

    def NAME(self):
        self.match(self.input.NAME)

    def NUMBER(self):
        self.match(self.input.NUMBER)

    def cmp_op(self):
        if self.LA(1) == self.input.EQUALS:
            self.DEQUALS()
        elif self.LA(1) == self.input.GT and self.LA(2) == self.input.EQUALS:
            self.GE()
        elif self.LA(1) == self.input.LT and self.LA(2) == self.input.EQUALS:
            self.LE()
        elif self.LA(1) == self.input.GT:
            self.match('>')
        elif self.LA(1) == self.input.LT:
            self.match('<')

    def add_op(self):
        if self.LA(1) == self.input.PLUS:
            self.match('+')
        elif self.LA(1) == self.input.DASH:
            self.match('-')

    def DEQUALS(self):
        self.match('=')
        self.match('=')

    def GE(self):
        self.match('>')
        self.match('=')

    def LE(self):
        self.match('<')
        self.match('=')
