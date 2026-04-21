# 📊 EFK Stack — Bank Transaction Logger

> A minimal EFK (Elasticsearch + Fluentd + Kibana) stack with a structured JSON log generator simulating bank transactions.

---

## 💡 Concept

A Python app simulates a bank processing system and emits structured JSON logs at three levels:

| Level | Share | Scenario |
|-------|-------|----------|
| `INFO` | 70% | Transaction approved |
| `WARNING` | 18% | Suspicious activity (large amount, unusual country, etc.) |
| `ERROR` | 12% | Transaction declined (insufficient funds, blocked card, etc.) |

Logs flow: **App → Docker Fluentd driver → Fluentd → Elasticsearch → Kibana**

---

## 🏗️ Architecture

```
efk-stack/
├── docker-compose.yml
├── fluentd/
│   ├── Dockerfile          # installs fluent-plugin-elasticsearch
│   └── conf/
│       └── fluent.conf     # parses JSON logs, ships to Elasticsearch
└── app/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py             # bank transaction log generator
```

### Log pipeline

```
[Python app]
    │  stdout (JSON)
    ▼
[Docker fluentd logging driver]  →  port 24224
    ▼
[Fluentd]  parses JSON, tags as bank.app
    ▼
[Elasticsearch]  index: bank-logs-YYYY.MM.DD
    ▼
[Kibana]  http://localhost:5601
```

---

## 🚀 Running

```bash
docker compose up --build -d
```

Check all containers are up:

```bash
docker compose ps
```

Expected:

```
elasticsearch   running
kibana          running
fluentd         running
bank-logger     running
```

---

## 🌐 Kibana Setup (first launch)

1. Open **http://localhost:5601**
2. Go to **Management → Stack Management → Index Patterns**
3. Click **Create index pattern**
4. Enter `bank-logs-*` → **Next step**
5. Select `@timestamp` as the time field → **Create index pattern**
6. Go to **Discover** — logs appear within ~30 seconds of startup

---

## 🔍 Useful Kibana Filters

Filter by log level:
```
levelname : "ERROR"
levelname : "WARNING"
```

Filter by transaction status:
```
status : "declined"
status : "flagged"
```

Filter by error reason:
```
error_reason : "insufficient_funds"
warning_reason : "large_amount"
```

Filter by country:
```
country : "US"
```

Filter by amount range — use the **Add filter** UI:
- Field: `amount`, Operator: `is between`, Values: `10000` to `50000`

---

## 📋 Log Fields Reference

| Field | Description | Example |
|-------|-------------|---------|
| `levelname` | Log level | `INFO`, `WARNING`, `ERROR` |
| `message` | Human-readable event | `Transaction approved` |
| `transaction_id` | Short unique TX id | `A1B2C3D4` |
| `type` | Transaction type | `transfer`, `payment`, `withdrawal` |
| `amount` | Amount in currency | `4200.50` |
| `currency` | Currency code | `UAH`, `USD`, `EUR` |
| `merchant` | Merchant name | `Silpo`, `Nova Poshta` |
| `card_last4` | Last 4 digits of card | `4242` |
| `user_id` | Internal user ID | `USR-1337` |
| `country` | Operation country | `UA`, `PL`, `US` |
| `status` | Transaction result | `approved`, `declined`, `flagged` |
| `error_reason` | Decline reason (ERROR) | `insufficient_funds` |
| `warning_reason` | Flag reason (WARNING) | `large_amount` |
| `risk_score` | Risk score 0–1 (WARNING) | `0.82` |
| `latency_ms` | Processing time (INFO) | `210` |

---

## ⏹️ Stop / Restart

```bash
# Stop
docker compose down

# Start again (after reboot)
docker compose up -d
```

---

## 📋 Requirements

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) plugin
- ~2 GB RAM free (Elasticsearch needs at least 1 GB)
