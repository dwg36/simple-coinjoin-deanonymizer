import csv
from collections import Counter

INPUT_FILE = 'coinjoin_data.csv'

# Load coinjoin_data.csv
def load_csv(filename):
    scenarios = {}

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:

            scenario = int(row['scenario'])
            tx_id = row['tx_id']
            i_idx = int(row['input_idx'])
            o_idx = int(row['output_idx'])
            uid = int(row['input_user_id'])
            careful = int(row['input_careful']) == 1

            # Create scenario if it doesn't exist
            if scenario not in scenarios:
                scenarios[scenario] = {}

            # Create transaction if it doesn't exist
            if tx_id not in scenarios[scenario]:
                scenarios[scenario][tx_id] = {
                    'inputs': {},
                    'outputs': {},
                    'round': None,
                    'users': {}
                }

            # Get transaction data
            tx_data = scenarios[scenario][tx_id]

            # Store data
            tx_data['round'] = int(row['round'])
            tx_data['inputs'][i_idx] = (uid, float(row['input_amount']), careful)
            tx_data['outputs'][o_idx] = (int(row['output_user_id']), float(row['output_amount']))
            tx_data['users'][uid] = careful

    all_scenarios = {}

    # iterate through scenarios
    for scenario_num in scenarios:
        txs = scenarios[scenario_num]
        tx_list = []
        users_dict = {}

        # iterate through transactions
        for tx_id in txs:
            data = txs[tx_id]

            # Sort inputs and outputs
            sorted_inputs = []
            for i in sorted(data['inputs'].keys()):
                sorted_inputs.append(data['inputs'][i])

            sorted_outputs = []
            for i in sorted(data['outputs'].keys()):
                sorted_outputs.append(data['outputs'][i])

            # Create transaction record
            tx_list.append({
                'id': tx_id,
                'round': data['round'],
                'inputs': sorted_inputs,
                'outputs': sorted_outputs
            })

            # Track users
            users_dict.update(data['users'])

        # Sort transactions by round number
        tx_list.sort(key=lambda x: x['round'])

        # Store scenario data
        all_scenarios[scenario_num] = {
            'transactions': tx_list,
            'users': users_dict
        }

    return all_scenarios


# Trace CoinJoin transaction using amount matching attack
def trace_transaction(tx):
    links = []

    # Count how many times each amount appears in inputs
    input_amounts = []
    for uid, amt, careful in tx['inputs']:
        input_amounts.append(amt)

    input_counts = Counter(input_amounts)

    # Check each input
    for i in range(len(tx['inputs'])):
        uid, amt, careful = tx['inputs'][i]

        # Check if this amount appears only once in inputs
        if input_counts[amt] == 1:
            matches = []
            for j in range(len(tx['outputs'])):
                o_uid, o_amt = tx['outputs'][j]
                # Check if amounts match (rounding to avoid float issues)
                if abs(o_amt - amt) < 0.001:
                    matches.append(j)

            # If exactly one match found, user is de-anonymized
            if len(matches) == 1:
                links.append((i, matches[0], 0.95))

    return links


# Analyze scenario and count exposed users
def analyze_scenario(transactions, users_dict):
    traced_links = {}
    careful_exposed = []
    careless_exposed = []
    total_traced = 0
    correct_traced = 0

    # Check each transaction
    for tx in transactions:
        links = trace_transaction(tx)
        traced_links[tx['id']] = links

        # Check each traced link
        for i_idx, o_idx, conf in links:
            total_traced += 1

            # Get input and output user IDs
            i_uid, i_amt, i_careful = tx['inputs'][i_idx]
            o_uid, o_amt = tx['outputs'][o_idx]

            # Check if our trace is correct
            if i_uid == o_uid:
                correct_traced += 1

                # Track which type of user was exposed
                if i_careful:
                    if i_uid not in careful_exposed:
                        careful_exposed.append(i_uid)
                else:
                    if i_uid not in careless_exposed:
                        careless_exposed.append(i_uid)

    careful_total = 0
    careless_total = 0
    for uid in users_dict:
        if users_dict[uid]:
            careful_total += 1
        else:
            careless_total += 1

    # Calculate accuracy
    if total_traced > 0:
        accuracy = correct_traced / total_traced
    else:
        accuracy = 0

    return {
        'total_traced': total_traced,
        'correct_traced': correct_traced,
        'accuracy': accuracy,
        'careful_exposed': len(careful_exposed),
        'careless_exposed': len(careless_exposed),
        'careful_total': careful_total,
        'careless_total': careless_total
    }


# Print results
def print_scenario_results(scenario_num, results):
    print(f"\nScenario {scenario_num}: {results['careful_total']} Careful, {results['careless_total']} Careless")
    print(f"Links traced: {results['total_traced']}")
    print(f"Accuracy: {results['accuracy']*100:.1f}%")

    if results['careful_total'] > 0:
        careful_rate = results['careful_exposed']/results['careful_total']*100
        print(f"Careful exposed: {results['careful_exposed']}/{results['careful_total']} ({careful_rate:.1f}%)")

    if results['careless_total'] > 0:
        careless_rate = results['careless_exposed']/results['careless_total']*100
        print(f"Careless exposed: {results['careless_exposed']}/{results['careless_total']} ({careless_rate:.1f}%)")

# Main function
def main():
    print("CoinJoin De-anonymizer\n")

    # Load data
    try:
        all_scenarios = load_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found")
        return

    # Analyze each scenario
    for scenario_num in sorted(all_scenarios.keys()):
        data = all_scenarios[scenario_num]
        results = analyze_scenario(data['transactions'], data['users'])
        print_scenario_results(scenario_num, results)

    print("\nAnalysis Complete")

# Run main function
if __name__ == "__main__":
    main()
