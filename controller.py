import json
import os
from datetime import datetime
from typing import Dict, List
from models import (
    Account, Transaction, TransactionHistoryQueue, TransactionType,
    CheckingAccount, SavingsAccount, CreditAccount, AccountFactory
)


class BankController:
    """Controller - управление бизнес-логикой"""

    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._history = TransactionHistoryQueue()
        self._data_file = "bank_data.json"
        self._load_data()

    def run(self):
        from main import BankView
        self._view = BankView()

        while True:
            choice = self._view.show_main_menu()

            if choice == "1":
                self._create_account()
            elif choice == "2":
                self._show_all_accounts()
            elif choice == "3":
                self._deposit()
            elif choice == "4":
                self._withdraw()
            elif choice == "5":
                self._transfer()
            elif choice == "6":
                self._show_all_transactions()
            elif choice == "7":
                self._filter_transactions()
            elif choice == "8":
                self._show_account_info()
            elif choice == "9":
                self._save_data()
                self._view.show_message("Данные сохранены. До свидания!")
                break
            else:
                self._view.show_message("Неверный выбор!", True)

    def _create_account(self):
        try:
            account_type, number, name, initial = self._view.get_account_creation_info()

            if number in self._accounts:
                self._view.show_message("Счет с таким номером уже существует!", True)
                return

            account = AccountFactory.create_account(account_type, number, name, initial)
            self._accounts[number] = account

            if initial > 0:
                transaction = Transaction(number, TransactionType.DEPOSIT, initial, "Начальный депозит")
                self._history.add_transaction(transaction)

            self._view.show_message(f"Счет {account_type} успешно создан! Номер: {number}")
        except Exception as e:
            self._view.show_message(str(e), True)

    def _show_all_accounts(self):
        self._view.show_accounts(list(self._accounts.values()))

    def _deposit(self):
        try:
            account_number, amount = self._view.get_account_and_amount("ДЕПОЗИТ")

            if account_number not in self._accounts:
                self._view.show_message("Счет не найден!", True)
                return

            self._accounts[account_number].deposit(amount)
            transaction = Transaction(account_number, TransactionType.DEPOSIT, amount, "Депозит средств")
            self._history.add_transaction(transaction)

            self._view.show_message(f"Депозит {amount:.2f} ₽ выполнен успешно!")
        except Exception as e:
            self._view.show_message(str(e), True)

    def _withdraw(self):
        try:
            account_number, amount = self._view.get_account_and_amount("СНЯТИЕ")

            if account_number not in self._accounts:
                self._view.show_message("Счет не найден!", True)
                return

            if self._accounts[account_number].withdraw(amount):
                transaction = Transaction(account_number, TransactionType.WITHDRAWAL, amount, "Снятие средств")
                self._history.add_transaction(transaction)
                self._view.show_message(f"Снятие {amount:.2f} ₽ выполнено успешно!")
            else:
                self._view.show_message("Недостаточно средств!", True)
        except Exception as e:
            self._view.show_message(str(e), True)

    def _transfer(self):
        try:
            from_account, to_account, amount = self._view.get_transfer_info()

            if from_account not in self._accounts:
                self._view.show_message("Счет отправителя не найден!", True)
                return

            if to_account not in self._accounts:
                self._view.show_message("Счет получателя не найден!", True)
                return

            if self._accounts[from_account].transfer(self._accounts[to_account], amount):
                transaction = Transaction(from_account, TransactionType.TRANSFER, amount,
                                         f"Перевод на {to_account}", to_account)
                self._history.add_transaction(transaction)
                self._view.show_message(f"Перевод {amount:.2f} ₽ выполнен успешно!")
            else:
                self._view.show_message("Недостаточно средств для перевода!", True)
        except Exception as e:
            self._view.show_message(str(e), True)

    def _show_all_transactions(self):
        self._view.show_transactions(self._history.get_all())

    def _filter_transactions(self):
        self._view.clear_screen()
        print("=== ФИЛЬТРАЦИЯ ТРАНЗАКЦИЙ ===\n")
        print("1. По дате")
        print("2. По типу")
        print("3. По счету")
        choice = input("\nВыберите опцию: ").strip()

        result = None

        if choice == "1":
            from_date, to_date = self._view.get_date_range()
            result = self._history.get_by_date(from_date, to_date)
            self._view.show_transactions(result)
        elif choice == "2":
            trans_type = self._view.get_transaction_type()
            result = self._history.get_by_type(trans_type)
            self._view.show_transactions(result)
        elif choice == "3":
            account_number = self._view.get_user_input("Номер счета")
            result = self._history.get_by_account(account_number)
            self._view.show_transactions(result)
        else:
            self._view.show_message("Неверный выбор!", True)

    def _show_account_info(self):
        account_number = self._view.get_user_input("Введите номер счета")

        if account_number not in self._accounts:
            self._view.show_message("Счет не найден!", True)
            return

        self._view.show_account_info(self._accounts[account_number])

    def _save_data(self):
        try:
            data = {
                "accounts": [],
                "transactions": []
            }

            # Сохраняем счета
            for account in self._accounts.values():
                account_data = account.to_dict()
                account_data["class_name"] = account.__class__.__name__
                data["accounts"].append(account_data)

            # Сохраняем транзакции
            for transaction in self._history.get_all():
                data["transactions"].append(transaction.to_dict())

            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def _load_data(self):
        if not os.path.exists(self._data_file):
            return

        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Загружаем счета
            for account_data in data.get("accounts", []):
                class_name = account_data.pop("class_name")
                account_number = account_data["account_number"]
                owner_name = account_data["owner_name"]
                balance = account_data["balance"]

                if class_name == "CheckingAccount":
                    account = CheckingAccount(account_number, owner_name, balance,
                                             account_data.get("overdraft_limit", 500))
                elif class_name == "SavingsAccount":
                    account = SavingsAccount(account_number, owner_name, balance,
                                            account_data.get("interest_rate", 0.02))
                    account._withdrawals_this_month = account_data.get("withdrawals_this_month", 0)
                elif class_name == "CreditAccount":
                    account = CreditAccount(account_number, owner_name,
                                           account_data.get("credit_limit", 1000),
                                           account_data.get("interest_rate", 0.15))
                    account._credit_used = account_data.get("credit_used", 0)
                else:
                    continue

                self._accounts[account_number] = account

            # Загружаем транзакции
            for trans_data in data.get("transactions", []):
                transaction = Transaction.from_dict(trans_data)
                self._history.add_transaction(transaction)
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
