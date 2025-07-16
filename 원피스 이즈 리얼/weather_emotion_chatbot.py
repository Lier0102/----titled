from flask import Flask, render_template, request, jsonify
import requests
import re
from datetime import datetime

app = Flask(__name__)

# 간단한 감정 분석 (키워드 기반)
EMOTION_KEYWORDS = {
    'happy': ['행복', '기쁘', '좋아', '즐거', '신나', '웃', '만족', '최고', '완벽', '사랑'],
    'sad': ['슬프', '우울', '힘들', '괴로', '아프', '눈물', '외로', '절망', '답답', '속상'],
    'angry': ['화나', '짜증', '분노', '열받', '빡쳐', '미치', '싫어', '스트레스', '억울', '답답'],
    'anxious': ['불안', '걱정', '두려', '무서', '긴장', '떨려', '초조', '조급', '근심', '염려'],
    'tired': ['피곤', '지쳐', '힘없', '졸려', '나른', '무기력', '귀찮', '번아웃', '탈진', '지침'],
    'excited': ['설레', '기대', '흥미', '신기', '재미', '활기', '에너지', '열정', '동기', '의욕']
}

def analyze_emotion(text):
    """간단한 키워드 기반 감정 분석"""
    text = text.lower()
    emotion_scores = {}
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        emotion_scores[emotion] = score
    
    if max(emotion_scores.values()) == 0:
        return 'neutral'
    
    return max(emotion_scores, key=emotion_scores.get)

def get_weather_data():
    """날씨 정보 가져오기 (OpenWeatherMap API 시뮬레이션)"""
    # 실제 API 키가 없으므로 더미 데이터 사용
    # 실제 구현시: api_key = "YOUR_API_KEY"
    # url = f"http://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={api_key}&units=metric&lang=kr"
    
    # 더미 날씨 데이터
    import random
    weather_conditions = ['맑음', '흐림', '비', '눈', '안개']
    temperatures = list(range(-5, 35))
    
    return {
        'condition': random.choice(weather_conditions),
        'temperature': random.choice(temperatures),
        'humidity': random.randint(30, 90),
        'city': '서울'
    }

