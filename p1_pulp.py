import time
import pulp
from pulp import LpProblem, LpMinimize, LpVariable, lpSum

def nova_variavel(prob, nome, lowBound=None):
    # no PuLP 4.x as variaveis sao criadas pelo proprio problema
    if hasattr(prob, "add_variable"):
        return prob.add_variable(nome, lowBound=lowBound)
    return LpVariable(nome, lowBound=lowBound)

def solver_padrao():
    # o PuLP 4.x nao vem mais com o CBC, usa o HiGHS (pip install highspy)
    if hasattr(pulp, "PULP_CBC_CMD"):
        return pulp.PULP_CBC_CMD(msg=False)
    return pulp.HiGHS(msg=False)

def resolver_p1(dados):
    n = dados['num_vertices']
    arestas = dados['arestas']

    s = dados['s'] if dados['s'] is not None else 1
    t = dados['t'] if dados['t'] is not None else n

    prob = LpProblem("P1", LpMinimize)

    d = {u: nova_variavel(prob, f"d_{u}", lowBound=0) for u in range(1, n + 1)}
    x = {e: nova_variavel(prob, f"x_{e}", lowBound=0) for e in range(len(arestas))}

    prob += lpSum(arestas[e][2] * x[e] for e in range(len(arestas))), "Custo_Total"

    for e, (u, v, c) in enumerate(arestas):
        prob += x[e] >= d[u] - d[v], f"uv_{e}"
        prob += x[e] >= d[v] - d[u], f"vu_{e}"

    prob += d[s] == 0, "fix_s"
    prob += d[t] == 1, "fix_t"

    inicio = time.time()
    prob.solve(solver_padrao())
    fim = time.time()

    return pulp.value(prob.objective), fim - inicio

if __name__ == "__main__":
    from leitor import ler_instancia
    
    caminho_instancia = "instancias/instance1.min"
    
    try:
        dados = ler_instancia(caminho_instancia)
        valor_obj, tempo = resolver_p1(dados)
        
        print("\n=== Execução Direta: P1 (MIN) ===")
        print(f"Instância: {caminho_instancia}")
        print(f"Valor do Objetivo: {valor_obj}")
        print(f"Tempo de Execução: {tempo:.4f} segundos\n")
    except FileNotFoundError:
        print(f"\nFicheiro '{caminho_instancia}' não encontrado.\n")