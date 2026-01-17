# 멀티 에이전트 MITM 프록시 통신 관찰

## 목표
Burp Suite를 활용한 MITM 시뮬레이션을 통해 멀티 에이전트 간 통신의 메시지 가로채기 및 변조 가능성 검증

---

## 1. Proxy 개념

### Forward Proxy
클라이언트와 서버 사이에서 클라이언트를 대신하여 요청을 전달하는 중계 서버

**특징**:
- 클라이언트가 프록시 서버를 명시적으로 설정
- 클라이언트의 실제 IP 주소를 숨기고 프록시의 IP로 요청 전송
- 요청/응답 캐싱, 접근 제어, 트래픽 모니터링 가능


### Reverse Proxy
클라이언트와 서버 사이에서 서버를 대신하여 요청을 수신하는 중계 서버

**특징**:
- 실제 백엔드 서버의 존재를 클라이언트로부터 은닉
- 로드 밸런싱, SSL/TLS 종료 지점, 보안 계층 제공
- 서버 인프라 보호 및 성능 최적화


### Transparent Proxy
클라이언트가 프록시의 존재를 인지하지 못하도록 네트워크 계층에서 자동으로 트래픽을 우회시키는 프록시

**특징**:
- 클라이언트 측 설정 불필요
- 네트워크 게이트웨이나 라우터 수준에서 동작
- ISP 레벨 트래픽 모니터링 및 제어

### 본 실습의 프록시 구성
**Forward Proxy (Burp Suite) + 명시적 프록시 설정**

환경변수를 통해 모든 에이전트가 Burp Suite 프록시를 경유하도록 강제 설정. HTTP/HTTPS 트래픽이 프록시를 통과하며 중간에서 관찰 및 조작 가능.

---

## 2. Burp Suite

### 개요
웹 애플리케이션 보안 테스트를 위한 통합 플랫폼으로, HTTP/HTTPS 프로토콜 기반 통신의 가로채기, 분석, 변조 기능을 제공

**주요 용도**: 취약점 스캔, 침투 테스트, 트래픽 분석

### 이번 실습 Proxy 동작 방식 
Forward Proxy로 동작하며, 클라이언트 애플리케이션이 `HTTP_PROXY` 환경변수를 통해 Burp Suite를 프록시로 지정하면 모든 HTTP 요청/응답이 Burp Suite를 경유함!

### 핵심 기능

#### Intercept
HTTP 요청 및 응답을 실시간으로 가로채어 전송 전 수정 가능.

- **Intercept is on**: 모든 트래픽이 중단되며 사용자가 수동으로 전달 또는 수정
- **Intercept is off**: 트래픽은 자동 전달되며 HTTP History에만 기록

#### HTTP History
프록시를 통과한 모든 HTTP 요청/응답의 전체 내역을 시간순으로 기록. 각 항목에 대해 요청 헤더/바디, 응답 헤더/바디, 타이밍 정보 등을 상세 확인 가능.

#### Repeater
기록된 HTTP 요청을 재전송하며 파라미터 수정 및 응답 관찰을 반복 수행. 특정 입력값에 대한 서버 동작 테스트 및 취약점 검증에 활용.


---

## 3. 시스템 아키텍처

### 통신 구조
```
Agent A (Client)
    ↓ [Burp Suite Proxy :8080]
Agent B (Server) 
    ↓ [Burp Suite Proxy :8080]
Tool Server
```

### 프록시 설정
**환경변수 기반 명시적 프록시 구성**
![프록시 설정](https://github.com/user-attachments/assets/2afd85d1-ad28-47a1-b2c6-27a608c41bcd)


---

## 4. 실습

### HTTP history를 통해 각 구간의 패킷 흐름 확인
![HTTP History - a↔b](https://github.com/user-attachments/assets/f16aaf49-df69-40e0-a970-0dfee62c8b73)
![HTTP History - b↔tool](https://github.com/user-attachments/assets/17056858-3a27-41b1-94c5-0668f1748e09)

#### 관찰 가능 구간
1. **Agent A → Agent B**: `POST /process` (prompt 전달)
2. **Agent B → Tool Server**: `POST /tool/{tool_name}` (tool 실행 요청)

---
### repeater 기능을 이용하여 변조해보기 
#### (1) prompt 변조
![Prompt 변조](https://github.com/user-attachments/assets/3b00c1d9-5757-4be8-9222-4fb3004907cc)

#### (2) tool-call 변조 (Response Poisoning)
![Tool-Call 변조 - passwd.txt 읽기](https://github.com/user-attachments/assets/412f6305-f470-41aa-b546-12584d7bd2e3)




---

