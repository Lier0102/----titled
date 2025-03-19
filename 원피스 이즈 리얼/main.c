#include <stdio.h>

int swap(int a, int b) {
    int tmp;

    tmp = a;
    a = b;
    b = tmp;
}

int main() {
    int *a;
    int b=1;
    int c=5;
    
    swap(b, c);

    printf("%d", c);
}