from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        # 보안을 위해 허용된 문자만 사용
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return jsonify({'error': '허용되지 않은 문자가 포함되어 있습니다.'})
        
        # 계산 실행
        result = eval(expression)
        return jsonify({'result': result})
    
    except ZeroDivisionError:
        return jsonify({'error': '0으로 나눌 수 없습니다.'})
    except Exception as e:
        return jsonify({'error': '잘못된 수식입니다.'})

if __name__ == '__main__':
    app.run(debug=True)