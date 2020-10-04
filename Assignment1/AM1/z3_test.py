import z3
P,Q = z3.Bools('P Q')
F = z3.And(P,Q)
solver = z3.Solver()
solver.add(F)
print(solver.check())
print(solver.model())