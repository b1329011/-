#include <stdio.h>

int main() {
    int i=12345;
    int m,n;
    m=i%10;
    n=(i%10000)/1000*1000;
    i=i-m-n+(m*1000)+(n/1000);
    printf("%d",i);
    return 0;
}
