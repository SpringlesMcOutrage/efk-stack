"""
Bank Transaction Logger
=======================
Симулятор банківських транзакцій.
Генерує структуровані JSON-логи трьох рівнів:
  INFO    — успішна транзакція
  WARNING — підозріла активність (велика сума, часті операції)
  ERROR   — відхилена транзакція (недостатньо коштів, заблокована картка)

Логи надходять у stdout → Docker fluentd driver → Fluentd → Elasticsearch → Kibana.
"""

import logging
import random
import time
from pythonjsonlogger import jsonlogger
from faker import Faker

fake = Faker("uk_UA")

# ── JSON logger setup ─────────────────────────────────────────────────────────

logger = logging.getLogger("bank")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# ── Constants ─────────────────────────────────────────────────────────────────

TRANSACTION_TYPES = ["transfer", "payment", "withdrawal", "deposit", "purchase"]
CURRENCIES        = ["UAH", "USD", "EUR"]
MERCHANTS         = [
    "Silpo", "Nova Poshta", "Rozetka", "Monobank", "YASNO",
    "McDonald's", "Uber", "Steam", "Netflix", "АЗС WOG",
]
ERROR_REASONS = [
    "insufficient_funds",
    "card_blocked",
    "daily_limit_exceeded",
    "invalid_cvv",
    "expired_card",
]
WARNING_REASONS = [
    "large_amount",
    "unusual_country",
    "frequent_transactions",
    "night_operation",
]

# ── Simulation helpers ────────────────────────────────────────────────────────

def random_amount(min_=10, max_=50000):
    return round(random.uniform(min_, max_), 2)

def make_transaction():
    return {
        "transaction_id": fake.uuid4()[:8].upper(),
        "type":           random.choice(TRANSACTION_TYPES),
        "currency":       random.choice(CURRENCIES),
        "merchant":       random.choice(MERCHANTS),
        "card_last4":     str(random.randint(1000, 9999)),
        "user_id":        f"USR-{random.randint(1000, 9999)}",
        "ip":             fake.ipv4(),
        "country":        random.choice(["UA", "UA", "UA", "PL", "DE", "US"]),
    }

# ── Log emitters ──────────────────────────────────────────────────────────────

def log_success():
    tx = make_transaction()
    amount = random_amount(10, 5000)
    logger.info(
        "Transaction approved",
        extra={
            **tx,
            "amount":  amount,
            "status":  "approved",
            "latency_ms": random.randint(80, 400),
        },
    )

def log_warning():
    tx = make_transaction()
    amount = random_amount(10000, 50000)
    reason = random.choice(WARNING_REASONS)
    logger.warning(
        f"Suspicious activity detected: {reason}",
        extra={
            **tx,
            "amount":         amount,
            "status":         "flagged",
            "warning_reason": reason,
            "risk_score":     round(random.uniform(0.6, 0.9), 2),
        },
    )

def log_error():
    tx = make_transaction()
    amount = random_amount(100, 20000)
    reason = random.choice(ERROR_REASONS)
    logger.error(
        f"Transaction declined: {reason}",
        extra={
            **tx,
            "amount":       amount,
            "status":       "declined",
            "error_reason": reason,
            "retry":        False,
        },
    )

# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    logger.info("Bank Transaction Logger started", extra={"service": "bank-logger", "version": "1.0.0"})

    while True:
        roll = random.random()

        if roll < 0.70:       # 70% — успішні транзакції
            log_success()
        elif roll < 0.88:     # 18% — попередження
            log_warning()
        else:                 # 12% — помилки
            log_error()

        # Іноді кілька транзакцій підряд (burst)
        if random.random() < 0.15:
            for _ in range(random.randint(2, 5)):
                log_success()
                time.sleep(0.1)

        time.sleep(random.uniform(1.5, 4.0))

if __name__ == "__main__":
    main()
