"""
Bernstein-Vazirani Benchmark Program - Fire Opal
"""

import sys
import time

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

sys.path[1:1] = ["_common", "_common/fireopal"]
sys.path[1:1] = ["../../_common", "../../_common/fireopal"]

import execute as ex
import metrics as metrics

np.random.seed(0)

verbose = False

# saved circuits for display
QC_ = None
Uf_ = None


# Circuit Definition


def create_oracle(num_qubits, input_size, secret_int):
    # Initialize first n qubits and single ancilla qubit
    qr = QuantumRegister(num_qubits)
    qc = QuantumCircuit(qr, name="Uf")

    # perform CX for each qubit that matches a bit in secret string
    s = ("{0:0" + str(input_size) + "b}").format(secret_int)
    for i_qubit in range(input_size):
        if s[input_size - 1 - i_qubit] == "1":
            qc.cx(qr[i_qubit], qr[input_size])
    return qc


def BernsteinVazirani(num_qubits, secret_int, method=1):
    # size of input is one less than available qubits
    input_size = num_qubits - 1

    if method == 1:
        qr = QuantumRegister(num_qubits)
        cr = ClassicalRegister(input_size)
        qc = QuantumCircuit(qr, cr, name="main")

        # put ancilla in |1> state
        qc.x(qr[input_size])

        # start with Hadamard on all qubits, including ancilla
        for i_qubit in range(num_qubits):
            qc.h(qr[i_qubit])

        qc.barrier()

        # generate Uf oracle
        Uf = create_oracle(num_qubits, input_size, secret_int)
        qc.append(Uf, qr)

        qc.barrier()

        # end with Hadamard on all qubits, including ancilla
        for i_qubit in range(num_qubits):
            qc.h(qr[i_qubit])

        # uncompute ancilla qubit, not necessary for algorithm
        qc.x(qr[input_size])

        qc.barrier()

        # measure all data qubits
        for i in range(input_size):
            qc.measure(i, i)

        global Uf_
        if Uf_ is None or num_qubits <= 6:
            if num_qubits < 9:
                Uf_ = Uf

    elif method == 2:
        qr = QuantumRegister(2)
        cr = ClassicalRegister(input_size)
        qc = QuantumCircuit(qr, cr, name="main")

        # put ancilla in |-> state
        qc.x(qr[1])
        qc.h(qr[1])

        qc.barrier()

        # perform CX for each qubit that matches a bit in secret string
        s = ('{0:0' + str(input_size) + 'b}').format(secret_int)
        for i in range(input_size):
            if s[input_size - 1 - i] == '1':
                qc.h(qr[0])
                qc.cx(qr[0], qr[1])
                qc.h(qr[0])
            qc.measure(qr[0], cr[i])

    # save smaller circuit example for display
    global QC_
    if QC_ is None or num_qubits <= 6:
        if num_qubits < 9:
            QC_ = qc

    # return a handle on the circuit
    return qc


# Result Data Analysis

# Analyze and print measured results
# Expected result is always the secret_int, so fidelity calc is simple
def analyze_and_print_result(qc, result, num_qubits, secret_int):
    # size of input is one less than available qubits
    input_size = num_qubits - 1

    # obtain counts from the result object
    counts = result.get_counts(qc)
    if verbose:
        print(f"For secret int {secret_int} measured: {counts}")

    # create the key that is expected to have all the measurements (for this circuit)
    key = format(secret_int, f"0{input_size}b")

    # correct distribution is measuring the key 100% of the time
    correct_dist = {key: 1.0}

    # use our polarization fidelity rescaling
    fidelity = metrics.polarization_fidelity(counts, correct_dist)

    return counts, fidelity


# Benchmark Loop

# Execute program with default parameters
def run(
    min_qubits=3,
    max_qubits=6,
    max_circuits=30,
    num_shots=1024,
    method=1,
    backend_id="fire_opal_ibmq_jakarta",
    device_credentials=None,
):
    print("Bernstein-Vazirani Benchmark Program - Fire Opal")

    # validate parameters (smallest circuit is 3 qubits)
    max_qubits = max(3, max_qubits)
    min_qubits = min(max(3, min_qubits), max_qubits)
    # print(f"min, max qubits = {min_qubits} {max_qubits}")

    # Initialize metrics module
    metrics.init_metrics()

    # Define custom result handler
    def execution_handler(qc, result, num_qubits, s_int):
        # determine fidelity of result set
        num_qubits = int(num_qubits)
        counts, fidelity = analyze_and_print_result(qc, result, num_qubits, int(s_int))
        metrics.store_metric(num_qubits, s_int, "fidelity", fidelity)

    # Initialize execution module using the execution result handler above and specified backend_id
    ex.init_execution(execution_handler)
    ex.set_execution_target(backend_id, device_credentials)

    # Execute Benchmark Program N times for multiple circuit sizes
    # Accumulate metrics asynchronously as circuits complete
    for num_qubits in range(min_qubits, max_qubits + 1):
        input_size = num_qubits - 1

        # determine number of circuits to execute for this group
        num_circuits = min(2**input_size, max_circuits)

        print(
            f"************\nExecuting [{num_circuits}] circuits with num_qubits = {num_qubits}"
        )

        # determine range of secret strings to loop over
        if 2**input_size <= max_circuits:
            s_range = list(range(num_circuits))
        else:
            s_range = np.random.choice(2**input_size, num_circuits, False)

        # loop over limited # of secret strings for this
        for s_int in s_range:
            # create the circuit for given qubit size and secret string, store time metric
            ts = time.time()
            qc = BernsteinVazirani(num_qubits, s_int)
            metrics.store_metric(num_qubits, s_int, "create_time", time.time() - ts)

            # collapse the sub-circuit levels used in this benchmark (for qiskit)
            qc2 = qc.decompose()

            # submit circuit for execution on target (simulator, cloud simulator, or hardware)
            ex.submit_circuit(qc2, num_qubits, s_int, shots=num_shots)

        # execute all circuits for this group, aggregate and report metrics when complete
        ex.execute_circuits()
        metrics.aggregate_metrics_for_group(num_qubits)
        metrics.report_metrics_for_group(num_qubits)

    # print a sample circuit
    print("Sample Circuit:")
    print(QC_ if QC_ is not None else "  ... too large!")
    print("\nQuantum Oracle 'Uf' =")
    print(Uf_ if Uf_ is not None else "  ... too large!")

    # Plot metrics for all circuit sizes
    metrics.plot_metrics(f"Benchmark Results - Bernstein-Vazirani ({method}) - Fire Opal")


# if main, execute method
if __name__ == "__main__":
    run()
