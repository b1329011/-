#include <stdio.h>

int main()
{
    int x;
    double y,pi=0;
    for(x=1;x<=10000000;x+=2){
        y=4.00/x;
        
        if(x%4==1){
        pi=pi+y;
        }
        
        else if(x%4==3){
        pi=pi-y;    
        }
    }
    printf("%.5f",pi);

    return 0;
}
