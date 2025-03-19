#include <stdio.h>

int employees(int x1, int y1, int r1, int x2, int y2, int r2) {
    int err, cp;

    err = (r1 + r2) * (r1 + r2); // 거리 1과 2의합 제곱
    cp = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1); // 두 예상 거리의 

    if (cp == 0) {
        if (r1 == r2) return -1;
    }
    else {
        if((cp < err) && (cp > (r2 - r1) * (r2 - r1))) return 2;
        if((cp == err) || (cp == (r2 - r1) * (r2 - r1))) return 1;
    }

    return 0;
}
int main(void) {
    int t;
    int x1, x2, y1, y2, r1, r2, i; // 각각의 주어진 좌표들

    scanf("%d", &t);

    for(i = 0; i < t; i++) {
        scanf("%d %d %d %d %d %d", &x1, &y1, &r1, &x2, &y2, &r2);
        printf("%d\n", employees(x1, y1, r1, x2, y2, r2));
    }
    return 0;
}

// use at your own risk
// author : neam