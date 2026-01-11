# Agent A - 클라이언트 에이전트
# 환경변수로부터 prompt를 받아 Agent B에게 전달

import requests
import logging
import time
import os

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [AGENT-A] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_prompt_to_agent_b(prompt, max_retries=5, retry_delay=3):
    # Agent B에게 prompt를 HTTP POST로 전송 (재시도 로직 포함)
    agent_b_url = "http://agent_b:5001/process"

    payload = {
        "prompt": prompt,
        "from": "agent_a",
        "timestamp": time.time()
    }

    for attempt in range(max_retries):
        try:
            logger.info("[PROMPT] Agent B로 전송 시도 %d/%d: %s", attempt + 1, max_retries, prompt)
            
            response = requests.post(
                agent_b_url,
                json=payload,
                timeout=30
            )

            logger.info("[RESPONSE] HTTP 상태 코드: %s", response.status_code)
            response_data = response.json()
            logger.info("[RESPONSE] 선택된 tool: %s", response_data.get('selected_tool', 'N/A'))
            
            return response_data

        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                logger.warning("연결 실패, %d초 후 재시도... (%s)", retry_delay, e)
                time.sleep(retry_delay)
            else:
                logger.error("연결 오류 (최대 재시도 횟수 초과): %s", e)
        except requests.exceptions.Timeout as e:
            logger.error("요청 타임아웃: %s", e)
            return None
        except Exception as e:
            logger.error("예상치 못한 오류: %s", e)
            return None

    return None


def main():
    logger.info("Agent A 시작")

    prompt = os.environ.get("PROMPT", "Hello, this is a test message")
    logger.info("환경변수에서 prompt 읽음: %s", prompt)

    # Agent B와 Tool Server가 준비될 때까지 대기
    logger.info("Agent B 준비 대기 중...")
    time.sleep(10)

    result = send_prompt_to_agent_b(prompt)
    if not result:
        logger.error("Prompt 전송 실패")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Agent A 종료")


if __name__ == "__main__":
    main()
