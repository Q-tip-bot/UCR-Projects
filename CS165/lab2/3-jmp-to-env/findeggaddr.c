#include <unistd.h>

int main(void)
{
  printf("EGG address: 0x%lx\n", getenv("EGG"));
  printf("RET address: 0x%lx\n", getenv("RET"));
  return 0;

}