def generate_response(emotion, weather):
    """감정과 날씨에 따른 맞춤형 응답 생성"""
    responses = {
        'happy': {
            '맑음': f"기분이 좋으시군요! 오늘 날씨도 맑고 ({weather['temperature']}°C) 완벽한 하루네요! 🌞 산책이나 야외활동 어떠세요?",
            '흐림': f"기분은 좋지만 날씨가 흐리네요 ({weather['temperature']}°C). 그래도 좋은 기분으로 실내에서 즐거운 시간 보내세요! ☁️",
            '비': f"기분이 좋으시네요! 비가 오지만 ({weather['temperature']}°C) 빗소리 들으며 따뜻한 차 한 잔 어떠세요? ☔",
            '눈': f"좋은 기분에 눈까지! ({weather['temperature']}°C) 로맨틱한 설경을 즐겨보세요 ❄️",
            '안개': f"기분이 좋으시군요! 안개 낀 날씨지만 ({weather['temperature']}°C) 신비로운 분위기를 만끽해보세요 🌫️"
        },
        'sad': {
            '맑음': f"힘드시겠지만 밖은 맑고 따뜻해요 ({weather['temperature']}°C). 햇볕을 쬐며 잠깐 산책해보세요. 기분이 나아질 거예요 🌞",
            '흐림': f"마음도 날씨도 흐리네요 ({weather['temperature']}°C). 좋아하는 음악 들으며 따뜻한 음료 한 잔 어떠세요? ☁️",
            '비': f"마음이 힘드시군요. 비 오는 날 ({weather['temperature']}°C) 집에서 푹 쉬시고, 좋은 영화나 책으로 위로받으세요 ☔",
            '눈': f"힘든 마음에 눈까지 오네요 ({weather['temperature']}°C). 하지만 새하얀 눈처럼 새로운 시작이 올 거예요 ❄️",
            '안개': f"마음이 안개처럼 답답하시겠어요 ({weather['temperature']}°C). 곧 안개가 걷히듯 마음도 맑아질 거예요 🌫️"
        },
        'angry': {
            '맑음': f"화가 나시는군요. 맑은 날씨 ({weather['temperature']}°C)를 활용해 운동으로 스트레스를 풀어보세요! 🌞",
            '흐림': f"기분이 좋지 않으시군요. 흐린 날씨 ({weather['temperature']}°C)처럼 마음도 무거우시겠어요. 깊게 숨쉬며 진정해보세요 ☁️",
            '비': f"화나는 마음에 비까지 오네요 ({weather['temperature']}°C). 빗소리 들으며 마음을 차분히 가라앉혀보세요 ☔",
            '눈': f"마음이 격해지셨군요. 눈 내리는 고요함 ({weather['temperature']}°C)으로 마음을 진정시켜보세요 ❄️",
            '안개': f"답답한 마음이시군요 ({weather['temperature']}°C). 안개가 걷히듯 화도 곧 가라앉을 거예요 🌫️"
        },
        'anxious': {
            '맑음': f"불안하시군요. 하지만 맑은 하늘 ({weather['temperature']}°C)처럼 마음도 맑아질 거예요. 심호흡하며 산책해보세요 🌞",
            '흐림': f"걱정이 많으시군요. 흐린 날씨 ({weather['temperature']}°C)지만 곧 해가 날 거예요. 따뜻한 차로 마음을 달래보세요 ☁️",
            '비': f"불안한 마음에 비까지 오네요 ({weather['temperature']}°C). 빗소리의 리듬으로 마음을 진정시켜보세요 ☔",
            '눈': f"걱정이 많으시군요 ({weather['temperature']}°C). 눈송이처럼 하나씩 천천히 해결해나가면 돼요 ❄️",
            '안개': f"마음이 안개처럼 불분명하시군요 ({weather['temperature']}°C). 시간이 지나면 모든 게 명확해질 거예요 🌫️"
        },
        'tired': {
            '맑음': f"피곤하시군요. 맑은 날씨 ({weather['temperature']}°C)지만 오늘은 푹 쉬세요. 햇볕만 잠깐 쬐어도 좋아요 🌞",
            '흐림': f"지치셨군요. 흐린 날씨 ({weather['temperature']}°C)에 맞춰 집에서 편안히 쉬세요 ☁️",
            '비': f"피곤한 몸에 비 오는 날 ({weather['temperature']}°C). 빗소리 들으며 깊은 잠에 빠져보세요 ☔",
            '눈': f"지치셨군요 ({weather['temperature']}°C). 눈 내리는 고요한 밤, 따뜻하게 휴식하세요 ❄️",
            '안개': f"몸이 무거우시군요 ({weather['temperature']}°C). 안개처럼 몽롱한 기분, 충분히 쉬세요 🌫️"
        },
        'excited': {
            '맑음': f"설레시는군요! 맑은 날씨 ({weather['temperature']}°C)와 함께 완벽한 하루네요! 뭔가 새로운 걸 시작해보세요 🌞",
            '흐림': f"기대감이 크시군요! 흐린 날씨 ({weather['temperature']}°C)지만 마음은 화창하시네요 ☁️",
            '비': f"설레는 마음이시군요! 비 오는 날 ({weather['temperature']}°C)도 특별한 추억이 될 수 있어요 ☔",
            '눈': f"흥미진진하시군요! 눈 내리는 날 ({weather['temperature']}°C), 뭔가 마법 같은 일이 일어날 것 같아요 ❄️",
            '안개': f"기대가 크시군요 ({weather['temperature']}°C)! 안개 속에서도 새로운 발견이 있을 거예요 🌫️"
        },
        'neutral': {
            '맑음': f"평온한 하루시군요. 맑은 날씨 ({weather['temperature']}°C)를 즐기며 좋은 하루 보내세요 🌞",
            '흐림': f"잔잔한 기분이시군요. 흐린 날씨 ({weather['temperature']}°C)에 맞춰 여유로운 시간 보내세요 ☁️",
            '비': f"차분한 기분이시군요. 비 오는 날 ({weather['temperature']}°C) 실내에서 편안한 시간 보내세요 ☔",
            '눈': f"고요한 마음이시군요. 눈 내리는 평화로운 날 ({weather['temperature']}°C) 즐기세요 ❄️",
            '안개': f"잔잔한 기분이시군요 ({weather['temperature']}°C). 안개 낀 신비로운 분위기를 만끽해보세요 🌫️"
        }
    }
    
    return responses.get(emotion, responses['neutral']).get(weather['condition'], 
           f"오늘 날씨는 {weather['condition']}, 기온은 {weather['temperature']}°C입니다.")

@app.route('/')
def index():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message.strip():
            return jsonify({'error': '메시지를 입력해주세요.'})
        
        # 감정 분석
        emotion = analyze_emotion(user_message)
        
        # 날씨 정보 가져오기
        weather = get_weather_data()
        
        # 맞춤형 응답 생성
        response = generate_response(emotion, weather)
        
        return jsonify({
            'response': response,
            'emotion': emotion,
            'weather': weather,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'error': f'오류가 발생했습니다: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)