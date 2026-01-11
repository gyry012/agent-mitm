# Tool Server
# Agent B의 요청에 따라 tool을 실행

from flask import Flask, request, jsonify
import logging
import os

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [TOOL-SERVER] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/tool/read_file', methods=['POST'])
def read_file_tool():
    # 파일을 읽어 내용을 반환
    try:
        data = request.get_json() or {}
        filename = data.get('parameters', {}).get('filename', 'hello.txt')
        filepath = f'/data/{filename}'

        logger.info("[TOOL-CALL] read_file 호출: %s", filename)

        if not os.path.exists(filepath):
            logger.error("파일을 찾을 수 없음: %s", filepath)
            return jsonify({
                "status": "error",
                "tool_name": "read_file",
                "result": {"error": f"File not found: {filename}"}
            }), 200

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        result = {
            "status": "success",
            "tool_name": "read_file",
            "result": {
                "filename": filename,
                "content": content,
                "size": len(content)
            }
        }
        
        logger.info("[TOOL-RESPONSE] read_file 완료 (크기: %d bytes)", len(content))
        
        return jsonify(result), 200

    except Exception as e:
        logger.error("read_file 실패: %s", e)
        return jsonify({
            "status": "error",
            "tool_name": "read_file",
            "result": {"error": str(e)}
        }), 500


@app.route('/tool/echo', methods=['POST'])
def echo_tool():
    # 받은 메시지를 그대로 반환
    try:
        data = request.get_json() or {}
        message = data.get('parameters', {}).get('message', '')

        logger.info("[TOOL-CALL] echo 호출")

        result = {
            "status": "success",
            "tool_name": "echo",
            "result": {
                "echoed_message": message,
                "message_length": len(message)
            }
        }
        
        logger.info("[TOOL-RESPONSE] echo 완료")

        return jsonify(result), 200

    except Exception as e:
        logger.error("echo 실패: %s", e)
        return jsonify({
            "status": "error",
            "tool_name": "echo",
            "result": {"error": str(e)}
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "tool_server"}), 200


if __name__ == '__main__':
    logger.info("Tool Server 시작 (포트 5002)")
    app.run(host='0.0.0.0', port=5002, debug=False)
