#include <stdio.h>

int solve[1000000], size, n, command, v;

int main() {
	scanf("%d", &n);

	while (n--) {
		scanf("%d", &command);

		switch (command) {
            case 1:
                scanf("%d", &v);
                solve[++size] = v;
                break;
            case 2:
                if (size) printf("%d\n", solve[size--]);
                else printf("-1\n");
                break;
            case 3:
                printf("%d\n", size);
                break;
            case 4:
                if (!size) printf("1\n");
                else printf("0\n");
                break;
            case 5:
                if (size) printf("%d\n", solve[size]);
                else printf("-1\n");
                break;
        }
	}
    
	return 0;
}

// 라곤 하지만 사실 dp가 ㅊ아님...ㅌ