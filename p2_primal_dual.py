import sys
import numpy as np

# Problema 1.2 - Fluxo máximo com múltiplas mercadorias

# Observações do trabalho:
# o PDF não exige conservação de fluxo no destino, então ele pode receber e mandar fluxo
# a capacidade das arestas é por sentido, como está no PDF

class PrimalDual:
    def __init__(self, c, A, b, maximizar=False, igualdades=None):
        self.cOrig = list(c)
        self.c = []
        for valor in c:
            if maximizar:
                self.c.append(-valor)
            else:
                self.c.append(valor)

        self.b = list(b)
        self.qtdLin = len(A)
        self.qtdVar = len(c)
        self.igualdades = igualdades or []

        # as restrições que não são igualdade ganham uma variável de folga
        desigs = []
        for i in range(self.qtdLin):
            if i not in self.igualdades:
                desigs.append(i)
        self.qtdCol = self.qtdVar + len(desigs)

        self.colunasA = []
        for j in range(self.qtdCol):
            self.colunasA.append([])
        for i in range(self.qtdLin):
            for j in range(self.qtdVar):
                if A[i][j] != 0:
                    self.colunasA[j].append((i, A[i][j]))
        for k in range(len(desigs)):
            self.colunasA[self.qtdVar + k].append((desigs[k], 1.0))
            self.c.append(0.0)

        self.tab = None
        self.base = []
        self.y = None

    def iniciaDual(self):
        menor = 0
        for j in range(self.qtdCol):
            if self.c[j] < menor:
                menor = self.c[j]

        y = []
        for i in range(self.qtdLin):
            if i in self.igualdades:
                y.append(0.0)
            else:
                y.append(menor)

        # confere se o y escolhido realmente é viável (custo reduzido nunca negativo)
        for j in range(self.qtdCol):
            soma = 0
            for (i, valor) in self.colunasA[j]:
                soma += y[i] * valor
            if soma > self.c[j] + 1e-9:
                raise ValueError("dual inicial não é viável")
        return y

    def montaTab(self):
        # monta o tableau da fase 1
        tamanho = self.qtdCol + self.qtdLin + 1
        self.tab = np.zeros((self.qtdLin + 1, tamanho))

        for j in range(self.qtdCol):
            for (i, valor) in self.colunasA[j]:
                self.tab[i, j] = valor

        for i in range(self.qtdLin):
            self.tab[i, self.qtdCol + i] = 1
            self.tab[i, -1] = self.b[i]

        for j in range(self.qtdCol):
            for (i, valor) in self.colunasA[j]:
                self.tab[-1, j] -= valor
        for i in range(self.qtdLin):
            self.tab[-1, -1] -= self.b[i]

        self.base = []
        for i in range(self.qtdLin):
            self.base.append(self.qtdCol + i)

    def entra(self, justas, bland=False):
        melhor = None
        menor = -1e-10
        for j in justas:
            custo = self.tab[-1, j]
            if custo < menor:
                melhor = j
                if bland:
                    return melhor
                menor = custo
        return melhor

    def sai(self, col):
        colunaPivo = self.tab[:, col].tolist()
        ladoDir = self.tab[:, -1].tolist()

        candidatas = []
        menor = None
        for i in range(self.qtdLin):
            if colunaPivo[i] > 1e-10:
                razao = ladoDir[i] / colunaPivo[i]
                candidatas.append((i, razao))
                if menor is None or razao < menor:
                    menor = razao

        if menor is None:
            return None

        # se várias linhas empatarem, fica com a que tem a variável de menor índice na base
        esc = None
        for (i, razao) in candidatas:
            if razao <= menor + 1e-10:
                if esc is None or self.base[i] < self.base[esc]:
                    esc = i
        return esc

    def fazPivo(self, lin, col):
        # faz o pivoteamento
        linhaPivo = self.tab[lin].tolist()
        pivo = linhaPivo[col]
        colsMuda = []
        for j in range(len(linhaPivo)):
            if linhaPivo[j] != 0:
                linhaPivo[j] = linhaPivo[j] / pivo
                colsMuda.append(j)
                self.tab[lin, j] = linhaPivo[j]

        colunaPivo = self.tab[:, col].tolist()
        for i in range(len(colunaPivo)):
            if i != lin:
                fat = colunaPivo[i]
                if abs(fat) > 1e-12:
                    linhaI = self.tab[i]
                    for j in colsMuda:
                        linhaI[j] = linhaI[j] - fat * linhaPivo[j]

        self.base[lin] = col

    def resolver(self, maxIter=100000, mostrar=False):
        # faz o primal dual
        y = self.iniciaDual()
        self.montaTab()

        for iteracao in range(maxIter):
            custoRed = []
            justas = []
            for j in range(self.qtdCol):
                soma = 0
                for (i, valor) in self.colunasA[j]:
                    soma += y[i] * valor
                custoRed.append(self.c[j] - soma)
                if abs(custoRed[j]) < 1e-9:
                    justas.append(j)

            pivos = 0
            semMelhora = 0
            bland = False
            while True:
                col = self.entra(justas, bland)
                if col is None:
                    break
                lin = self.sai(col)
                if lin is None:
                    break
                antes = self.tab[-1, -1]
                self.fazPivo(lin, col)
                pivos += 1

                if abs(self.tab[-1, -1] - antes) < 1e-12:
                    semMelhora += 1
                    if semMelhora > 50:
                        bland = True
                else:
                    semMelhora = 0
                    bland = False

                if mostrar and pivos % 2000 == 0:
                    print(f"   ... {pivos} pivôs nesta iteração (soma das artificiais = {-self.tab[-1, -1]:.4f})", flush=True)

            somaArt = -self.tab[-1, -1]
            if mostrar:
                custoDual = 0
                for i in range(self.qtdLin):
                    custoDual += self.b[i] * y[i]
                print(f"iteracao {iteracao}: pivôs = {pivos}, |J| = {len(justas)}, soma das artificiais = {somaArt:.6f}, custo dual = {custoDual:.6f}", flush=True)

            if somaArt < 1e-8:
                self.y = y
                return self.pegaSolucao()

            dir = []
            for i in range(self.qtdLin):
                dir.append(1 - self.tab[-1, self.qtdCol + i])

            passo = None
            for j in range(self.qtdCol):
                dirA = 0
                for (i, valor) in self.colunasA[j]:
                    dirA += dir[i] * valor
                if dirA > 1e-10:
                    razao = max(custoRed[j], 0) / dirA
                    if passo is None or razao < passo:
                        passo = razao

            if passo is None:
                print("PROBLEMA INVIÁVEL")
                return None

            for i in range(self.qtdLin):
                y[i] = y[i] + passo * dir[i]

        print("MÁXIMO DE ITERAÇÕES ATINGIDO")
        return None

    def pegaSolucao(self):
        x = []
        for j in range(self.qtdVar):
            x.append(0.0)
        for i in range(self.qtdLin):
            if self.base[i] < self.qtdVar:
                x[self.base[i]] = self.tab[i, -1]

        valor = 0
        for j in range(self.qtdVar):
            valor += self.cOrig[j] * x[j]
        return x, valor


