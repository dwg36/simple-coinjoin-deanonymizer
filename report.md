# CoinJoin Privacy Analysis - Project Report

## Summary

For this project, I implemented a simplified CoinJoin cryptocurrency mixing protocol to demonstrate how vulnerable it is to amount-matching deanonymization attacks. Through testing with different parameters, I found that while CoinJoin does provide some privacy benefits, users who don't split their transaction amounts into standard denominations get almost completely deanonymized.

## Introduction to CoinJoin

CoinJoin is a privacy-enhancing technique for cryptocurrency transactions that works by combining multiple users' transactions into a single transaction with shuffled outputs. This makes it difficult for observers to determine which input corresponds to which output, obscuring the transaction graph.

### How My Implementation Works

My project consists of two main components:

1. **coinjoin.py** - Simulates CoinJoin mixing rounds
2. **deanonymize.py** - Attempts to trace transactions using amount-matching attacks

### How to Run

**Required Libraries:**
All libraries used are part of Python's standard library, so no external dependencies need to be installed:
- `csv` - For reading/writing transaction data
- `random` - For randomizing transaction outputs
- `hashlib` - For generating transaction IDs
- `collections.Counter` - For counting amount occurrences in the deanonymization attack

**Running the Code:**

1. First, run the CoinJoin simulator to generate transaction data:
```bash
python3 coinjoin.py
```
This creates `coinjoin_data.csv` with all the simulated transactions.

2. Then, run the deanonymization analysis:
```bash
python3 deanonymize.py
```
This analyzes the CSV and outputs exposure rates for each scenario.

**Adjusting Parameters:**
To test different configurations, edit the parameters at the top of `coinjoin.py`:
- `NUM_USERS` - Number of participants
- `NUM_ROUNDS` - Number of mixing rounds

#### Code Structure (coinjoin.py)

**User Behavior Types:**

I modeled two types of users in the simulation:

1. **Careful Users**: These users split their amounts into standard denominations (1.0, 0.1, 0.01). This mimics what real-world implementations like Wasabi Wallet and Dash's PrivateSend do - they enforce denomination splitting to create larger anonymity sets.

2. **Careless Users**: These users just use arbitrary, non-standard amounts without splitting. This creates unique fingerprints that make them vulnerable to deanonymization.

**Transaction Generation:**

For each round:
- All users contribute their inputs with corresponding amounts
- Shuffle the outputs randomly to obscure the input-output mapping
- Transaction data gets recorded for later analysis

#### Deanonymization Attack (deanonymize.py)

My deanonymization script implements an amount-matching attack:

1. For each transaction, it counts how many times each amount appears in the inputs
2. If an amount appears only once in the inputs, it checks for matching outputs
3. If exactly one output matches that unique amount, it can trace the link with high confidence
4. This reveals which input corresponds to which output, breaking anonymity

The attack achieves 100% accuracy when it can make a trace, but can't trace transactions where amounts aren't unique (when multiple users use the same standard denominations).

## Experimental Results

I ran multiple tests with different parameter configurations to see how user count and mixing rounds affect privacy:

### Test 1: 10 users, 30 rounds

**What I Found:**
- Links traced: Up to 289 maximum
- Careless users: 100% exposed
- Careful users: Protection improves dramatically with more careful peers
  - With 6+ careful users: 0% exposure rate
  - With 4-5 careful users: 20-60% exposure rate
  - With 1-3 careful users: 33-100% exposure rate

### Test 2: 5 rounds, 20 users

**What I Found:**
- Links traced: Up to 94 maximum
- Careless users: 100% exposed
- Careful users: Better protection due to larger anonymity set
  - With 7+ careful users: 0% exposure
  - With 2-6 careful users: 0-33% exposure (much better than default)

### Test 3: 50 rounds, 5 users

**What I Found:**
- Links traced: Up to 244 maximum
- Careless users: 100% exposed
- Careful users: Significantly worse protection
  - Even with all 5 users being careful: 40% exposure
  - With 3-4 careful users: 50-100% exposure

### Test 4: 5 rounds, 5 users

**What I Found:**
- Links traced: Up to 25 maximum
- Careless users: 100% exposed
- Careful users: Moderate protection
  - With all 5 careful: 0% exposure
  - With 3-4 careful: 0-33% exposure

