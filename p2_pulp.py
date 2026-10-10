import time
import pulp
from pulp import LpProblem, LpMaximize, LpVariable, lpSum

def resolver_p2(dados):
    arestas = dados['arestas']
    premios = dados['premios']
    fontes = dados['fontes']
    sumidouros = dados['sumidouros']
    num_vertices = dados['num_vertices']

    arcos = []
    for e, (u, v, c) in enumerate(arestas):
        arcos.append((u, v, e, c))
        arcos.append((v, u, e, c))

    prob = LpProblem("P2", LpMaximize)
    commodities = list(premios.keys())

    f = {}
    for i in commodities:
        for u, v, e, c in arcos:
            f[(i, u, v, e)] = LpVariable(f"f_{i}_{u}_{v}_{e}", lowBound=0)

    objetivo_termos = []
    for i in commodities:
        target = sumidouros.get(i)
        for u, v, e, c in arcos:
            if v == target:
                objetivo_termos.append(premios[i] * f[(i, u, v, e)])

    prob += lpSum(objetivo_termos), "Lucro_Total"

    for idx_arco, (u, v, e, c) in enumerate(arcos):
        prob += lpSum(f[(i, u, v, e)] for i in commodities) <= c, f"cap_{u}_{v}_{e}_{idx_arco}"

    todos_vertices = range(1, num_vertices + 1)
    for i in commodities:
        origem = fontes.get(i)
        destino = sumidouros.get(i)

        for w in todos_vertices:
            if w == origem or w == destino:
                continue

            saindo = lpSum(f[(i, u, v, e)] for u, v, e, c in arcos if u == w)
            entrando = lpSum(f[(i, u, v, e)] for u, v, e, c in arcos if v == w)

            prob += (saindo - entrando == 0), f"cons_{i}_{w}"

    inicio = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    fim = time.time()

    return pulp.value(prob.objective), fim - inicio

if __name__ == "__main__":
    from leitor import ler_instancia

    caminho_instancia = "instancias/mc_instance1.max"
    
    try:
        dados = ler_instancia(caminho_instancia)
        valor_obj, tempo = resolver_p2(dados)
        
        print("\n=== Execução Direta: P2 (MCF) ===")
        print(f"Instância: {caminho_instancia}")
        print(f"Valor do Objetivo: {valor_obj}")
        print(f"Tempo de Execução: {tempo:.4f} segundos\n")
    except FileNotFoundError:
        print(f"\nFicheiro '{caminho_instancia}' não encontrado.\n")