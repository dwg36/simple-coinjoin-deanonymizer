import csv
import random
import hashlib

# Configuration
NUM_USERS = 10
NUM_ROUNDS = 30
OUTPUT_FILE = 'coinjoin_data.csv'

# Generate a unique transaction ID
def generate_tx_id(scenario, round_num):
    data = f"tx_s{scenario}_r{round_num}_{random.random()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

# Amounts are based on whether a user is careful or careless
def get_amounts(is_careful):
    # Generate a random total amount to mix
    total = random.uniform(0.5, 2.0)

    if is_careful:
        # Careful users split into standard denominations
        amounts = []
        remaining = total

        # Add 1.0
        while remaining >= 1.0:
            amounts.append(1.0)
            remaining -= 1.0

        # Add 0.1
        while remaining >= 0.1:
            amounts.append(0.1)
            remaining -= 0.1
            
        # Add 0.01
        while remaining >= 0.01:
            amounts.append(0.01)
            remaining -= 0.01

        return amounts if amounts else [0.1]
    else:
        # Careless users don't split
        return [round(total, 2)]

# Run a scenario with x careful users and y careless users
def run_scenario(num_careful):
    users = []

    for i in range(num_careful):
        user = {'id': i, 'careful': True}
        users.append(user)
    for i in range(num_careful, NUM_USERS):
        user = {'id': i, 'careful': False}
        users.append(user)

    random.shuffle(users)
    transactions = []

    for round_num in range(NUM_ROUNDS):
        tx = {
            'id': generate_tx_id(num_careful, round_num),
            'scenario': num_careful,
            'round': round_num,
            'inputs': [],
            'outputs': []
        }

        # For simplicity, all users participate in every round
        for user in users:
            amounts = get_amounts(user['careful'])

            for amt in amounts:
                tx['inputs'].append((user, amt))
                tx['outputs'].append((user['id'], amt))

        random.shuffle(tx['outputs'])
        transactions.append(tx)

    return transactions

# Generate all scenarios and save to CSV
def generate_all_scenarios():
    print("Generating CoinJoin data...")
    print(f"Users per round: {NUM_USERS}")
    print(f"Rounds per scenario: {NUM_ROUNDS}\n")

    all_transactions = []

    # Loop through each scenario
    for num_careful in range(NUM_USERS + 1):
        scenario_txs = run_scenario(num_careful)
        all_transactions.extend(scenario_txs)

    # Save to CSV
    with open(OUTPUT_FILE, 'w', newline='') as f:
        fieldnames = [
            'scenario', 'tx_id', 'round', 'input_idx', 'input_user_id',
            'input_amount', 'input_careful', 'output_idx', 'output_user_id',
            'output_amount'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for tx in all_transactions:
            for i_idx, (i_user, i_amt) in enumerate(tx['inputs']):
                for o_idx, (o_uid, o_amt) in enumerate(tx['outputs']):
                    writer.writerow({
                        'scenario': tx['scenario'],
                        'tx_id': tx['id'],
                        'round': tx['round'],
                        'input_idx': i_idx,
                        'input_user_id': i_user['id'],
                        'input_amount': i_amt,
                        'input_careful': 1 if i_user['careful'] else 0,
                        'output_idx': o_idx,
                        'output_user_id': o_uid,
                        'output_amount': o_amt
                    })

    print(f"Generated {len(all_transactions)} transactions across {NUM_USERS + 1} scenarios")
    print(f"Saved to {OUTPUT_FILE}")

# Run main function
if __name__ == "__main__":
    generate_all_scenarios()