### Test 5: 10 users, 40 rounds

**What I Found:**
- Links traced: Up to 384 maximum
- Careless users: 100% exposed
- Careful users:
  - With 6+ careful: 0-12% exposure (slightly higher than default due to more rounds)
  - With fewer careful: Similar to default

## Key Observations and Trends

### 1. Careless Users Are Always Vulnerable
Across ALL my tested configurations, users who don't split their amounts into standard denominations face total deanonymization (100% exposure rate). This finding is critical: **amount standardization is not optional for privacy.**

### 2. Anonymity Set Size Matters Most
Configurations with more users (20 vs 5) showed much better privacy for careful users, even with fewer rounds. The larger the pool of participants, the harder it is to uniquely identify transactions through amount matching.

### 3. Diminishing Returns from Additional Rounds
When I compared 30 rounds vs 40 rounds with the same user count, I saw minimal privacy improvements. Actually, more rounds sometimes slightly reduced privacy by giving me more data points to analyze. There seems to be an optimal range of mixing rounds beyond which additional rounds don't really help.

### 4. Effect of Careful Users
There's a threshold effect where privacy dramatically improves once a certain proportion of users are "careful":
- Below ~40% careful users: Careful users still face significant exposure risk
- Above ~60% careful users: Exposure risk drops substantially, approaching 0%

This suggests CoinJoin works best when most participants follow best practices.

### 5. Computational Limits of Deanonymization
The timeout with 20 users and 50 rounds (1,050 transactions) shows that amount-matching attacks get computationally expensive at scale. Real-world blockchain analysis might face similar limits, though systems with way more resources could potentially overcome them.

### 6. Small Pools Are Dangerous
With only 5 users, even 50 mixing rounds couldn't provide strong privacy guarantees. Small mixing pools should definitely be avoided since they can't create sufficient anonymity sets regardless of how many rounds you run.

## Limitations of My Project

My simulation makes several simplifying assumptions:

- All users participate in every round (real-world participation is more variable)
- I only implemented amount-matching attacks (real attacks use timing, network analysis, and other techniques)
- I didn't consider transaction fees, which can leak information
- Simplified denomination structure (real systems might use more complex mechanisms)
- No modeling of post-mixing behavior (which is the most critical vulnerability)

## Modern CoinJoin Implementations

### Wasabi Wallet and Dash PrivateSend

Modern implementations like Wasabi Wallet and Dash have greatly improved upon this basic version of CoinJoin in a couple ways:

**Enforced Denomination Splitting**: Both systems require users to split their funds into standard denominations before mixing. This increases the anonymity set by ensuring many users have identical output amounts.

**Multiple Mixing Rounds**: Wasabi and Dash support multiple rounds of mixing, where outputs from one round become inputs to the next.

### Limitations and Traceability

Despite these improvements, research has shown that even sophisticated CoinJoin implementations are still vulnerable:

**Merging After Splitting**: The main vulnerability happens when users recombine (merge) their split outputs after mixing. When multiple previously-mixed outputs are spent together in a single transaction, it reveals they belong to the same owner.

**Address Reuse**: Reusing addresses before or after mixing can also leak identity information.

**Timing Analysis**: Correlation of input/output timing patterns can reduce anonymity sets.

**Sybil Attacks**: Malicious actors can run multiple nodes to participate in many mixing rounds, potentially learning input-output mappings.

## Conclusion

My project shows that basic CoinJoin provides meaningful privacy benefits, but only when:
1. Users properly split amounts into standard denominations
2. Mixing pools are sufficiently large (10+ users minimum, 20+ preferred)
3. Multiple rounds are used (though with diminishing returns)

The fact that careless users face 100% deanonymization across all my configurations really emphasizes how important proper operational security is. Modern implementations like Wasabi and Dash improve on this basic protocol through enforced denomination splitting, but they're still vulnerable to post-mixing analysis when users merge outputs.

For real privacy in cryptocurrency transactions, CoinJoin should be combined with other techniques: proper coin control, avoiding address reuse, careful transaction timing, and being aware that merging previously-mixed outputs significantly degrades privacy.

The computational limitations I observed with large-scale mixing (20 users, 50 rounds timing out) suggest that scaling CoinJoin appropriately can make analysis impractical, though determined adversaries with significant resources could probably still succeed with more sophisticated techniques.
