from flask import Flask, request, jsonify
import logging
from datetime import datetime
import os

app = Flask(__name__)

# 로그 폴더 만들기 (없으면 에러남)
os.makedirs('../data/logs', exist_ok=True)

# 로그 파일 설정
logging.basicConfig(
    filename='../data/logs/tool_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# 가짜 은행 계좌 (실제로는 DB 쓰지만 여기선 간단히)
accounts = {
    "user": 10000,   # 사용자: 10000달러
    "alice": 5000,   # Alice: 5000달러
    "bob": 3000      # Bob: 3000달러
}

@app.route('/api/transfer', methods=['POST'])
def transfer():
    """
    송금 API
    누가 POST로 요청하면 → 송금 처리
    """
    # 요청 데이터 받기
    data = request.json
    recipient = data.get('recipient')  # 누구에게
    amount = data.get('amount')        # 얼마
    
    # 로그 남기기 (증거용)
    logging.info(f"요청 받음: {recipient}에게 ${amount}")
    
    # 실제 송금 (숫자 빼기/더하기)
    accounts['user'] -= amount
    accounts[recipient] += amount
    
    # 응답 만들기
    response = {
        "status": "success",
        "recipient": recipient,
        "amount": amount,  # ← 🎯 여기를 Burp가 바꿀거임!
        "sender_balance": accounts['user']
    }
    
    # 로그에 기록
    logging.info(f"실제 송금: ${amount}")
    logging.info(f"응답: {response}")
    
    return jsonify(response)

@app.route('/api/balance', methods=['GET'])
def balance():
    """잔액 보기 (테스트용)"""
    return jsonify(accounts)

if __name__ == '__main__':
    print("🏦 은행 서버 시작!")
    print(f"계좌: {accounts}")
    app.run(port=5000)