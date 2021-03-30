/* 
Mini_l.y 
Made by Queston Juarez and Mark Spencer
CS152
*/

%{
#include "heading.h"
void yyerror(const char *s);
extern int currLine;
extern int currPos;
int yylex(void);
%}

// Bison Declarations
%union{
  int		int_val;
  char*		op_val;
}

%error-verbose
%start	Program
%token	FUNCTION
%token	BEGIN_PARAMS
%token  END_PARAMS
%token  BEGIN_LOCALS
%token  END_LOCALS
%token  BEGIN_BODY
%token  END_BODY
%token  INTEGER
%token  ARRAY
%token  OF
%token  IF
%token  THEN
%token  ENDIF
%token  ELSE
%token  WHILE
%token  DO
%token  FOREACH
%token  IN
%token  BEGINLOOP
%token  ENDLOOP
%token  CONTINUE
%token  READ
%token  WRITE
%token  AND
%token  OR
%token  NOT
%token  TRUE
%token  FALSE
%token  RETURN
%token  SUB
%token  ADD
%token  MULT
%token  DIV
%token  MOD
%token  EQ
%token  NEQ
%token  LT
%token  GT
%token  LTE
%token  GTE
%token  SEMICOLON
%token  COLON
%token  COMMA
%token  L_PAREN
%token  R_PAREN
%token  L_SQUARE_BRACKET
%token  R_SQUARE_BRACKET
%token  ASSIGN
%token  <op_val>  IDENT
%token  <int_val> NUMBER


// Grammar Rules
%%
Program:	functions {printf ("Program -> functions\n");}
		;

functions:	{printf ("functions -> epsilon\n");}
		| function functions {printf ("functions -> function functions\n");}
		;

function:	FUNCTION ident SEMICOLON BEGIN_PARAMS declarations END_PARAMS BEGIN_LOCALS declarations END_LOCALS BEGIN_BODY statements END_BODY {printf ("function -> FUNCTION ident SEMICOLON BEGINPARAMS declarations ENDPARAMS BEGINLOCALS declarations ENDLOCALS BEGINBODY statements ENDBODY\n");}
		;

declarations:	{printf ("declarations -> epsilon\n");} 
		| declaration SEMICOLON declarations {printf ("declarations -> declaration SEMICOLON declarations\n");}
		;

declaration:	identifiers COLON INTEGER {printf ("declaration -> identifiers COLON INTEGER\n");} 
		| identifiers COLON ARRAY L_SQUARE_BRACKET NUMBER R_SQUARE_BRACKET OF INTEGER {printf ("declaration -> identifiers COLON ARRAY L_SQUARE_BRACKET NUMBER %d R_SQUARE_BRACKET OF INTEGER\n", $5);}
		;

identifiers:	ident {printf ("identifiers -> ident\n");} 
		| ident COMMA identifiers {printf ("identifiers -> ident COMMA identifiers\n");}
		;

ident:		IDENT {printf ("ident -> IDENT %s\n",$1);}
		;

statements:	{printf ("statements -> epsilon\n");} 
		| statement SEMICOLON statements {printf ("statements -> statement SEMICOLON statements\n");}
		;

statement:	READ vars {printf ("statement -> READ vars\n");} 
		| WRITE vars {printf ("statement -> WRITE vars\n");} 
		| var ASSIGN expression {printf ("statement -> var ASSIGN expression\n");} 
		| CONTINUE {printf ("statement -> CONTINUE\n");} 
		| IF bool_exp THEN statements ENDIF {printf ("statement -> IF bool_exp THEN statements ENDIF\n");} 
		| IF bool_exp THEN statements ELSE statements ENDIF {printf ("statement -> IF bool_exp THEN statements ELSE statements ENDIF\n");} 
		| WHILE bool_exp BEGINLOOP statements ENDLOOP {printf ("statement -> WHILE bool_exp BEGINLOOP statements ENDLOOP\n");} 
		| DO BEGINLOOP statements ENDLOOP WHILE bool_exp {printf ("statement -> DO BEGINLOOP statements ENDLOOP WHILE bool_exp\n");} 
		| FOREACH ident IN ident BEGINLOOP statements ENDLOOP {printf ("statement -> FOREACH ident IN ident BEGINLOOP statements ENDLOOP\n");} 
		| RETURN expression {printf ("statement -> RETURN expression\n");}
		;

bool_exp:	relation_and_exp {printf ("bool_exp -> relation_and_exp\n");} 
		| relation_and_exp OR bool_exp {printf ("bool_exp -> relation_and_exp OR bool_exp\n");}
		;

relation_and_exp:	 relation_exp AND relation_and_exp {printf ("relation_and_exp -> relation_exp AND relation_and_exp\n");}
			| relation_exp {printf ("relation_and_exp -> relation_exp\n");}
			;

relation_exp:	relation_exps {printf ("relation_exp -> relation_exps\n");} 
		| NOT relation_exps {printf ("relation_exp -> NOT relation_exps\n");}
		;

relation_exps:	expression comp expression {printf ("relation_exps -> expression comp expression\n");} 
		| TRUE {printf ("relation_exps -> TRUE\n");} 
		| FALSE {printf ("relation_exps -> FALSE\n");} 
		| L_PAREN bool_exp R_PAREN {printf ("relation_exps -> L_PAREN bool_exp R_PAREN\n");}
		;

comp:		EQ {printf ("comp -> EQ\n");} 
		| NEQ {printf ("comp -> NEQ\n");} 
		| LT {printf ("comp -> LT\n");} 
		| GT {printf ("comp -> GT\n");} 
		| LTE {printf ("comp -> LTE\n");} 
		| GTE {printf ("comp -> GTE\n");}
		;

expression:	multiplicative_expression {printf ("expression -> multiplicative_expression\n");} 
		| multiplicative_expression ADD expression  {printf ("expression -> multiplicative_expression ADD expression\n");} 
		| multiplicative_expression SUB expression {printf ("expression -> multiplicative_expression SUB expression\n");}
		;

multiplicative_expression:	term {printf ("multiplicative_expression -> term\n");} 
				| term MULT term {printf ("multiplicative_expression -> term MULT term\n");} 
				| term DIV term {printf ("multiplicative_expression -> term DIV term\n");} 
				| term MOD term {printf ("multiplicative_expression -> term MOD term\n");}
				; 

term:		ident L_PAREN R_PAREN {printf ("term -> ident L_PAREN R_PAREN\n");} 
		| ident L_PAREN term_expression R_PAREN {printf ("term -> ident L_PAREN term_expression R_PAREN\n");} 
		| SUB terms {printf ("term -> SUB terms\n");} 
		| terms {printf ("term -> terms\n");}
		;

term_expression:	expression {printf ("term_expression -> expression\n");} 
			| expression COMMA term_expression {printf ("term_expression -> expression COMMA term_expression\n");}
			;

terms:		var {printf ("terms -> var\n");} 
		| NUMBER {printf ("terms -> NUMBER %d\n", $1);} 
		| L_PAREN expression R_PAREN {printf ("terms -> L_PAREN expression R_PAREN\n");}
		; 

vars:		var {printf ("vars -> var\n");}
		| var COMMA vars {printf ("vars -> var COMMA vars\n");}
		;

var:		ident {printf ("var -> ident\n");} 
		| ident L_SQUARE_BRACKET expression R_SQUARE_BRACKET {printf ("var -> ident L_SQUARE_BRACKET expression R_SQUARE_BRACKET\n");}
		;

%%

void yyerror(const char *s)
{
  printf("** Line %d, position %d: %s\n", currLine, currPos, s);
}

main()
{
  yyparse();
  return 0;
}
