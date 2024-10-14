with open('orders.json', 'r') as f:
    orders = [json.loads(line) for line in f.read().splitlines()]

print(orders)  # List of order dictionaries