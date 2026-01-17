# Agent B - 처리 에이전트
# Agent A로부터 prompt를 받아 분석하고, 규칙 기반으로 tool을 선택하여 Tool Server를 호출

from flask import Flask, request, jsonify
import requests
import logging
import os
import urllib3

# SSL 인증서 검증 비활성화 경고 숨기기 (Burp Suite 사용 시)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [AGENT-B] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_prompt_and_select_tool(prompt):
    # 규칙 기반 tool 선택
    # - prompt에 'file' 키워드가 있으면 -> read_file
    # - 그 외 -> echo
    prompt_lower = prompt.lower()

    if 'file' in prompt_lower:
        return 'read_file', {'filename': 'hello.txt'}

    return 'echo', {'message': prompt}


def call_tool(tool_name, tool_params):
    # Tool Server에 tool 호출 요청
    
    proxy_url = os.environ.get('HTTP_PROXY', '')
    proxies = {'http': proxy_url, 'https': proxy_url} if proxy_url else None
    
    if proxy_url:
        tool_server_url = f"http://host.docker.internal:5002/tool/{tool_name}"
        logger.info("[PROXY] 프록시 사용: %s", proxy_url)
    else:
        tool_server_host = os.environ.get('TOOL_SERVER_HOST', 'tool_server')
        tool_server_url = f"http://{tool_server_host}:5002/tool/{tool_name}"

    payload = {
        "tool_name": tool_name,
        "parameters": tool_params
    }

    try:
        logger.info("[TOOL-CALL] Tool 호출: %s", tool_name)
        
        response = requests.post(
            tool_server_url,
            json=payload,
            proxies=proxies,
            verify=False,  # Burp Suite 인증서 검증 비활성화
            timeout=10
        )
        
        response_data = response.json()
        logger.info("[TOOL-RESPONSE] HTTP 상태 코드: %s", response.status_code)
        
        return response_data

    except Exception as e:
        logger.error("Tool 호출 실패: %s", e)
        return {
            "status": "error",
            "tool_name": tool_name,
            "result": {"error": str(e)}
        }

@app.route('/process', methods=['POST'])
def process_prompt():
    # Agent A로부터 prompt를 받아 처리하고 tool 선택
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '')

        logger.info("[PROMPT] Agent A로부터 수신: %s", prompt)

        # 규칙 기반으로 tool 선택
        tool_name, tool_params = analyze_prompt_and_select_tool(prompt)
        logger.info("[TOOL-SELECTION] 선택된 tool: %s", tool_name)
        
        # 선택된 tool로 Tool Server 호출 
        tool_result = call_tool(tool_name, tool_params)

        response = {
            "status": "success",
            "prompt": prompt,
            "selected_tool": tool_name,
            "tool_result": tool_result
        }

        logger.info("[RESPONSE] Agent A로 응답 전송")

        return jsonify(response), 200

    except Exception as e:
        logger.error("요청 처리 실패: %s", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "agent_b"}), 200


if __name__ == '__main__':
    logger.info("Agent B 시작 (포트 5001)")
    app.run(host='0.0.0.0', port=5001, debug=False)
