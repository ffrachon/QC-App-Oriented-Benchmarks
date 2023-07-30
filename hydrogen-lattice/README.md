# Hydrogen Lattice - Benchmark Program

This benchmark uses the VQE algorithm [[1]](#references) as an example of a quantum application that can simulate the dynamics of a lattice arrangement of hydrogen atoms and determine its lowest energy state. The number and shape of the hydrogen lattice is configurable, allowing for performance tests are different levels of electron correlation. The hydrogen lattice system is of interest to benchmarking as while it is simple (relatively few electrons) and scalable (adding more atoms is trivial), it also has the potential to switch into a strongly correlated regime. Classically calculating dynamics is difficult within this strongly correlated regime, and due to the ease with which benchmarks can be made, it is a good area to benchmark early quantum VQE algorithms.

This benchmark was created as an extension of the existing MaxCut bencharks, where the goal is to instead find the ground state energy of a hydrogen lattice configuration specified by a .json file. Using a particular ansatz, the ground state energy is found through VQE. This energy is compared to a corresponding .sol file containing the ground state energies for the same hydrogen lattice configuration, except calculated by current classical methods. Both the .json and .sol files can be generated by the generate-vqe-instance.py and compute-vqe-solution (check names0 respectively), or supplied by a user. 

The remainder of this README offers a brief summary of the benchmark and how to run it.  For more detail, please see the aforementioned paper.

## Problem outline

The VQE algorithm would optimally allow for finding ground state energies in systems that are too difficult to solve classically (like in strongly correlated regimes). By performing the algorithm on a lattice arrangement of hydrogen atoms, it is possible to create scalable benchmarks that showcase how well current NISQ-era quantum computers can perform relative to each other and compared to current classical systems. 

## Benchmarking

As an extension to the MaxCut frameworks, several comparisons are easily made and may help in understanding how VQE benchmarking is performed. Similar to the MaxCut benchmarks, there are two primary benchmarking methods, denoted by methods 1 and 2. Method 1 runs a VQE ansatz at various lengths and widths, testing target system execution fidelities in a fashion very similar to method 1 of the MaxCut Framework. Method 2 runs the entire VQE algorithm, in which a paramaterized quantum system works in conjunction with a classical optimizer to approximate the ground state energy. While again very similar to the MaxCut framework, there are several key differences. In addition to iterating over the same circuit like in the MaxCut framework, the VQE benchmarks must iterate through multiple circuits to find the expectation value for each Pauli term in the hamiltonian. Additionally, over the same number of qubits, we might want to run differnent hamiltonians that describe lattices with different radii. These differences have led to metric collection and running of the benchmarks to behave differently than the MaxCut ones. 

In the run() method for the benchmark, there are a number of optional arguments that can be specified. While kept similar to MaxCut's own run() method, note that some argumenents have been necessarily changed. All of the arguments can be examined in the source code, but the key arguments that would typically be modifed from defaults are the following:

(note these need to be modifed for the VQE ...)

```
    method : int, optional
        If 1, then do standard metrics, if 2, implement iterative algo metrics. The default is 1.
    rounds : int, optional
        number of QAOA rounds. The default is 1.
    degree : int, optional
        degree of graph. The default is 3. Can be -3 also.
    thetas_array : list, optional
        list or ndarray of beta and gamma values. The default is None, which uses [1,1,...].
    use_fixed_angles : bool, optional
        use betas and gammas obtained from a 'fixed angles' table, specific to degree and rounds
    parameterized : bool, optional
        Whether to use parametrized circuits or not. The default is False.
    max_iter : int, optional
        Number of iterations for the minimizer routine. The default is 30.
    score_metric : list or string, optional
        Which metrics are to be plotted in area metrics plots. The default is 'fidelity'. For method 2 s/b 'approx_ratio'.
    x_metric : list or string, optional
        Horizontal axis for area plots. The default is 'cumulative_exec_time' Can be 'cumulative_elapsed_time' also.
```

## Classical algorithm

Classical algorithms to solve the dynamics of quantum systems have been in development for many years, some of which have the advantage of being exact in the infinite limit. Unfortunately, due to the exponential scaling of quantum systems, they tend to use too many resources for relatively few qubits. We use several such algorithms to compute ground state energies, storing them in .sol files corresponding to each problem instance .json. It is thought that using a quantum computer to store the ansatz rather than clasically solving them will provide a more natural and efficient means to solve quantum dynamics problems. 

## Quantum algorithm

VQE primarily uses the quantum computer to store and manipulate the eigenstate, meaning that the optimization step itself is done classically. This means that many optimization algorithms are compatible with VQE- two commonly used ones are COBYLA and SPSA. COBYLA is mostly used for noise-free simulations with simple Hamiltonians, wheras SPSA can better handle noise. For our benchmarking purposes, the ___ algorithm is used. A more detailed derivation of the particular style of VQE follows in the next paragraphs.

### General VQE 

First, from a system of interest, a hamiltonian is defined and is converted from a fermionic to qubit basis via the Jordan-Wigner Transformation (JWT):  
$a_p \mapsto \frac{1}{2}\left(X_p+\mathrm{i} Y_p\right) Z_1 \cdots Z_{p-1}$ [use refernece that the VQE readme uses]

The Hamiltonian therefore becomes a sum of weighed pauli operators: 

$H=\sum_p g_p P_p$

Where $g_p$ are the ampltiudes and $P_p$ are the Pauli operators. 

Different ansatz can be used. If, for instance, the pUCCD ansatz is used, the JWT is also used to transform from the fermionic to qubit basis. 

### General Quantum Circuit

VQE circuits generally consist of a state preparation state, with parameterized quantum gates then applied afterwards for the iterative optimization steps. 

Put in a general picture of the quantum circuit here? 

### Algorithmic Visualization

Put in pictures from qiskit of the various VQE algorithms here. 

### Algorithm Steps

(Create a new latex picture for the algorithm steps. Should be pretty straightforwards.)

## Gate Implementation

In MaxCut, both this and circuit methods are elaborated on in the paper itself rather than in here. 

## Circuit Methods

Describe ...

## References

Modify for the VQE and hydrogen lattice problem ...

[Solving combinatorial optimization problems using QAOA (Qiskit Tutorial)](https://qiskit.org/textbook/ch-applications/qaoa.html)