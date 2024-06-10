from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram
import numpy as np
import random
import time

def perform_classical_search(target, arr):
    classical_start_time = time.time()
    for index, element in enumerate(arr):
        if element == target:
            classical_end_time = time.time()
            classical_duration = classical_end_time - classical_start_time
            return index, classical_duration
    return -1, 0

def create_oracle(num_qubits, marked_item):
    oracle_qc = QuantumCircuit(num_qubits, name="oracle")
    
    for qubit in range(num_qubits):
        if marked_item & (1 << qubit):
            oracle_qc.x(qubit)
    
    oracle_qc.h(num_qubits-1)
    oracle_qc.mcx(list(range(num_qubits-1)), num_qubits-1)
    oracle_qc.h(num_qubits-1)
    
    for qubit in range(num_qubits):
        if marked_item & (1 << qubit):
            oracle_qc.x(qubit)
    
    return oracle_qc

def create_grover_circuit(num_qubits, marked_item, num_iterations):
    grover_qc = QuantumCircuit(num_qubits, num_qubits-1)
    
    grover_qc.h(range(num_qubits))
    
    for _ in range(num_iterations):
        grover_qc.append(create_oracle(num_qubits, marked_item), range(num_qubits))
        
        grover_qc.h(range(num_qubits))
        grover_qc.x(range(num_qubits))
        grover_qc.h(num_qubits-1)
        grover_qc.mcx(list(range(num_qubits-1)), num_qubits-1)
        grover_qc.h(num_qubits-1)
        grover_qc.x(range(num_qubits))
        grover_qc.h(range(num_qubits))
    
    grover_qc.measure(range(num_qubits-1), range(num_qubits-1))
    
    return grover_qc

num_qubits = 11
marked_item = 1023
search_target = marked_item
search_range = 2 ** (num_qubits-1)
num_iterations = int(search_range ** 0.5)
print(num_iterations)

marked_item = ~marked_item & (2**num_qubits - 1)

grover_qc = create_grover_circuit(num_qubits, marked_item, num_iterations)

simulator = Aer.get_backend('qasm_simulator')

transpiled_qc = transpile(grover_qc, simulator)

result = simulator.run(transpiled_qc, shots=1024).result()

counts = result.get_counts(grover_qc)

sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
print(sorted_counts)

print(search_range)
search_array = list(range(search_range))

random.shuffle(search_array)

if search_target not in search_array:
    random_index = random.randint(0, search_range)
    search_array[random_index] = search_target

classical_result = perform_classical_search(search_target, search_array)
print(classical_result)

print("Quantum Algorithm Time:", result.time_taken, "s")
print("Total Classical Search Execution Time:", classical_result[1], "s")

print("Number of Classical Iterations:", classical_result[0] + 1)  
print("Number of Quantum Iterations:", num_iterations)

quantum_value = int(max(counts, key=counts.get), 2)
if classical_result[0] is not None and search_array[classical_result[0]] == quantum_value:
    print("The results match!")
else:
    print("The results do not match.")
