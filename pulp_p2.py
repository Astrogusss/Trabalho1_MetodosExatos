import pulp
from p2_primal_dual import lerEntrada

V, E, k, arestas, commodits = lerEntrada("mc_instance5.max")

modelo = pulp.LpProblem("Fluxo_Multicommodity", pulp.LpMaximize)

# Variáveis de fluxo
f = {}
for i in range(1, k + 1):
    for (u, v, cap) in arestas:
        f[(i, u, v)] = pulp.LpVariable(f"f_{i}_{u}_{v}", lowBound=0)

# O que tem que maximizar
soma = []
for i in range(1, k + 1):
    s, t, p = commodits[i - 1]
    for (u, v, cap) in arestas:
        if v == t:
            soma.append(p * f[(i, u, v)])
modelo += pulp.lpSum(soma)

# Não pode passar da capacidade
n = 0
for (u, v, cap) in arestas:
    soma = 0
    for i in range(1, k + 1):
        soma += f[(i, u, v)]
    modelo += soma <= cap, f"cap_{n}"
    n += 1

# Conservação só nos nós do meio
n = 0
for i in range(1, k + 1):
    s, t, p = commodits[i - 1]
    for u in range(1, V + 1):
        if u == s or u == t:
            continue

        sai = 0
        entra = 0
        for (u_, v, c) in arestas:
            if u_ == u:
                sai += f[(i, u, v)]
        for (u_, v_, c) in arestas:
            if v_ == u:
                entra += f[(i, u_, u)]

        modelo += (sai - entra == 0, f"cons_{n}")
        n += 1

# Resolve
modelo.solve()

# Resultado
print("Status:", pulp.LpStatus[modelo.status])
print("Valor otimo:", pulp.value(modelo.objective))
