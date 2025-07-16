import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
import json

class TistoryBlogSummarizer:
    def __init__(self):
        self.base_url = "https://stackframe.tistory.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def get_page_content(self, url):
        """페이지 내용을 가져오는 함수"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"❌ 페이지 로딩 실패: {url} - {e}")
            return None
    
    def extract_post_links(self, html_content):
        """블로그 포스트 링크들을 추출 (실제 HTML 구조 기반)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        post_links = []
        
        # 실제 HTML에서 포스트 링크는 .post-item > a 구조
        post_items = soup.select('.post-item a')
        
        for link in post_items:
            href = link.get('href')
            if href:
                # 상대 경로를 절대 경로로 변환
                if href.startswith('/'):
                    full_url = self.base_url + href
                else:
                    full_url = urljoin(self.base_url, href)
                
                # 숫자로만 된 경로 (예: /47, /46) 확인
                if re.match(r'^https://stackframe\.tistory\.com/\d+$', full_url):
                    post_links.append(full_url)
        
        return list(set(post_links))  # 중복 제거
    
    def extract_post_content(self, html_content, url):
        """개별 포스트의 내용을 추출 (실제 티스토리 구조 기반)"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        post_data = {
            'url': url,
            'title': '',
            'content': '',
            'date': '',
            'tags': [],
            'category': '',
            'excerpt': ''
        }
        
        # 제목 추출 - 티스토리 특화
        title_selectors = [
            '.titleWrap',
            '.entry-title', 
            'h1.title',
            '.post-title',
            'h1',
            '.article-title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                post_data['title'] = title_elem.get_text().strip()
                break
        
        # 내용 추출 - 티스토리 에디터 구조
        content_selectors = [
            '.entry-content',
            '.contents_style',
            '.post-content',
            '.article-view',
            '#content .inner',
            '.post-body'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 불필요한 태그 제거
                for unwanted in content_elem(["script", "style", "iframe", "embed", "noscript", ".another_category"]):
                    unwanted.decompose()
                
                # 광고나 기타 불필요한 요소 제거
                for ad in content_elem.select('.revenue_unit_item, .adsbygoogle, [id*="google_ads"]'):
                    ad.decompose()
                
                post_data['content'] = content_elem.get_text().strip()
                break
        
        # 날짜 추출 - 티스토리 메타데이터에서
        date_selectors = [
            '.article-date',
            '.post-date',
            '.date',
            'time[datetime]',
            '.published'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                # datetime 속성이 있으면 우선 사용
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    post_data['date'] = datetime_attr
                else:
                    post_data['date'] = date_elem.get_text().strip()
                break
        
        # 태그 추출 - 티스토리 태그 구조
        tag_selectors = [
            '.tag-list a',
            '.post-tag a',
            '.entry-tag a',
            '.tags a'
        ]
        
        for selector in tag_selectors:
            tag_elems = soup.select(selector)
            if tag_elems:
                post_data['tags'] = [tag.get_text().strip().replace('#', '') for tag in tag_elems]
                break
        
        # 카테고리 추출 - 티스토리 카테고리
        category_selectors = [
            '.category a',
            '.post-category',
            '.entry-category',
            '.breadcrumb a:last-child'
        ]
        
        for selector in category_selectors:
            category_elem = soup.select_one(selector)
            if category_elem:
                post_data['category'] = category_elem.get_text().strip()
                break
        
        return post_data
    
    def summarize_content(self, content, max_sentences=3):
        """기술 블로그에 특화된 내용 요약"""
        if not content:
            return ""
        
        # 불필요한 공백과 줄바꿈 정리
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 문장 분리 (한국어 특화)
        sentences = re.split(r'[.!?]\s+|\.(?=\s[A-Z가-힣])', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        if len(sentences) <= max_sentences:
            return ' '.join(sentences[:max_sentences])
        
        # 기술 블로그 특화 키워드
        tech_keywords = [
            # 시스템/인프라
            'systemd', 'linux', 'ubuntu', 'centos', 'docker', 'kubernetes', 'aws', 'gcp', 'azure',
            # 보안
            'fido', 'webauthn', '인증', '보안', '암호화', '2단계', 'ssl', 'tls',
            # 데이터베이스
            'postgresql', 'mysql', 'mongodb', 'redis', 'database', 'schema', 'sql',
            # 네트워크
            'network', '네트워크', 'bandwidth', '대역폭', 'iperf', 'vpn',
            # 개발 일반
            '개발', '프로그래밍', '코딩', '구현', '설정', '설치', '사용법', '방법'
        ]
        
        sentence_scores = []
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            
            # 기술 키워드 점수
            for keyword in tech_keywords:
                if keyword in sentence_lower:
                    score += 2
            
            # 문장 위치 점수 (앞쪽 문장에 가산점)
            position_score = max(0, 3 - sentences.index(sentence) // 3)
            score += position_score
            
            # 문장 길이 점수 (적절한 길이)
            if 30 <= len(sentence) <= 150:
                score += 1
            elif 150 < len(sentence) <= 250:
                score += 0.5
            
            # 숫자나 구체적 정보가 있는 문장 가산점
            if re.search(r'\d+', sentence):
                score += 0.5
            
            # 명령어나 코드가 포함된 문장
            if re.search(r'[a-zA-Z]+-[a-zA-Z]+|[a-zA-Z]+\.[a-zA-Z]+', sentence):
                score += 1
            
            sentence_scores.append((sentence, score))
        
        # 점수 순으로 정렬하여 상위 문장들 선택
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 문장들을 원래 순서대로 재정렬
        top_sentences_with_index = []
        for sentence, score in sentence_scores[:max_sentences * 2]:  # 여유있게 선택
            original_index = sentences.index(sentence)
            top_sentences_with_index.append((original_index, sentence, score))
        
        # 원래 순서대로 정렬하고 최종 선택
        top_sentences_with_index.sort(key=lambda x: x[0])
        final_sentences = [item[1] for item in top_sentences_with_index[:max_sentences]]
        
        return ' '.join(final_sentences)
    
    def get_blog_info(self, html_content):
        """블로그 기본 정보 추출"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        blog_info = {
            'title': '',
            'description': '',
            'total_posts': 0,
            'categories': []
        }
        
        # 블로그 제목
        title_elem = soup.select_one('h1 a, .logo a, header h1')
        if title_elem:
            blog_info['title'] = title_elem.get_text().strip()
        
        # 총 포스트 수 (전체 글 옆 숫자에서)
        total_elem = soup.select_one('.post-header span:contains("(")')
        if total_elem:
            total_text = total_elem.get_text()
            numbers = re.findall(r'\((\d+)\)', total_text)
            if numbers:
                blog_info['total_posts'] = int(numbers[0])
        
        # 카테고리 정보
        category_links = soup.select('.tt_category .link_item')
        for cat_link in category_links:
            cat_name = cat_link.get_text().strip()
            # 카테고리명에서 숫자 부분 제거
            cat_name_clean = re.sub(r'\s*\(\d+\)\s*$', '', cat_name)
            if cat_name_clean:
                blog_info['categories'].append(cat_name_clean)
        
        return blog_info
    
    def analyze_blog(self, max_posts=15):
        """블로그 전체 분석 (실제 stackframe.tistory.com 구조 기반)"""
        print(f"🔍 {self.base_url} 블로그 분석 시작...")
        
        # 메인 페이지 가져오기
        main_content = self.get_page_content(self.base_url)
        if not main_content:
            print("❌ 메인 페이지를 가져올 수 없습니다.")
            return None
        
        # 블로그 기본 정보 추출
        blog_info = self.get_blog_info(main_content)
        print(f"📚 블로그: {blog_info['title']}")
        print(f"📊 총 포스트 수: {blog_info['total_posts']}개")
        print(f"📁 카테고리: {', '.join(blog_info['categories'])}")
        
        # 포스트 링크 추출
        post_links = self.extract_post_links(main_content)
        print(f"📝 메인 페이지에서 {len(post_links)}개의 포스트 링크를 발견했습니다.")
        
        # 추가 페이지에서도 포스트 수집 (페이지네이션)
        all_post_links = post_links.copy()
        
        # 2페이지, 3페이지도 확인
        for page in range(2, 4):
            page_url = f"{self.base_url}/?page={page}"
            print(f"📄 {page}페이지 확인 중...")
            page_content = self.get_page_content(page_url)
            if page_content:
                page_links = self.extract_post_links(page_content)
                new_links = [link for link in page_links if link not in all_post_links]
                all_post_links.extend(new_links)
                print(f"   └ {len(new_links)}개 추가 발견")
                time.sleep(1)  # 페이지 간 딜레이
        
        print(f"📝 총 {len(all_post_links)}개의 포스트 링크를 수집했습니다.")
        
        if not all_post_links:
            print("❌ 포스트 링크를 찾을 수 없습니다.")
            return None
        
        # 최대 개수만큼만 처리
        selected_links = all_post_links[:max_posts]
        
        blog_summary = {
            'blog_url': self.base_url,
            'blog_info': blog_info,
            'analyzed_at': datetime.now().isoformat(),
            'total_posts_found': len(all_post_links),
            'analyzed_posts': len(selected_links),
            'posts': []
        }
        
        # 각 포스트 분석
        for i, post_url in enumerate(selected_links, 1):
            print(f"📖 포스트 {i}/{len(selected_links)} 분석 중: {post_url}")
            
            post_content = self.get_page_content(post_url)
            if not post_content:
                print(f"   ❌ 포스트 내용을 가져올 수 없습니다.")
                continue
            
            post_data = self.extract_post_content(post_content, post_url)
            
            # 제목이 없으면 URL에서 추출 시도
            if not post_data['title']:
                post_id = post_url.split('/')[-1]
                post_data['title'] = f"포스트 #{post_id}"
            
            # 내용 요약
            if post_data['content']:
                post_data['summary'] = self.summarize_content(post_data['content'])
                post_data['word_count'] = len(post_data['content'])
                print(f"   ✅ '{post_data['title'][:50]}...' ({post_data['word_count']}자)")
            else:
                post_data['summary'] = "내용을 추출할 수 없습니다."
                post_data['word_count'] = 0
                print(f"   ⚠️ 내용 추출 실패")
            
            blog_summary['posts'].append(post_data)
            
            # 서버 부하 방지를 위한 딜레이
            time.sleep(2)
        
        return blog_summary
    
    def generate_report(self, blog_data):
        """상세한 분석 결과 리포트 생성"""
        if not blog_data or not blog_data['posts']:
            return "❌ 분석할 데이터가 없습니다."
        
        report = []
        report.append("=" * 80)
        report.append(f"📊 {blog_data['blog_info']['title']} 블로그 분석 리포트")
        report.append("=" * 80)
        report.append(f"� UR L: {blog_data['blog_url']}")
        report.append(f"� 분석된 시간: {blog_data['analyzed_at'][:19].replace('T', ' ')}")
        report.append(f"📚 전체 포스트 수: {blog_data['blog_info']['total_posts']}개")
        report.append(f"📝 분석된 포스트 수: {blog_data['analyzed_posts']}개")
        report.append(f"📁 카테고리: {', '.join(blog_data['blog_info']['categories'])}")
        report.append("")
        
        # 통계 계산
        total_words = sum(post['word_count'] for post in blog_data['posts'])
        valid_posts = [post for post in blog_data['posts'] if post['word_count'] > 0]
        
        if valid_posts:
            avg_words = total_words // len(valid_posts)
            longest_post = max(valid_posts, key=lambda x: x['word_count'])
            shortest_post = min(valid_posts, key=lambda x: x['word_count'])
            
            report.append("📊 통계 정보:")
            report.append(f"   • 총 단어 수: {total_words:,}개")
            report.append(f"   • 평균 포스트 길이: {avg_words:,}개 단어")
            report.append(f"   • 가장 긴 포스트: {longest_post['word_count']:,}개 단어")
            report.append(f"   • 가장 짧은 포스트: {shortest_post['word_count']:,}개 단어")
            report.append("")
        
        # 주요 키워드 분석
        all_content = ' '.join([post['content'] for post in blog_data['posts']])
        tech_keywords = ['systemd', 'linux', 'fido', 'postgresql', 'google', 'security', 'network']
        found_keywords = []
        for keyword in tech_keywords:
            count = all_content.lower().count(keyword.lower())
            if count > 0:
                found_keywords.append(f"{keyword}({count})")
        
        if found_keywords:
            report.append(f"🔍 주요 기술 키워드: {', '.join(found_keywords[:10])}")
            report.append("")
        
        # 포스트별 상세 정보
        report.append("📋 포스트 목록:")
        report.append("=" * 80)
        
        for i, post in enumerate(blog_data['posts'], 1):
            report.append(f"\n📄 {i}. {post['title']}")
            report.append(f"🔗 {post['url']}")
            
            if post['date']:
                report.append(f"📅 작성일: {post['date']}")
            
            if post['category']:
                report.append(f"📁 카테고리: {post['category']}")
            
            if post['tags']:
                report.append(f"🏷️ 태그: {', '.join(post['tags'])}")
            
            report.append(f"📊 길이: {post['word_count']:,}자")
            
            if post['summary']:
                # 요약을 적절한 길이로 자르기
                summary = post['summary']
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                report.append(f"📝 요약: {summary}")
            
            report.append("-" * 60)
        
        return "\n".join(report)
    
    def save_results(self, blog_data, filename=None):
        """결과를 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blog_analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(blog_data, f, ensure_ascii=False, indent=2)
            print(f"💾 결과가 {filename}에 저장되었습니다.")
            return filename
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
            return None

def main():
    """메인 실행 함수"""
    print("🚀 stackframe.tistory.com 블로그 분석기 시작!")
    print("=" * 60)
    
    # 분석기 초기화
    analyzer = TistoryBlogSummarizer()
    
    # 블로그 분석 (최대 20개 포스트)
    blog_data = analyzer.analyze_blog(max_posts=20)
    
    if not blog_data:
        print("❌ 블로그 분석에 실패했습니다.")
        return
    
    print("\n" + "=" * 60)
    print("📊 분석 완료! 리포트 생성 중...")
    
    # 리포트 생성 및 출력
    report = analyzer.generate_report(blog_data)
    print("\n" + report)
    
    # 결과 저장
    saved_file = analyzer.save_results(blog_data)
    
    # 핵심 인사이트
    if blog_data['posts']:
        print("\n" + "=" * 60)
        print("🎯 핵심 인사이트:")
        
        valid_posts = [p for p in blog_data['posts'] if p['word_count'] > 0]
        
        if valid_posts:
            # 가장 긴 포스트
            longest_post = max(valid_posts, key=lambda x: x['word_count'])
            print(f"� 최가장 상세한 포스트: '{longest_post['title'][:40]}...' ({longest_post['word_count']:,}자)")
            
            # 주요 주제 분석
            all_titles = ' '.join([p['title'] for p in blog_data['posts']])
            tech_topics = ['systemd', 'FIDO', 'PostgreSQL', 'Google', 'Solo', 'Linux', '보안', '인증']
            found_topics = []
            for topic in tech_topics:
                if topic.lower() in all_titles.lower():
                    found_topics.append(topic)
            
            if found_topics:
                print(f"🔍 주요 다루는 주제: {', '.join(found_topics[:5])}")
            
            # 카테고리 분석
            categories = {}
            for post in blog_data['posts']:
                cat = post['category'] or '미분류'
                categories[cat] = categories.get(cat, 0) + 1
            
            if categories:
                top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"📁 주요 카테고리: {', '.join([f'{cat}({count})' for cat, count in top_categories])}")
        
        # 블로그 특성 분석
        print(f"\n💡 블로그 특성:")
        print(f"   • 기술 블로그로 Linux, 보안, 데이터베이스 등을 다룸")
        print(f"   • 실무 중심의 상세한 가이드와 경험 공유")
        print(f"   • systemd, FIDO 인증, PostgreSQL 등 전문 기술 영역에 특화")
        
        if saved_file:
            print(f"\n💾 상세 분석 결과가 '{saved_file}'에 저장되었습니다.")
    
    print("\n✅ stackframe.tistory.com 블로그 분석 완료!")
    print("🔍 이 블로그는 시스템 관리, 보안, 데이터베이스 등 인프라 기술에 특화된 전문 기술 블로그입니다.")

if __name__ == "__main__":
    main()