import requests
import logging
import uuid
import os
from datetime import datetime

# 로그 폴더 생성
os.makedirs('../data/logs', exist_ok=True)

# 일반 로그
logging.basicConfig(
    filename='../data/logs/agent_b_secure.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# 보안 로그 (별도)
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)
security_handler = logging.FileHandler('../data/logs/security.log')
security_handler.setFormatter(logging.Formatter(
    '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
))
security_logger.addHandler(security_handler)

# Burp 프록시
USE_PROXY = True
PROXY = {'http': 'http://127.0.0.1:8080'} if USE_PROXY else None

class SecurityAlert(Exception):
    """보안 위협 탐지 시 발생하는 예외"""
    pass

class SecureAgentB:
    
    def __init__(self):
        self.server = "http://localhost:5000"
        self.intent_store = {}  # 핵심! 요청 의도 저장소
        
        print(f"🛡️  Secure Agent B 시작")
        if USE_PROXY:
            print(f"⚠️  Burp 프록시 사용 중 (127.0.0.1:8080)")
        print(f"✅ 방어 메커니즘: Intent Store + Consistency Check")
        print()
    
    def transfer(self, recipient, amount):
        """
        핵심 방어:
        1. 요청 전송 전 → Intent Store에 저장
        2. 응답 수신 후 → 저장된 값과 비교
        3. 불일치 발견 → SecurityAlert 발생
        """
        # 고유 ID 생성
        request_id = f"req_{str(uuid.uuid4())[:8]}"
        
        # 1단계: Intent 저장 (핵심!)
        self.intent_store[request_id] = {
            "action": "transfer",
            "recipient": recipient,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
        
        logging.info(f"[{request_id}] 🔒 Intent 저장")
        logging.info(f"[{request_id}] Expected: recipient={recipient}, amount={amount}")
        
        # 요청 준비
        payload = {
            "recipient": recipient,
            "amount": amount,
            "request_id": request_id
        }
        
        logging.info(f"[{request_id}] 요청 보냄: {payload}")
        
        try:
            # 2단계: 요청 전송
            response = requests.post(
                f"{self.server}/api/transfer",
                json=payload,
                proxies=PROXY,
                timeout=60
            )
            
            data = response.json()
            logging.info(f"[{request_id}] 응답 받음: {data}")
            
            # 3단계: 상태 확인
            if data.get('status') != 'success':
                logging.error(f"[{request_id}] 송금 실패: {data.get('message')}")
                return {
                    "success": False,
                    "message": data.get('message', 'Transfer failed')
                }
            
            # 4단계: 핵심! 일관성 검증
            expected_intent = self.intent_store[request_id]
            
            # 4-1. Amount 검증
            expected_amount = expected_intent["amount"]
            received_amount = data.get("amount")
            
            if expected_amount != received_amount:
                # 변조 탐지
                alert_msg = (
                    f"RESPONSE TAMPERING DETECTED!\n"
                    f"Request ID: {request_id}\n"
                    f"Expected Amount: ${expected_amount}\n"
                    f"Received Amount: ${received_amount}\n"
                    f"Difference: ${received_amount - expected_amount}\n"
                    f"Timestamp: {datetime.now().isoformat()}"
                )
                
                security_logger.critical(alert_msg)
                logging.error(f"[{request_id}] ❌ Amount 변조 탐지!")
                
                print(f"\n{'='*60}")
                print(f"🚨 보안 경고: 응답 변조 탐지!")
                print(f"{'='*60}")
                print(f"예상 금액: ${expected_amount}")
                print(f"수신 금액: ${received_amount}")
                print(f"차이: ${received_amount - expected_amount}")
                print(f"{'='*60}\n")
                
                raise SecurityAlert(
                    f"Amount mismatch! Expected {expected_amount}, "
                    f"got {received_amount}"
                )
            
            # 4-2. Recipient 검증
            expected_recipient = expected_intent["recipient"]
            received_recipient = data.get("recipient")
            
            if expected_recipient != received_recipient:
                # 수신자 변조 탐지!
                alert_msg = (
                    f"RECIPIENT TAMPERING DETECTED!\n"
                    f"Request ID: {request_id}\n"
                    f"Expected Recipient: {expected_recipient}\n"
                    f"Received Recipient: {received_recipient}\n"
                    f"Timestamp: {datetime.now().isoformat()}"
                )
                
                security_logger.critical(alert_msg)
                logging.error(f"[{request_id}] ❌ Recipient 변조 탐지!")
                
                raise SecurityAlert(
                    f"Recipient mismatch! Expected {expected_recipient}, "
                    f"got {received_recipient}"
                )
            
            # 5단계: 검증 통과
            logging.info(f"[{request_id}] 일관성 검증 통과")
            logging.info(f"[{request_id}] Amount: {expected_amount} == {received_amount}")
            logging.info(f"[{request_id}] Recipient: {expected_recipient} == {received_recipient}")
            
            # Intent Store 정리
            del self.intent_store[request_id]
            
            print(f" ${received_amount} 송금 완료 (검증됨)")
            
            return {
                "success": True,
                "message": f"${received_amount} transferred to {received_recipient}",
                "amount": received_amount,
                "recipient": received_recipient,
                "balance": data.get("sender_balance"),
                "validated": True  # 검증 완료 표시
            }
            
        except requests.exceptions.ProxyError:
            logging.error(f"[{request_id}] Burp 프록시 연결 실패")
            return {
                "success": False,
                "message": "Proxy error: Make sure Burp Suite is running!"
            }
        except SecurityAlert as e:
            # 보안 경고는 그대로 전파
            raise
        except Exception as e:
            logging.error(f"[{request_id}] 예외 발생: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }

def demo():
    """방어 테스트 데모"""
    print("\n" + "=" * 60)
    print("🛡️  Secure Agent B - 방어 테스트")
    print("=" * 60)
    print()
    
    agent = SecureAgentB()
    
    print("📋 테스트 시나리오:")
    print("   1. Alice에게 $100 송금 요청")
    print("   2. Tool Server는 $100 처리")
    print("   3. Burp가 응답을 $1000으로 변조")
    print("   4. Agent가 변조 탐지 예상")
    print()
    
    try:
        print("[실행] $100 송금 시도...\n")
        result = agent.transfer("alice", 100)
        
        if result["success"]:
            print(f"\n결과: {result['message']}")
            print(f"잔액: ${result['balance']}")
            print(f"검증 완료: {result.get('validated', False)}")
    
    except SecurityAlert as e:
        print(f"\n🚨 보안 경고 발생!")
        print(f"상세: {str(e)}")
        print(f"\n✅ 방어 성공! 응답 변조를 탐지했습니다.")
    
    print("\n" + "=" * 60)
    print("📝 로그 확인:")
    print("   일반 로그: ../data/logs/agent_b_secure.log")
    print("   보안 로그: ../data/logs/security.log")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    demo()