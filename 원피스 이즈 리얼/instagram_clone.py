from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'instagram-clone-secret-key'

# 데이터 저장용 JSON 파일
DATA_FILE = 'instagram_data.json'

def load_data():
    """데이터 파일에서 데이터 로드"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'users': {},
        'posts': [],
        'comments': {},
        'likes': {}
    }

def save_data(data):
    """데이터를 파일에 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_sample_data():
    """샘플 데이터 초기화"""
    data = load_data()
    if not data['users']:
        # 샘플 사용자들
        sample_users = [
            {'username': 'john_doe', 'name': 'John Doe', 'bio': '📸 Photography enthusiast', 'avatar': '👨‍💻'},
            {'username': 'jane_smith', 'name': 'Jane Smith', 'bio': '✈️ Travel blogger & foodie 🍕', 'avatar': '👩‍🎨'},
            {'username': 'photo_master', 'name': 'Photo Master', 'bio': '🌟 Capturing moments', 'avatar': '📷'},
            {'username': 'travel_lover', 'name': 'Travel Lover', 'bio': '🌍 Exploring the world', 'avatar': '🧳'}
        ]
        
        for user in sample_users:
            data['users'][user['username']] = user
        
        # 샘플 포스트들
        sample_posts = [
            {
                'id': str(uuid.uuid4()),
                'username': 'john_doe',
                'image': '🌅',
                'caption': 'Beautiful sunrise this morning! #sunrise #nature #photography',
                'timestamp': '2024-01-15 08:30',
                'likes': 42,
                'comments_count': 5
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'jane_smith',
                'image': '🍕',
                'caption': 'Pizza night with friends! 🍕✨ #pizza #friends #foodie',
                'timestamp': '2024-01-14 19:45',
                'likes': 38,
                'comments_count': 8
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'photo_master',
                'image': '🌸',
                'caption': 'Spring is coming! Cherry blossoms are so beautiful 🌸 #spring #flowers #nature',
                'timestamp': '2024-01-13 14:20',
                'likes': 67,
                'comments_count': 12
            },
            {
                'id': str(uuid.uuid4()),
                'username': 'travel_lover',
                'image': '🏔️',
                'caption': 'Amazing view from the mountain top! #hiking #nature #adventure',
                'timestamp': '2024-01-12 16:10',
                'likes': 89,
                'comments_count': 15
            }
        ]
        
        data['posts'] = sample_posts
        
        # 샘플 댓글들
        for post in sample_posts:
            post_id = post['id']
            data['comments'][post_id] = [
                {
                    'id': str(uuid.uuid4()),
                    'username': 'jane_smith',
                    'text': 'Amazing shot! 👍',
                    'timestamp': '2024-01-15 09:00'
                },
                {
                    'id': str(uuid.uuid4()),
                    'username': 'photo_master',
                    'text': 'Wow! Where did you take this?',
                    'timestamp': '2024-01-15 09:15'
                }
            ]
        
        save_data(data)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('instagram.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Please enter a username.'}), 400
    
    app_data = load_data()
    
    # 새 사용자 생성
    if username not in app_data['users']:
        app_data['users'][username] = {
            'username': username,
            'name': username.title(),
            'bio': 'New Instagram user! 👋',
            'avatar': '😊'
        }
        save_data(app_data)
    
    session['username'] = username
    return jsonify({'success': True})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/posts')
def get_posts():
    data = load_data()
    posts = data['posts']
    posts.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(posts)

@app.route('/api/posts', methods=['POST'])
def create_post():
    if 'username' not in session:
        return jsonify({'error': 'Login required.'}), 401
    
    data = request.get_json()
    image = data.get('image', '').strip()
    caption = data.get('caption', '').strip()
    
    if not image:
        return jsonify({'error': 'Please select an image.'}), 400
    
    app_data = load_data()
    
    new_post = {
        'id': str(uuid.uuid4()),
        'username': session['username'],
        'image': image,
        'caption': caption,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'likes': 0,
        'comments_count': 0
    }
    
    app_data['posts'].insert(0, new_post)
    app_data['comments'][new_post['id']] = []
    save_data(app_data)
    
    return jsonify(new_post)

@app.route('/api/posts/<post_id>/like', methods=['POST'])
def toggle_like(post_id):
    if 'username' not in session:
        return jsonify({'error': 'Login required.'}), 401
    
    data = load_data()
    username = session['username']
    
    if post_id not in data['likes']:
        data['likes'][post_id] = []
    
    if username in data['likes'][post_id]:
        data['likes'][post_id].remove(username)
        liked = False
    else:
        data['likes'][post_id].append(username)
        liked = True
    
    # 포스트의 좋아요 수 업데이트
    for post in data['posts']:
        if post['id'] == post_id:
            post['likes'] = len(data['likes'][post_id])
            break
    
    save_data(data)
    return jsonify({'liked': liked, 'likes': len(data['likes'][post_id])})

@app.route('/api/posts/<post_id>/comments')
def get_comments(post_id):
    data = load_data()
    comments = data['comments'].get(post_id, [])
    return jsonify(comments)

@app.route('/api/posts/<post_id>/comments', methods=['POST'])
def add_comment(post_id):
    if 'username' not in session:
        return jsonify({'error': 'Login required.'}), 401
    
    request_data = request.get_json()
    text = request_data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'Please enter a comment.'}), 400
    
    data = load_data()
    
    new_comment = {
        'id': str(uuid.uuid4()),
        'username': session['username'],
        'text': text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    if post_id not in data['comments']:
        data['comments'][post_id] = []
    
    data['comments'][post_id].append(new_comment)
    
    # 포스트의 댓글 수 업데이트
    for post in data['posts']:
        if post['id'] == post_id:
            post['comments_count'] = len(data['comments'][post_id])
            break
    
    save_data(data)
    return jsonify(new_comment)

@app.route('/api/user/<username>')
def get_user(username):
    data = load_data()
    user = data['users'].get(username)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    return jsonify(user)

@app.route('/api/current-user')
def get_current_user():
    if 'username' not in session:
        return jsonify({'error': 'Login required.'}), 401
    
    data = load_data()
    user = data['users'].get(session['username'])
    return jsonify(user)

if __name__ == '__main__':
    init_sample_data()
    app.run(debug=True, port=5002)