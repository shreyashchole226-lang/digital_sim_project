"""
gate_engine.py
----------------
Shared logic-gate simulation engine.
Every module (K-map schematic, combinational circuits, sequential
circuits, FSM realization) builds on top of this file.

A circuit is represented as a graph of Gate objects. Each Gate has
input Wires and computes its own output using evaluate().
Propagation happens by calling evaluate() on gates in dependency order.
"""

class Wire:
    """A wire carries a single bit value (0 or 1 or None if undefined)."""
    def __init__(self, name="", value=None):
        self.name = name
        self.value = value

    def set(self, value):
        self.value = int(value)

    def get(self):
        return self.value if self.value is not None else 0

    def __repr__(self):
        return f"Wire({self.name}={self.value})"


class Gate:
    """
    Generic logic gate.
    gate_type: 'AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR', 'XNOR', 'BUF'
    inputs: list of Wire objects
    output: a Wire object (auto-created if not supplied)
    """
    def __init__(self, gate_type, inputs, name="", output=None):
        self.gate_type = gate_type.upper()
        self.inputs = inputs
        self.name = name or gate_type
        self.output = output or Wire(name=self.name + "_out")

    def evaluate(self):
        vals = [w.get() for w in self.inputs]
        gt = self.gate_type

        if gt == "AND":
            result = 1
            for v in vals:
                result &= v
        elif gt == "OR":
            result = 0
            for v in vals:
                result |= v
        elif gt == "NOT":
            result = 1 - vals[0]
        elif gt == "NAND":
            r = 1
            for v in vals:
                r &= v
            result = 1 - r
        elif gt == "NOR":
            r = 0
            for v in vals:
                r |= v
            result = 1 - r
        elif gt == "XOR":
            result = 0
            for v in vals:
                result ^= v
        elif gt == "XNOR":
            r = 0
            for v in vals:
                r ^= v
            result = 1 - r
        elif gt == "BUF":
            result = vals[0]
        else:
            raise ValueError(f"Unknown gate type: {gt}")

        self.output.set(result)
        return result

    def __repr__(self):
        ins = ",".join(str(w.get()) for w in self.inputs)
        return f"{self.name}[{self.gate_type}]({ins})->{self.output.get()}"


class Circuit:
    """
    Holds a set of Wires (inputs) and Gates, evaluated in the order
    they were added. For purely combinational, feed-forward circuits
    (no loops), evaluating gates in insertion order is sufficient as
    long as each gate's inputs were defined earlier.
    """
    def __init__(self, name="circuit"):
        self.name = name
        self.input_wires = {}   # name -> Wire
        self.gates = []         # ordered list of Gate
        self.output_wires = {}  # name -> Wire

    def add_input(self, name, value=0):
        w = Wire(name=name, value=value)
        self.input_wires[name] = w
        return w

    def add_gate(self, gate_type, inputs, name=None):
        g = Gate(gate_type, inputs, name=name or f"g{len(self.gates)}")
        self.gates.append(g)
        return g

    def mark_output(self, name, wire):
        self.output_wires[name] = wire

    def set_input(self, name, value):
        self.input_wires[name].set(value)

    def propagate(self):
        """Evaluate every gate once, in insertion order."""
        for g in self.gates:
            g.evaluate()

    def get_output(self, name):
        return self.output_wires[name].get()

    def get_all_outputs(self):
        return {k: w.get() for k, w in self.output_wires.items()}


# ---------------------------------------------------------------------
# Convenience builders for common small circuits, all built from Gates
# (so everything really is simulated at gate level, not hardcoded math)
# ---------------------------------------------------------------------

def build_half_adder(a_val=0, b_val=0):
    c = Circuit("Half Adder")
    A = c.add_input("A", a_val)
    B = c.add_input("B", b_val)
    sum_gate = c.add_gate("XOR", [A, B], name="SUM")
    carry_gate = c.add_gate("AND", [A, B], name="CARRY")
    c.mark_output("SUM", sum_gate.output)
    c.mark_output("CARRY", carry_gate.output)
    return c


def build_full_adder(a_val=0, b_val=0, cin_val=0):
    c = Circuit("Full Adder")
    A = c.add_input("A", a_val)
    B = c.add_input("B", b_val)
    CIN = c.add_input("CIN", cin_val)

    xor1 = c.add_gate("XOR", [A, B], name="xor1")
    sum_gate = c.add_gate("XOR", [xor1.output, CIN], name="SUM")

    and1 = c.add_gate("AND", [A, B], name="and1")
    and2 = c.add_gate("AND", [xor1.output, CIN], name="and2")
    carry_gate = c.add_gate("OR", [and1.output, and2.output], name="COUT")

    c.mark_output("SUM", sum_gate.output)
    c.mark_output("COUT", carry_gate.output)
    return c


def build_sr_latch_nand(s_val=1, r_val=1, q_init=0):
    """
    Cross-coupled NAND SR latch. Because it has feedback, we cannot use
    plain feed-forward propagate(); instead we iterate a few times so
    the loop settles (standard trick for simulating latches in a
    feed-forward engine).
    """
    c = Circuit("SR Latch (NAND)")
    S = c.add_input("S_bar", s_val)   # active-low inputs typical for NAND latch
    R = c.add_input("R_bar", r_val)

    q_wire = Wire(name="Q", value=q_init)
    qn_wire = Wire(name="Qn", value=1 - q_init)

    gate_q = Gate("NAND", [S, qn_wire], name="gate_q", output=q_wire)
    gate_qn = Gate("NAND", [R, q_wire], name="gate_qn", output=qn_wire)

    c.gates = [gate_q, gate_qn]

    # settle the feedback loop
    for _ in range(4):
        gate_q.evaluate()
        gate_qn.evaluate()

    c.mark_output("Q", q_wire)
    c.mark_output("Qn", qn_wire)
    return c


def sop_to_gate_tree(minterms, num_vars):
    """
    Given a list of minterms (ints) and number of variables,
    build an AND-OR (2-level) gate network representing the
    UNSIMPLIFIED SOP (before minimization) -- useful as a starting
    schematic that Module 1's minimizer will later reduce.
    Returns (Circuit, list_of_input_wires)
    """
    c = Circuit("SOP Gate Tree")
    var_names = [chr(ord('A') + i) for i in range(num_vars)]
    inputs = [c.add_input(v, 0) for v in var_names]

    or_inputs = []
    for m in minterms:
        bits = format(m, f'0{num_vars}b')
        literals = []
        for i, b in enumerate(bits):
            if b == '1':
                literals.append(inputs[i])
            else:
                notg = c.add_gate("NOT", [inputs[i]], name=f"NOT_{var_names[i]}_{m}")
                literals.append(notg.output)
        and_gate = c.add_gate("AND", literals, name=f"AND_m{m}")
        or_inputs.append(and_gate.output)

    if len(or_inputs) == 1:
        final = c.add_gate("BUF", or_inputs, name="F")
    else:
        final = c.add_gate("OR", or_inputs, name="F")

    c.mark_output("F", final.output)
    return c, inputs


if __name__ == "__main__":
    # quick self-test
    fa = build_full_adder(1, 1, 0)
    fa.propagate()
    print(fa.get_all_outputs())  # expect SUM=0, COUT=1

    sr = build_sr_latch_nand(0, 1)  # S active -> Q should go 1
    print(sr.get_all_outputs())
