#define ll long long
gcd(a,b){return b?gcd(b,a%b):a;}main(a,b){scanf("%d%d",&a,&b);printf("%lld",(ll)a/gcd(a,b)*b);}

// 내가 숏코딩 위에 서겠다.