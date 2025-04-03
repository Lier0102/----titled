#include <stdio.h>
#include <stdlib.h>

int main() {
    int a,b, max;
    scanf("%d %d", &a, &b);
    
    max = a > b ? a : b;
    printf("%d\n", a==max ? a-b : b-a);
    
    printf("%d\n", abs(a-b));

    printf("%d\n", (a-b) < 0 ? (b-a) : (a-b));
}
