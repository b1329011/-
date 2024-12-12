#include <stdio.h>

int main() {
    int i,x,y;
    for (i=1; i<=81; i++) {
        x=(i-1)/9+1;
        y=(i-1)%9+1;
        
        printf("%d*%d=%d ",x,y,x*y);
        
        if (y==9) {
            printf("\n"); 
        }
    }
    return 0;
}
