#include <stdio.h>

int GCD(int a, int b) {
	if (b == 0) {
		return a;
	}
	else {
		return GCD(b, a % b);
	}
}

int LCM(int a, int b) {
	return a * b / GCD(a, b);
}

int main(void) {
    int k;

    scanf("%d", &k);

    for (int i = 2; i < k; i++) printf("%d ", GCD(k, i));

    return 0;
}