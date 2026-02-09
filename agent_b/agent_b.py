import requests
import logging
import os

# 로그 폴더
os.makedirs('../data/logs', exist_ok=True)

# 로그 설정
logging.basicConfig(
    filename='../data/logs/agent_b.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Burp 프록시 설정
USE_PROXY = True  # True면 Burp 통과, False면 직접 연결
PROXY = {'http': 'http://127.0.0.1:8080'} if USE_PROXY else None

class VulnerableAgentB:

    def __init__(self):
        self.server = "http://localhost:5000"
        print(f"Agent B 시작")
        if USE_PROXY:
            print(f"Burp 프록시 사용 중 (127.0.0.1:8080)")
    
    def transfer(self, recipient, amount):
        # 1. 요청 준비
        payload = {
            "recipient": recipient,
            "amount": amount
        }
        
        logging.info(f"요청 보냄: {payload}")
        
        # P 여기서 amount를 저장해야 하는데 안함!
        # expected_amount = amount  ← 이게 없음!
        
        # 2. Tool Server에 요청
        response = requests.post(
            f"{self.server}/api/transfer",
            json=payload,
            proxies=PROXY
        )
        
        # 3. 응답 받기
        data = response.json()
        logging.info(f"응답 받음: {data}")
        
        # 4. 검증 (바보같이 status만 봄)
        if data['status'] == 'success':
            # P 여기서 amount 비교해야 하는데 안함!
            # if data['amount'] != expected_amount:
            #     raise Exception("변조 감지!")
            
            received_amount = data['amount']
            print(f"${received_amount} 송금 완료!")
            return data
        else:
            print(f"송금 실패")
            return None

# 테스트 코드
if __name__ == '__main__':
    agent = VulnerableAgentB()
    agent.transfer("alice", 100)