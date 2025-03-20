#include <stdio.h>
#include <math.h>

int main(void) {
	int k;
	int prime = 0;
	int cnt=1;

	scanf("%d", &k);

	for(;;) {
		prime = 1;
		for (int i = 2; i * i <= k; i++) {
			if (k % i == 0) {
				prime = 0;
				k /= i;
				cnt++;
				break;
			}
		}
		if (prime) break;
	}
	
	int ans = (int)ceil(log10(cnt) / log10(2));

	printf("%d", ans);

	return 0;
}

// author : neam
// aedsfasldjflasdjfkadsjf;asojfaoiw;efjaio;ejf;a
// tlqkf tprtm!!!!!