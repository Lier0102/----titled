#include <stdio.h>

int main(void) {
    int a, b, c;
    int n1000=0, n500=0, n100=0;

    scanf("%d %d", &a, &b);

    c = b - a;

    while(1) {
        if (c - 1000 > 0) { c -= 1000;  n1000++;}
        else if (c - 500 >= 0) { c -= 500; n500++;}
        else if (c - 100 >= 0) { c -= 100; n100++;}
        else break;
    }

    printf("1000원 : %d, 500원 : %d, 100원 : %d", n1000, n500, n100);
}