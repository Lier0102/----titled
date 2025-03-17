#include <stdio.h>

int A[20][20], ans, B[20], n;

void f(int e, int s) {
    if(e == n + 1) {
        for (int i = 1; i <= n; i++) {
            for (int j = i + 1; j <= n; j++) {
                if (B[i] == 1 && B[j] == 1 && A[i][j] == 1) return;
            }
            if (ans<s) ans=s;
        }
        return;
    }
    B[e] = 1;
    f(e + 1, s+1);

    B[e] = 0;
    f(e + 1, s);
}


int main(void) {
    f(3, 1);

    printf("%d", ans);

    return 0;
}