def montaProblema(qtdV, qtdE, qtdMerc, arestas, mercs):
    # monta o problema em forma de matriz. Cada aresta tem uma variável pra cada mercadoria
    colDe = {}
    cont = 0
    for i in range(1, qtdMerc + 1):
        for e in range(len(arestas)):
            colDe[(i, e)] = cont
            cont += 1
            
    c = [0.0] * (qtdMerc * qtdE)
    for i in range(1, qtdMerc + 1):
        ori, dest, prem = mercs[i - 1]
        for e in range(len(arestas)):
            if arestas[e][1] == dest:
                c[colDe[(i, e)]] = prem

    A = []
    b = []
    igualdades = []

    for e in range(len(arestas)):
        lin = [0.0] * (qtdMerc * qtdE)
        for i in range(1, qtdMerc + 1):
            lin[colDe[(i, e)]] = 1
        A.append(lin)
        b.append(arestas[e][2])

    for i in range(1, qtdMerc + 1):
        ori, dest, prem = mercs[i - 1]
        for u in range(1, qtdV + 1):
            if u == ori or u == dest:
                continue
            lin = [0.0] * (qtdMerc * qtdE)
            for e in range(len(arestas)):
                de = arestas[e][0]
                para = arestas[e][1]
                if de == u:
                    lin[colDe[(i, e)]] += 1
                if para == u:
                    lin[colDe[(i, e)]] -= 1
            A.append(lin)
            b.append(0.0)
            igualdades.append(len(A) - 1)

    return c, A, b, colDe, igualdades


