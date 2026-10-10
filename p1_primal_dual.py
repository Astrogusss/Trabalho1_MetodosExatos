import numpy as np
import sys

def ler_instancia(caminho_arquivo):
    num_vertices = 0
    fonte = 0
    sorvedouro = 0
    arestas = []

    with open(caminho_arquivo, "r") as f:
        for linha in f:
            partes = linha.split()
            if len(partes) == 0 or partes[0] == "c":
                continue
            
            if partes[0] == "p":
                num_vertices = int(partes[2])
            elif partes[0] == "n":
                if partes[2] == "s":
                    fonte = int(partes[1])
                elif partes[2] == "t":
                    sorvedouro = int(partes[1])
            elif partes[0] == "a":
                u = int(partes[1])
                v = int(partes[2])
                cap = int(partes[3])
                arestas.append((u, v, cap))

    return num_vertices, fonte, sorvedouro, arestas

def aplicar_pivo(tableau, linha, coluna):
    tableau[linha] = tableau[linha] / tableau[linha, coluna]
    
    for i in range(len(tableau)):
        if i != linha:
            fator = tableau[i, coluna]
            tableau[i] = tableau[i] - (fator * tableau[linha])

def rodar_simplex(tableau, base, colunas_permitidas=[]):
    for iteracao in range(10000):
        custos = tableau[-1, :-1]
        
        if len(colunas_permitidas) == 0:
            coluna = int(np.argmin(custos))
            if custos[coluna] >= -0.000001:
                break 
        else:
            pos_menor = int(np.argmin(custos[colunas_permitidas]))
            coluna = colunas_permitidas[pos_menor]
            
            if custos[coluna] >= -0.000001:
                break

        menor_razao = 999999999
        linha = -1
        
        for i in range(len(tableau) - 1):
            coeficiente = tableau[i, coluna]
            if coeficiente > 0.000001:
                razao = tableau[i, -1] / coeficiente
                if razao < menor_razao:
                    menor_razao = razao
                    linha = i
                    
        if linha == -1:
            #"O problema é ilimitado."
            return -1
            
        aplicar_pivo(tableau, linha, coluna)
        base[linha] = coluna
        
    else:
        #"estourou"
        return -1

    solucao = np.zeros(tableau.shape[1] - 1)
    for i in range(len(base)):
        col = base[i]
        solucao[col] = tableau[i, -1]
        
    return solucao

def modelar_corte_minimo(n, s, t, arestas):
    m = len(arestas)
    linhas = 2 * m + 2
    colunas = m + n + 2 * m 

    A = np.zeros((linhas, colunas))
    b = np.zeros(linhas)
    c = np.zeros(colunas)

    for k in range(len(arestas)):
        u = arestas[k][0]
        v = arestas[k][1]
        capacidade = arestas[k][2]

        col_u = m + u - 1
        col_v = m + v - 1
        ida = 2 * k
        volta = 2 * k + 1

        c[k] = capacidade 

        A[ida, k] = 1
        A[ida, col_u] = -1
        A[ida, col_v] = 1
        A[ida, m + n + ida] = -1

        A[volta, k] = 1
        A[volta, col_u] = 1
        A[volta, col_v] = -1
        A[volta, m + n + volta] = -1

    A[-2, m + s - 1] = 1
    A[-1, m + t - 1] = 1
    b[-1] = 1 

    return A, b, c

