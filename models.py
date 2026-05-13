import json
from datetime import datetime
from enum import Enum
from collections import deque
from typing import List, Optional, Iterator

# ==================== ENUMS ====================
class TransactionType(Enum):
    DEPOSIT = "Депозит"
    WITHDRAWAL = "Снятие"
    TRANSFER = "Перевод"
    INTEREST = "Начисление процентов"
    FEE = "Комиссия"


# ==================== TRANSACTION ====================
class Transaction:
    """Модель транзакции"""

    def __init__(self, account_number: str, transaction_type: TransactionType,
                 amount: float, description: str = "", destination_account: str = None):
        self.transaction_id = str(abs(hash(f"{account_number}{datetime.now()}{amount}")))[:8]
        self.account_number = account_number
        self.destination_account = destination_account
        self.type = transaction_type
        self.amount = amount
        self.date = datetime.now()
        self.description = description

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "account_number": self.account_number,
            "destination_account": self.destination_account,
            "type": self.type.value,
            "amount": self.amount,
            "date": self.date.isoformat(),
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        transaction = cls(
            data["account_number"],
            TransactionType(data["type"]),
            data["amount"],
            data["description"],
            data.get("destination_account")
        )
        transaction.transaction_id = data["transaction_id"]
        transaction.date = datetime.fromisoformat(data["date"])
        return transaction

    def __str__(self):
        dest = f" → {self.destination_account}" if self.destination_account else ""
        return f"[{self.date.strftime('%Y-%m-%d %H:%M:%S')}] {self.type.value:10} | {self.account_number}{dest:10} | {self.amount:10.2f} ₽ | {self.description}"


# ==================== TRANSACTION QUEUE ====================
class TransactionHistoryQueue:
    """Очередь для хранения истории транзакций"""

    def __init__(self, max_size: int = 100):
        self._transactions = deque(maxlen=max_size)

    def add_transaction(self, transaction: Transaction):
        self._transactions.append(transaction)

    def get_all(self) -> List[Transaction]:
        return list(self._transactions)

    def get_by_date(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        return [t for t in self._transactions if start_date <= t.date <= end_date]

    def get_by_type(self, transaction_type: TransactionType) -> List[Transaction]:
        return [t for t in self._transactions if t.type == transaction_type]

    def get_by_account(self, account_number: str) -> List[Transaction]:
        return [t for t in self._transactions if t.account_number == account_number]

    def clear(self):
        self._transactions.clear()

    def __len__(self):
        return len(self._transactions)


# ==================== BASE ACCOUNT ====================
class Account:
    """Базовый класс для всех счетов"""

    def __init__(self, account_number: str, owner_name: str, initial_balance: float):
        self.account_number = account_number
        self.owner_name = owner_name
        self._balance = initial_balance
        self.account_type = "Базовый счет"

    @property
    def balance(self) -> float:
        return self._balance

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if self._balance >= amount:
            self._balance -= amount
            return True
        return False

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        self._balance += amount

    def transfer(self, destination: 'Account', amount: float) -> bool:
        if self.withdraw(amount):
            destination.deposit(amount)
            return True
        return False

    def get_available_funds(self) -> float:
        return self._balance

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "owner_name": self.owner_name,
            "balance": self._balance,
            "account_type": self.account_type
        }

    def __str__(self):
        return f"{self.account_type}: {self.account_number} - {self.owner_name} - {self._balance:.2f} ₽"


# ==================== CHECKING ACCOUNT ====================
class CheckingAccount(Account):
    """Расчетный счет с овердрафтом"""

    def __init__(self, account_number: str, owner_name: str, initial_balance: float, overdraft_limit: float = 500):
        super().__init__(account_number, owner_name, initial_balance)
        self.account_type = "Расчетный счет"
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if self._balance + self.overdraft_limit >= amount:
            self._balance -= amount
            return True
        return False

    def get_available_funds(self) -> float:
        return self._balance + self.overdraft_limit

    def to_dict(self):
        data = super().to_dict()
        data["overdraft_limit"] = self.overdraft_limit
        return data


# ==================== SAVINGS ACCOUNT ====================
class SavingsAccount(Account):
    """Сберегательный счет с ограничением на снятие"""

    MAX_FREE_WITHDRAWALS = 3

    def __init__(self, account_number: str, owner_name: str, initial_balance: float, interest_rate: float = 0.02):
        super().__init__(account_number, owner_name, initial_balance)
        self.account_type = "Сберегательный счет"
        self.interest_rate = interest_rate
        self._withdrawals_this_month = 0

    def withdraw(self, amount: float) -> bool:
        if self._withdrawals_this_month >= self.MAX_FREE_WITHDRAWALS:
            raise Exception("Превышен лимит бесплатных снятий в этом месяце")

        if super().withdraw(amount):
            self._withdrawals_this_month += 1
            return True
        return False

    def add_interest(self):
        interest = self._balance * self.interest_rate
        self._balance += interest

    def get_available_funds(self) -> float:
        return self._balance

    def reset_monthly_withdrawals(self):
        self._withdrawals_this_month = 0

    def to_dict(self):
        data = super().to_dict()
        data["interest_rate"] = self.interest_rate
        data["withdrawals_this_month"] = self._withdrawals_this_month
        return data


# ==================== CREDIT ACCOUNT ====================
class CreditAccount(Account):
    """Кредитный счет"""

    def __init__(self, account_number: str, owner_name: str, credit_limit: float, interest_rate: float = 0.15):
        super().__init__(account_number, owner_name, 0)
        self.account_type = "Кредитный счет"
        self.credit_limit = credit_limit
        self.interest_rate = interest_rate
        self._credit_used = 0

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        available = self._balance + (self.credit_limit - self._credit_used)
        if available >= amount:
            if self._balance >= amount:
                self._balance -= amount
            else:
                remaining = amount - self._balance
                self._balance = 0
                self._credit_used += remaining
            return True
        return False

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        if self._credit_used > 0:
            if amount >= self._credit_used:
                amount -= self._credit_used
                self._credit_used = 0
                self._balance += amount
            else:
                self._credit_used -= amount
        else:
            self._balance += amount

    def calculate_interest(self):
        interest = self._credit_used * self.interest_rate
        self._credit_used += interest

    def get_available_funds(self) -> float:
        return self._balance + (self.credit_limit - self._credit_used)

    def to_dict(self):
        data = super().to_dict()
        data["credit_limit"] = self.credit_limit
        data["interest_rate"] = self.interest_rate
        data["credit_used"] = self._credit_used
        return data


# ==================== ACCOUNT FACTORY ====================
class AccountFactory:
    """Фабрика для создания счетов"""

    @staticmethod
    def create_account(account_type: str, account_number: str, owner_name: str,
                      initial_balance: float = 0, **kwargs) -> Account:
        if account_type == "Checking":
            overdraft_limit = kwargs.get("overdraft_limit", 500)
            return CheckingAccount(account_number, owner_name, initial_balance, overdraft_limit)
        elif account_type == "Savings":
            interest_rate = kwargs.get("interest_rate", 0.02)
            return SavingsAccount(account_number, owner_name, initial_balance, interest_rate)
        elif account_type == "Credit":
            credit_limit = kwargs.get("credit_limit", initial_balance if initial_balance > 0 else 1000)
            interest_rate = kwargs.get("interest_rate", 0.15)
            return CreditAccount(account_number, owner_name, credit_limit, interest_rate)
        else:
            raise ValueError(f"Неизвестный тип счета: {account_type}")
