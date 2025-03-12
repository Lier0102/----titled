// 2*N타일링_2

#include <stdio.h>

long long dp[1001];

int main(void) {
    int n;
    
    dp[1] = 1;
    dp[2] = 3;

    scanf("%d", &n);

    for (int i = 3; i <= n; i++) dp[i] = (dp[i - 1] + 2 * dp[i - 2]) % 10007;

    printf("%lld\n", dp[n]);

    return 0;
}

// author : neam 
// >:D