def resolver_primal_dual(A, b, c):
    linhas = len(A)
    colunas = len(A[0])
    
    tableau = np.zeros((linhas + 1, colunas + linhas + 1))
    
    for i in range(linhas):
        for j in range(colunas):
            tableau[i][j] = A[i][j]
            
    for i in range(linhas):
        tableau[i][colunas + i] = 1
        
    for i in range(linhas):
        tableau[i][-1] = b[i]
        
    for i in range(linhas):
        tableau[-1][colunas + i] = 1
        
    for i in range(linhas):
        for j in range(len(tableau[0])):
            tableau[-1][j] = tableau[-1][j] - tableau[i][j]

    base = list(range(colunas, colunas + linhas))
    artificiais = list(range(colunas, colunas + linhas))
    pi = np.zeros(linhas) 

    it = 0
    for i in range(int(100000)):
        it += 1
        custo_reduzido = c - pi.dot(A)
        #"Erro: O problema Dual perdeu a viabilidade."
        if min(custo_reduzido) < -0.000001:
            return -1

        J = []
        for j in range(colunas):
            if abs(custo_reduzido[j]) <= 0.000001:
                J.append(j)
        
        solucao = rodar_simplex(tableau, base, J + artificiais)
        
        if type(solucao) == int:
            return -1

        soma_artificiais = sum(solucao[colunas:])
        # print(f"Iteração {it}: Variáveis artificiais = {soma_artificiais:.6f} | Custo dual = {b.dot(pi):.6f}")
        
        if soma_artificiais <= 0.000001:
            solucao_final = []
            valor_otimo = 0
            
            for i in range(colunas):
                solucao_final.append(solucao[i])
                valor_otimo = valor_otimo + (c[i] * solucao[i])
                
            return solucao_final, valor_otimo, pi
            
        direcao_dual = np.zeros(linhas)
        for i in range(linhas):
            valor_artificial = tableau[-1][colunas + i]
            direcao_dual[i] = 1 - valor_artificial
            
        wa = direcao_dual.dot(A)
        
        passos = []
        for j in range(colunas):
            if j not in J:
                if wa[j] > 0.000001:
                    valor_passo = custo_reduzido[j] / wa[j]
                    passos.append(valor_passo)
        
        if len(passos) == 0:
            return -1
            
        menor_passo = min(passos)
        pi = pi + (menor_passo * direcao_dual)

    return -1

if __name__ == "__main__":
    
    nomes_arquivos = ["instance1.min", "instance2.min", "instance3.min", "instance4.min", "instance5.min"]
        
    for nome in nomes_arquivos:
        print("Testando o arquivo:", nome)
        
        n, s, t, arestas = ler_instancia(nome)
        A, b, c = modelar_corte_minimo(n, s, t, arestas)

        resultado = resolver_primal_dual(A, b, c)

        if resultado == -1:
            print("A execução parou")
        else:
            solucao = resultado[0]
            valor_otimo = resultado[1]
            var_duais = resultado[2]

            num_arestas = len(arestas)
            
            distancias = []
            for i in range(n):
                distancias.append(solucao[num_arestas + i])
            
            conjunto_S = []
            for u in range(1, n + 1):
                if distancias[u - 1] < 0.5:
                    conjunto_S.append(u)
            
            arestas_cortadas = []
            for i in range(len(arestas)):
                u = arestas[i][0]
                v = arestas[i][1]
                
                if (u in conjunto_S and v not in conjunto_S) or (v in conjunto_S and u not in conjunto_S):
                    arestas_cortadas.append((u, v))
            
            print("Valor Primal:", valor_otimo)
            print("Valor Dual:", b.dot(var_duais))
            print("Vértices no lado da Fonte:", conjunto_S)
            print("Arestas no corte:", arestas_cortadas)

            print("\n Variáveis Primais Não Nulas ")
            for i in range(len(solucao)):
                valor = solucao[i]
                
                if valor > 0.000001 or valor < -0.000001:
                    valor_arredondado = round(valor, 4) 
                    
                    if i < num_arestas:
                        u = arestas[i][0]
                        v = arestas[i][1]
                        print(f"x_{i + 1} (aresta {u} para {v}) = {valor_arredondado}")
                    elif i < num_arestas + n:
                        vertice = i - num_arestas + 1
                        print(f"d_{vertice} = {valor_arredondado}")
                    else:
                        excesso = i - num_arestas - n + 1
                        print(f"excesso_{excesso} = {valor_arredondado}")

            print("\nVariáveis Duais Não Nulas")
            for i in range(len(var_duais)):
                valor = var_duais[i]
                
                if valor > 0.000001 or valor < -0.000001:
                    valor_arredondado = round(valor, 4)
                    
                    if i < (2 * num_arestas):
                        indice_aresta = int(i / 2)
                        u = arestas[indice_aresta][0]
                        v = arestas[indice_aresta][1]
                        
                        if i % 2 == 0:
                            sentido = "ida"
                        else:
                            sentido = "volta"
                            
                        print(f"pi_{i + 1} (aresta {u} para {v}, {sentido}) = {valor_arredondado}")
                    elif i == (2 * num_arestas):
                        print(f"pi_{i + 1} (distância da fonte s={s} é 0) = {valor_arredondado}")
                    else:
                        print(f"pi_{i + 1} (distância do sorvedouro t={t} é 1) = {valor_arredondado}")