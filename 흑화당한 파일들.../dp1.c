#include <stdio.h>

long dp[1001];

int main(void) {
    int n;

    dp[1] = 1;
    dp[2] = dp[1];
    dp[3] = dp[1] + dp[2];

    scanf("%d", &n);

    for (int i = 4; i <= n; i++) dp[i] = dp[i - 1] + dp[i - 2];

    printf("%ld\n", dp[n]);
}

// author : neam
// >:D
// 30초컷