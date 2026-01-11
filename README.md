# 멀티 에이전트 HTTP 통신 관찰

## 목표

멀티 에이전트 구조에서 **에이전트 간 HTTP 평문 통신**을 관찰하고, 에이전트의 내부 처리 과정(prompt / tool-call / response)이 **네트워크 메시지 형태로 어떻게 외부에 드러나는지**를 확인합니다.

- Agent 내부 처리 흐름과 네트워크 메시지의 대응 관계 이해
- HTTP payload 내 JSON 필드 의미 분석
- prompt / tool-call / response 구분

## 프로젝트 구조

```
agent-http/
├── agent_a/              # Agent A (Client)
│   ├── agent_a.py
│   └── Dockerfile
├── agent_b/              # Agent B (Server)
│   ├── agent_b.py
│   └── Dockerfile
├── tool_server/          # Tool Server
│   ├── tool_server.py
│   └── Dockerfile
├── data/                 # 공유 데이터
│   └── hello.txt
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 아키텍처

```
┌──────────┐         ┌──────────┐         ┌──────────────┐
│ Agent A  │────────▶│ Agent B  │────────▶│ Tool Server  │
│ (Client) │  HTTP   │ (Server) │  HTTP   │              │
└──────────┘         └──────────┘         └──────────────┘
     │                    │                       │
     │  [PROMPT]          │  [TOOL-CALL]         │
     │                    │                       │
     │◀───────────────────│◀──────────────────────│
     │  [RESPONSE]        │  [TOOL-RESPONSE]      │
```

## 코드 구조 설명

### 각 컴포넌트 역할

- **Agent A**: 환경변수 `PROMPT`로 입력을 받아 Agent B에게 전달
- **Agent B**: prompt를 분석하여 규칙 기반으로 tool 선택 (prompt에 'file' 있으면 read_file, 없으면 echo)
- **Tool Server**: Agent B의 요청에 따라 tool 실행

### Prompt / Tool-Call / Response 구분

**1. Prompt (Agent A → Agent B)**

**2. Tool-Call (Agent B → Tool Server)**

**3. Response (Tool Server → Agent B → Agent A)**


## 실행 방법

### 1. Docker Compose 실행

```powershell
docker-compose up --build
```

### 2. Wireshark 캡처 설정

1. Wireshark 실행 
2. 인터페이스: **"Adapter for loopback traffic capture"** 선택
3. 필터: `tcp.port == 5001 || tcp.port == 5002`
4. 캡처 시작

### 3. 테스트 요청

**PowerShell에서:**

#### 1. read_file tool 테스트
```powershell
$body = @{prompt="Please read the file"; from="agent_a"; timestamp=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5001/process -Method POST -Body $body -ContentType "application/json"
```

**Wireshark HTTP 패킷 캡처:**
![Wireshark HTTP 패킷 캡처](https://github.com/user-attachments/assets/6cbcde7c-2702-4c23-b289-91854ff4e2ae)

연두색 HTTP 패킷 4개:
1. POST /process (포트 5001) A -> B
2. POST /tool/read_file (포트 5002) B -> Tool Server
3. HTTP 200 OK (포트 5002) Tool Server -> B
4. HTTP 200 OK (포트 5001) B -> A

#### 2. echo tool 테스트
```powershell
$body = @{prompt="Hello test"; from="agent_a"; timestamp=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:5001/process -Method POST -Body $body -ContentType "application/json"
```

**Wireshark HTTP 패킷 캡처:**
![echo tool 테스트](https://github.com/user-attachments/assets/642d30f5-37ce-4ade-ae19-7f842605c161)


### 3. HTTP Payload 내 JSON 필드 분석 (read_file)

**캡처 방법:** Wireshark에서 HTTP 패킷 선택 → Follow → HTTP Stream

**분석 내용:**

![HTTP Payload JSON 분석](https://github.com/user-attachments/assets/f4899fae-dba8-45e7-9e50-3607f911fa92)

**Prompt 단계 (POST /process):**
```json
{
  "from": "agent_a",                 // 발신자
  "timestamp": 1768102409,        // 요청 시각
  "prompt": "Please read the file"  // 사용자 입력
}
```

**Tool-Call 단계 (POST /tool/read_file):**

![Tool-Call JSON](https://github.com/user-attachments/assets/15cd4c10-0eda-4e2c-9c65-79378ca5827d)

```json
{
  "tool_name": "read_file",           // 선택된 tool
  "parameters": {
    "filename": "hello.txt"          // tool 매개변수
  }
}
```

**Response 단계:**
사진 아래쪽의 파란색 부분을 보면 성공적으로 작동했다는 것을 확인할 수 있다. 

---
### 4. Prompt 값 변경 후 Tool-Call 변화 (read_file vs echo)

**echo tool HTTP Payload:**
![echo HTTP Payload](https://github.com/user-attachments/assets/b4befdae-a574-405d-927e-136279e85273)

**비교 스크린샷:**
![Prompt 변경 Tool-Call 변화](https://github.com/user-attachments/assets/b4281f92-558c-4853-bf50-fb0b15bac340)


**비교 내용:**

| Prompt | URL | tool_name | parameters |
|--------|-----|-----------|------------|
| "Please read the file" | `/tool/read_file` | `"read_file"` | `{"filename": "hello.txt"}` |
| "Hello test" | `/tool/echo` | `"echo"` | `{"message": "Hello test"}` |

**관찰:** prompt에 'file' 키워드 유무에 따라 Agent B가 다른 tool을 선택하고, 이는 HTTP 요청의 URL과 JSON payload로 드러남



## 정리

**컨테이너 중지 및 제거:**
```powershell
docker-compose down
```

**이미지까지 삭제하려면:**
```powershell
docker-compose down --rmi all
```



## 결론

에이전트의 내부 처리 과정(prompt 분석, tool 선택)이 네트워크 메시지로 드러남을 확인:
- Prompt → HTTP POST 요청의 JSON body
- Tool 선택 로직 → HTTP 요청의 URL과 JSON payload
- Tool 실행 결과 → HTTP 응답의 JSON body

모든 내부 처리 과정이 네트워크 패킷 레벨에서 관찰 가능함을 확인.

## 참고 사항

- 처음에는 Docker 내부 네트워크(172.18.0.x)를 직접 캡처하려고 했는데 이유는 모르겠지만 잘 안됐다. 
- 그래서 일단 호스트 포트(5001, 5002)를 통해 통신을 캡쳐했다. 나중에 왜 안됐는지 찾아봐야겠다. 