def lerEntrada(cam):
    arestas = []
    oris = {}
    dests = {}
    prems = {}

    with open(cam) as arq:
        for lin in arq:
            pt = lin.split()
            if not pt or pt[0] == "c":
                continue
            if pt[0] == "p":
                qtdV, qtdE, qtdMerc = int(pt[2]), int(pt[3]), int(pt[4])
            elif pt[0] == "n":
                if pt[2] == "s":
                    oris[int(pt[3])] = int(pt[1])
                else:
                    dests[int(pt[3])] = int(pt[1])
            elif pt[0] == "w":
                prems[int(pt[1])] = float(pt[2])
            elif pt[0] == "a":
                arestas.append((int(pt[1]), int(pt[2]), float(pt[3])))

    mercs = []
    for i in range(1, qtdMerc + 1):
        mercs.append((oris[i], dests[i], prems[i]))
    return qtdV, qtdE, qtdMerc, arestas, mercs


if __name__ == "__main__":
    nomes = sys.argv[1:] if len(sys.argv) > 1 else ["mc_instance1.max"]

    for nome in nomes:
        print("Testando o arquivo:", nome, flush=True)
        qtdV, qtdE, qtdMerc, arestas, mercs = lerEntrada(nome)
        print(f"V = {qtdV}, E = {qtdE}, k = {qtdMerc}", flush=True)

        c, A, b, colDe, igualdades = montaProblema(qtdV, qtdE, qtdMerc, arestas, mercs)
        print(f"{len(A)} restrições, {len(c)} variáveis", flush=True)

        prob = PrimalDual(c, A, b, maximizar=True, igualdades=igualdades)
        res = prob.resolver(mostrar=True)

        if res is None:
            print("PROBLEMA ILIMITADO OU INVIÁVEL")
            continue

        # o valor primal já vem com o sinal certo. O dual precisa inverter o sinal
        x, otimo = res
        y = prob.y
        custoDual = 0
        for i in range(len(b)):
            custoDual += b[i] * y[i]
        print(f"\nValor Primal: {otimo:.4f}")
        print(f"Valor Dual:   {-custoDual:.4f}\n")

        # mostra o fluxo de cada mercadoria nas arestas (só os que não são zero)
        print("Fluxos não-nulos:")
        for i in range(1, qtdMerc + 1):
            ori, dest, prem = mercs[i - 1]
            print(f"  Mercadoria {i} (s={ori}, t={dest}, p={prem}):")
            for e in range(len(arestas)):
                u, v, cap = arestas[e]
                val = x[colDe[(i, e)]]
                if val > 1e-6:
                    print(f"    f{i}({u}->{v}) = {val:.4f}")

        # mostra quanto de cada aresta foi usado, somando todas as mercadorias
        print("\nUso das capacidades:")
        for e in range(len(arestas)):
            u, v, cap = arestas[e]
            usado = 0
            for i in range(1, qtdMerc + 1):
                usado += x[colDe[(i, e)]]
            print(f"  aresta {u}->{v}: {usado:.4f} / {cap}")

        # as variáveis duais das capacidades dizem quanto vale uma unidade a mais em cada aresta
        print("\nVariáveis duais não-nulas (capacidades, y = -pi):")
        for e in range(len(arestas)):
            if abs(y[e]) > 1e-6:
                u, v, cap = arestas[e]
                print(f"  y({u}->{v}) = {-y[e]:.4f}")
        print()
