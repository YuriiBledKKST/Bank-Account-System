import os
import sys
from datetime import datetime
from models import Account, CheckingAccount, SavingsAccount, CreditAccount, TransactionType

class BankView:
    """View - интерфейс взаимодействия с пользователем"""

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def show_main_menu():
        BankView.clear_screen()
        print("╔══════════════════════════════════════╗")
        print("║     BANK ACCOUNT SYSTEM             ║")
        print("╠══════════════════════════════════════╣")
        print("║ 1. Создать новый счет               ║")
        print("║ 2. Просмотреть все счета            ║")
        print("║ 3. Внести депозит                   ║")
        print("║ 4. Снять средства                   ║")
        print("║ 5. Перевести между счетами          ║")
        print("║ 6. История транзакций               ║")
        print("║ 7. Фильтрация транзакций            ║")
        print("║ 8. Информация о счете               ║")
        print("║ 9. Сохранить и выйти                ║")
        print("╚══════════════════════════════════════╝")
        return input("\nВыберите опцию: ").strip()

    @staticmethod
    def show_message(message, is_error=False):
        if is_error:
            print(f"\n❌ Ошибка: {message}")
        else:
            print(f"\n✅ {message}")
        input("\nНажмите Enter для продолжения...")

    @staticmethod
    def get_user_input(prompt):
        return input(f"{prompt}: ").strip()

    @staticmethod
    def get_decimal_input(prompt):
        while True:
            try:
                value = float(input(f"{prompt}: ").strip())
                if value > 0:
                    return value
                print("Сумма должна быть положительной!")
            except ValueError:
                print("Пожалуйста, введите корректное число!")

    @staticmethod
    def show_accounts(accounts):
        BankView.clear_screen()
        print("=== СПИСОК СЧЕТОВ ===\n")
        if not accounts:
            print("Нет доступных счетов.")
        else:
            for account in accounts:
                print(f"┌─────────────────────────────────")
                print(f"│ {account}")
                print(f"│ Доступно: {account.get_available_funds():.2f} ₽")
                print(f"└─────────────────────────────────\n")
        input("\nНажмите Enter для продолжения...")

    @staticmethod
    def show_account_info(account):
        BankView.clear_screen()
        print("=== ИНФОРМАЦИЯ О СЧЕТЕ ===\n")
        print(f"Тип счета: {account.account_type}")
        print(f"Номер счета: {account.account_number}")
        print(f"Владелец: {account.owner_name}")
        print(f"Текущий баланс: {account.balance:.2f} ₽")
        print(f"Доступно средств: {account.get_available_funds():.2f} ₽")
        input("\nНажмите Enter для продолжения...")

    @staticmethod
    def show_transactions(transactions):
        BankView.clear_screen()
        print("=== ИСТОРИЯ ТРАНЗАКЦИЙ ===\n")
        transactions_list = list(transactions)
        if not transactions_list:
            print("Нет транзакций для отображения.")
        else:
            for t in transactions_list:
                print(t)
            print(f"\nВсего транзакций: {len(transactions_list)}")
        input("\nНажмите Enter для продолжения...")

    @staticmethod
    def get_date_range():
        BankView.clear_screen()
        print("=== ФИЛЬТРАЦИЯ ПО ДАТЕ ===\n")
        while True:
            try:
                from_date = datetime.strptime(input("Начальная дата (ГГГГ-ММ-ДД): "), "%Y-%m-%d")
                to_date = datetime.strptime(input("Конечная дата (ГГГГ-ММ-ДД): "), "%Y-%m-%d")
                return from_date, to_date
            except ValueError:
                print("Неверный формат даты!")

    @staticmethod
    def get_transaction_type():
        BankView.clear_screen()
        print("=== ФИЛЬТРАЦИЯ ПО ТИПУ ===\n")
        print("1. Депозит")
        print("2. Снятие")
        print("3. Перевод")
        print("4. Начисление процентов")
        print("5. Комиссия")
        choice = input("\nВыберите тип: ").strip()
        types = {
            "1": TransactionType.DEPOSIT,
            "2": TransactionType.WITHDRAWAL,
            "3": TransactionType.TRANSFER,
            "4": TransactionType.INTEREST,
            "5": TransactionType.FEE
        }
        return types.get(choice, TransactionType.DEPOSIT)

    @staticmethod
    def get_account_and_amount(action):
        BankView.clear_screen()
        print(f"=== {action} СРЕДСТВ ===\n")
        number = BankView.get_user_input("Номер счета")
        amount = BankView.get_decimal_input("Сумма")
        return number, amount

    @staticmethod
    def get_transfer_info():
        BankView.clear_screen()
        print("=== ПЕРЕВОД СРЕДСТВ ===\n")
        from_account = BankView.get_user_input("С какого счета перевести")
        to_account = BankView.get_user_input("На какой счет перевести")
        amount = BankView.get_decimal_input("Сумма перевода")
        return from_account, to_account, amount

    @staticmethod
    def get_account_creation_info():
        BankView.clear_screen()
        print("=== СОЗДАНИЕ НОВОГО СЧЕТА ===\n")
        print("Тип счета:")
        print("1. Расчетный счет")
        print("2. Сберегательный счет")
        print("3. Кредитный счет")
        type_choice = input("\nВыберите тип (1-3): ").strip()

        account_types = {
            "1": "Checking",
            "2": "Savings",
            "3": "Credit"
        }
        account_type = account_types.get(type_choice, "Checking")

        number = BankView.get_user_input("Номер счета")
        name = BankView.get_user_input("Имя владельца")
        initial = BankView.get_decimal_input("Начальный баланс")

        return account_type, number, name, initial


def main():
    from controller import BankController
    controller = BankController()
    controller.run()


if __name__ == "__main__":
    main()
