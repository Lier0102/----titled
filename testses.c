#include <stdio.h>

int main(void) {
    int total;
    char grade;

    scanf("%d", &total);
    fflush(stdin);
    scanf("%c", &grade);

    printf("%d %c", total, grade);

    return 0;
}