// 메뉴
// 홈
// 태그
// 방명록
// 미학
// dump
// Programming
// CS50
// PS
// CS:APP
// Troubleshooting
// Projects
// TIL
// Contribution
// 쇼츠
// 번역&요약
// 기타
// 인기포스트
// SSH로 원격 서버 안전하게 접속 관리하기
// 티스토리 블로그에 마크다운 콜아웃(Callout) 넣어⋯
// 하버드 CS50 프로그래밍 입문 강의 수강 가이드 및 ⋯
// [CS:APP/시스템 프로그래밍] Bomb Lab 풀이
// ABOUT ME
// 소프트웨어 개발, 프로그래밍에 대한 이야기를 다룹니다. 

// 트위터
// 인스타그램
// Today6Yesterday131
// Total17,452
// 수서곤충의 세계
// 수서곤충의 세계
// 메뉴검색
// 백준 1021번 회전하는 큐: C언어 풀이
// Programming/PS 2023. 10. 14. 14:09
// 백준 1021 회전하는 큐 문제의 C언어 해설입니다.
// 큐의 회전을 구현하는 방법과, 문제에서 필요한 배열의 크기를 계산하는 방법을 설명합니다.

// 전략
// 큐의 회전 횟수를 어떻게 구할 수 있을까?
// 처음엔 직접 회전을 구현하지 않고, 문제에 필요한 최솟값만 산출하는 방법을 잠깐 고민해봤다.
// 시행착오 끝에, 입력 값 크기도 작겠다, 그냥 정직하게 회전을 구현하기로 했다.

// 오른쪽 회전의 구현은 간단하다. 큐에서 뽑은 원소를 다시 넣어주기만 하면 끝이다.
// 왼쪽 회전의 구현은 해 줄 필요가 없다. 왼쪽 회전 횟수는 오른쪽 회전 횟수에서 유도할 수 있으니까.

// 뽑아내려고 하는 수를 찾을 때 까지 오른쪽으로 회전하고, 회전 횟수를 센다.
// 왼쪽 회전일 경우 "현재 원소 수" 에서 오른쪽 회전 횟수를 빼는 것으로 연산 횟수를 간단히 구할 수 있다.

// 둘 중 최솟값을 골라 저장해두면 끝.

// 배열의 크기
// 큐는 배열을 써 구현하기로 했다. 따라서 크기를 미리 정해두어야 한다.
// 입력 조건상 필요한 배열의 최대 크기를 계산해보자.

// 배열의 크기를 단순하게 50(입력 최대값)으로 잡으면 안된다.
// 회전 1회당 큐에 원소를 넣기위한 여유 공간이 하나 더 필요하게 된다.
// 즉 처음 입력 크기 + 회전 횟수 만큼의 크기가 필요하다.

// 회전이 가장 많이 발생하는 경우는 뽑아내려고 하는 원소가 맨 뒤에 있는 경우이다.
// 뽑아낸 이후에는 원소의 수가 1개 줄어들기 때문에 n 개의 원소 기준 최대 회전 횟수는 n-1 + n-2 + ... + 1 이 된다.
// 처음 원소를 담을 크기도 필요하니까 필요한 큐의 크기는 다음과 같다.

// ∑𝑘=1𝑛𝑘=𝑛(𝑛+1)/2

// n은 최대 50이므로, 배열의 크기는 25*51 = 1275 이상으로 잡는다.

// 코드
// #include <stdio.h>

// // (Sum of 1 to 50) + 1
// #define MAX_QUEUE_SIZE 1276

// int queue[MAX_QUEUE_SIZE];
// int head = 0;
// int tail = 0;

// int main(void)
// {
//     int size;
//     int num_pops;
//     scanf("%d %d", &size, &num_pops);

//     // Initialize 
//     for (int i = 0; i < size; i++)
//     {
//         queue[i] = i + 1;
//     }
//     tail = size;

//     int rotation_count = 0;
//     for (int i = 0; i < num_pops; i++)
//     {
//         int pop_value;
//         scanf("%d", &pop_value);

//         int right_rotation = 0;

//         // Calculate the minimum rotation count
//         while (queue[head] != pop_value)
//         {
//             queue[tail++] = queue[head++];
//             right_rotation++;
//         }
//         int left_rotation = size - right_rotation;
//         rotation_count += (left_rotation > right_rotation) ? right_rotation : left_rotation;

//         // Pop the value
//         head++;
//         size--;

//     }
//     printf("%d", rotation_count);
// }
// C

// 좋아요공감
// 공유하기게시글 관리
// 구독하기
// TAG
// boj, c, PS, 백준
// 관련글관련글 더보기
// 백준 1158번 요세푸스 문제: C언어 풀이
// 백준 2346번 풍선 터뜨리기: C언어 풀이
// 백준 2161번 카드 1: C언어 풀이
// 백준 24511번 Queuestack: C언어 풀이
// 댓글 0
// 수서곤충의 세계
// 소프트웨어 개발, 프로그래밍에 대한 이야기를 다룹니다.

// 구독하기
// 댓글을 입력해주세요.
// 이름
// 비밀번호
//  비밀글
// 등록
// LINK
// 인기포스트
// SSH로 원격 서버 안전하게 접속 관리하기
// 티스토리 블로그에 마크다운 콜아웃(Callout) 넣어⋯
// 하버드 CS50 프로그래밍 입문 강의 수강 가이드 및 ⋯
// [CS:APP/시스템 프로그래밍] Bomb Lab 풀이
// ABOUT ME
// 소프트웨어 개발, 프로그래밍에 대한 이야기를 다룹니다. 

// ADMIN
// admin 글쓰기


// 크롤링 테스트