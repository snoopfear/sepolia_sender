import time
import random
from web3 import Web3

# Настройки
RPC_URL = "https://endpoints.omniatech.io/v1/eth/sepolia/public"  # Замените на ваш RPC-узел
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Проверка соединения
if not web3.is_connected():
    raise Exception("Не удалось подключиться к RPC-узлу")

# Задать процент отправки ETH от баланса (например, 50%):
SEND_PERCENTAGE = 1

# Укажите диапазон задержки между транзакциями (в секундах)
MIN_DELAY = 5
MAX_DELAY = 10

# Задержка между проверками баланса (в секундах)
BALANCE_CHECK_DELAY = 1

# Загрузка кошельков из файла
def load_wallets(file_path):
    wallets = []
    with open(file_path, "r") as file:
        for line in file:
            private_key, receiver_address = line.strip().split(":")
            
            # Добавить '0x' к приватному ключу, если его нет
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            
            wallets.append((private_key, receiver_address))
    return wallets
    
# Проверка баланса с задержкой
def check_balances(wallets):
    print("\n--- Проверка баланса кошельков ---\n")
    for private_key, receiver_address in wallets:
        # Получить адрес отправителя из приватного ключа
        sender_address = web3.eth.account.from_key(private_key).address
        # Получить баланс
        balance = web3.eth.get_balance(sender_address)
        eth_balance = web3.from_wei(balance, "ether")
        print(f"Адрес: {sender_address} | Баланс: {eth_balance} ETH")

        # Задержка между проверками
        print(f"Ожидание {BALANCE_CHECK_DELAY} секунд перед проверкой следующего кошелька...")
        time.sleep(BALANCE_CHECK_DELAY)
    print("\nПроверка баланса завершена.\n")

# Отправка ETH
def send_eth(private_key, receiver_address, percentage):
    # Создать аккаунт-отправитель
    account = web3.eth.account.from_key(private_key)
    sender_address = account.address

    # Получить баланс
    balance = web3.eth.get_balance(sender_address)
    eth_balance = web3.from_wei(balance, "ether")
    print(f"Баланс отправителя {sender_address}: {eth_balance} ETH")

    # Рассчитать сумму для отправки
    amount_to_send = int(balance * (percentage / 100))
    if amount_to_send == 0:
        print(f"Недостаточно средств для отправки с {sender_address}")
        return

    # Преобразовать адрес получателя в формат checksum
    receiver_address = Web3.to_checksum_address(receiver_address)

    # Составление транзакции
    tx = {
        "from": sender_address,
        "to": receiver_address,  # Адрес должен быть в формате checksum
        "value": amount_to_send,
        "gas": 21000,  # Стандартный лимит газа для перевода ETH
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(sender_address),
    }

    # Подписание транзакции
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)

    # Отправка транзакции
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Транзакция отправлена! Hash: {web3.toHex(tx_hash)}")
    except Exception as e:
        print(f"Ошибка при отправке транзакции: {e}")
# Запуск передачи ETH
def send_eth_to_wallets(wallets, percentage):
    print("\n--- Запуск передачи ETH ---\n")
    for private_key, receiver_address in wallets:
        print(f"Отправка с {private_key} на {receiver_address}")
        send_eth(private_key, receiver_address, percentage)

        # Рандомная задержка
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(f"Ожидание {delay} секунд перед следующей транзакцией...")
        time.sleep(delay)
    print("\nПередача ETH завершена.\n")

# Основное меню
def main_menu():
    wallets = load_wallets("wallets.txt")

    while True:
        print("\n--- Главное меню ---")
        print("1. Проверить баланс кошельков (Sepolia)")
        print("2. Запустить передачу ETH")
        print("3. Выйти")
        
        choice = input("\nВведите номер действия: ")

        if choice == "1":
            check_balances(wallets)
        elif choice == "2":
            send_eth_to_wallets(wallets, SEND_PERCENTAGE)
        elif choice == "3":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

# Запуск программы
if __name__ == "__main__":
    main_menu()
