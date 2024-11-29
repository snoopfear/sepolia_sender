import time
import random
from web3 import Web3

# Настройки
RPC_URL = "https://endpoints.omniatech.io/v1/eth/sepolia/public"  # Замените на ваш RPC-узел
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# Проверка соединения
if not web3.isConnected():
    raise Exception("Не удалось подключиться к RPC-узлу")

# Задать процент отправки ETH от баланса (например, 50%):
SEND_PERCENTAGE = 1

# Укажите диапазон задержки между транзакциями (в секундах)
MIN_DELAY = 5
MAX_DELAY = 15

# Загрузка кошельков из файла
def load_wallets(file_path):
    wallets = []
    with open(file_path, "r") as file:
        for line in file:
            private_key, receiver_address = line.strip().split(":")
            wallets.append((private_key, receiver_address))
    return wallets

# Отправка ETH
def send_eth(private_key, receiver_address, percentage):
    # Создать аккаунт-отправитель
    account = web3.eth.account.from_key(private_key)
    sender_address = account.address

    # Получить баланс
    balance = web3.eth.get_balance(sender_address)
    eth_balance = web3.fromWei(balance, "ether")
    print(f"Баланс отправителя {sender_address}: {eth_balance} ETH")

    # Рассчитать сумму для отправки
    amount_to_send = (balance * percentage) // 100
    if amount_to_send == 0:
        print(f"Недостаточно средств для отправки с {sender_address}")
        return

    # Составление транзакции
    tx = {
        "from": sender_address,
        "to": receiver_address,
        "value": amount_to_send,
        "gas": 21000,  # Стандартный лимит газа для простого перевода ETH
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(sender_address),
    }

    # Подписание транзакции
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)

    # Отправка транзакции
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Транзакция отправлена! Hash: {web3.toHex(tx_hash)}")
    except Exception as e:
        print(f"Ошибка при отправке транзакции: {e}")

# Основная функция
def main():
    # Загрузить список кошельков
    wallets = load_wallets("wallets.txt")

    # Обработка каждого кошелька
    for private_key, receiver_address in wallets:
        print(f"Отправка с {private_key} на {receiver_address}")
        send_eth(private_key, receiver_address, SEND_PERCENTAGE)

        # Рандомная задержка
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(f"Ожидание {delay} секунд перед следующей транзакцией...")
        time.sleep(delay)

if __name__ == "__main__":
    main()
