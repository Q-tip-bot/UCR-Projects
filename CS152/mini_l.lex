/* 
   Program used to parse MINI_L files 
   
   Queston Juarez
   SID 861148519
   Worked in collaboration with Mark Spencer
   (Mark is currently waitlisted for the class)
*/

%{
#include "heading.h"
#include "y.tab.h"
int currLine = 1, currPos = 1;
%}

digit		[0-9]
alpha		[a-zA-Z]
under		[_]
identifier	({alpha}|{digit}|{under})*({alpha}|{digit})+
invalid1	{digit}({alpha}|{digit}|{under})*({alpha}|{digit})*
invalid2	{alpha}({alpha}|{digit}|{under})*({under})+
number		{digit}+
comment		##.*

%%
"function"	{currPos+=yyleng; return FUNCTION;}
"beginparams"	{currPos+=yyleng; return BEGIN_PARAMS;}
"endparams"	{currPos+=yyleng; return END_PARAMS;}
"beginlocals"	{currPos+=yyleng; return BEGIN_LOCALS;}
"endlocals"	{currPos+=yyleng; return END_LOCALS;}
"beginbody"	{currPos+=yyleng; return BEGIN_BODY;}
"endbody"	{currPos+=yyleng; return END_BODY;}
"integer"	{currPos+=yyleng; return INTEGER;}
"array"		{currPos+=yyleng; return ARRAY;}
"of"		{currPos+=yyleng; return OF;}
"if"		{currPos+=yyleng; return IF;}
"then"		{currPos+=yyleng; return THEN;}
"endif"		{currPos+=yyleng; return ENDIF;}
"else"		{currPos+=yyleng; return ELSE;}
"while"		{currPos+=yyleng; return WHILE;}
"do"		{currPos+=yyleng; return DO;}
"foreach"	{currPos+=yyleng; return FOREACH;}
"in"		{currPos+=yyleng; return IN;}
"beginloop"	{currPos+=yyleng; return BEGINLOOP;}
"endloop"	{currPos+=yyleng; return ENDLOOP;}
"continue"	{currPos+=yyleng; return CONTINUE;}
"read"		{currPos+=yyleng; return READ;}
"write"		{currPos+=yyleng; return WRITE;}
"and"		{currPos+=yyleng; return AND;}
"or"		{currPos+=yyleng; return OR;}
"not"		{currPos+=yyleng; return NOT;}
"true"		{currPos+=yyleng; return TRUE;}
"false"		{currPos+=yyleng; return FALSE;}
"return"	{currPos+=yyleng; return RETURN;}

"-"		{currPos+=yyleng; return SUB;}
"+"		{currPos+=yyleng; return ADD;}
"*"		{currPos+=yyleng; return MULT;}
"/"		{currPos+=yyleng; return DIV;}
"%"		{currPos+=yyleng; return MOD;}
"=="		{currPos+=yyleng; return EQ;}
"<>"		{currPos+=yyleng; return NEQ;}
"<"		{currPos+=yyleng; return LT;}
">"		{currPos+=yyleng; return GT;}
"<="		{currPos+=yyleng; return LTE;}
">="		{currPos+=yyleng; return GTE;}
";"		{currPos+=yyleng; return SEMICOLON;}
":"		{currPos+=yyleng; return COLON;}
","		{currPos+=yyleng; return COMMA;}
"("		{currPos+=yyleng; return L_PAREN;}
")"		{currPos+=yyleng; return R_PAREN;}
"["		{currPos+=yyleng; return L_SQUARE_BRACKET;}
"]"		{currPos+=yyleng; return R_SQUARE_BRACKET;}
":="		{currPos+=yyleng; return ASSIGN;}

"_"		{printf("Error at line %d, column %d: identifier \"%s\" cannot start with an underscore\n", currLine, currPos, yytext);exit(0);}


{number}	{yylval.int_val = atoi(yytext); currPos+=yyleng; return NUMBER;}

{invalid1}	{printf("Error at line %d, column %d: identifier \"%s\" cannot start with a number\n", currLine, currPos, yytext);exit(0);}
{invalid2}	{printf("Error at line %d, column %d: identifier \"%s\" cannot end with an underscore\n", currLine, currPos, yytext);exit(0);}

{identifier}	{yylval.op_val = yytext; currPos+=yyleng; return IDENT;}

[ \t]+		{/* Skip White Space */ currPos += yyleng;}
"\n"		{currLine++; currPos = 1;}
{comment}	{currLine++; currPos = 1;}
.		{printf("Error at line %d, column %d: unrecognized symbol \"%s\"\n", currLine, currPos, yytext);exit(0);}
%%

