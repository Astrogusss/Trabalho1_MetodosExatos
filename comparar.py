\
import os
import glob
from p1_primal_dual import modelar_corte_minimo, resolver_primal_dual

from leitor import ler_instancia
from p1_pulp import resolver_p1
from p2_pulp import resolver_p2

def main():
    pasta_instancias = "instancias"
    arquivos = sorted(glob.glob(os.path.join(pasta_instancias, "*")))

    if not arquivos:
        print(f"Nenhum arquivo encontrado na pasta '{pasta_instancias}/'.")
        return

    header = f"{'Instância':<25} | {'Problema':<8} | {'Algoritmo':<10} | {'PuLP':<10} | {'Bateu?'}"
    print(header)
    print("-" * len(header))

    for caminho_arquivo in arquivos:
        nome_instancia = os.path.basename(caminho_arquivo)

        try:
            dados = ler_instancia(caminho_arquivo)
        except Exception as err:
            print(f"{nome_instancia:<25} | Erro ao ler arquivo: {err}")
            continue

        if dados.get('tipo_problema') == 'mcf':
            problema = "P2"
            obj_pulp, tempo_pulp = resolver_p2(dados)
            
            obj_alg = None
        else:
            problema = "P1"
            obj_pulp, tempo_pulp = resolver_p1(dados)

            A, b, c = modelar_corte_minimo(
                dados['num_vertices'], dados['s'], dados['t'], dados['arestas']
            )
            resultado = resolver_primal_dual(A, b, c)
            if type(resultado) == int:
                obj_alg = None
            else:
                obj_alg = resultado[1]

        if obj_alg is None or obj_pulp is None:
            bateu = "—"
            str_alg = f"{obj_alg:.2f}" if obj_alg is not None else "—"
        else:
            str_alg = f"{obj_alg:.2f}"
            bateu = "sim" if abs(obj_alg - obj_pulp) < 1e-6 else "não"

        str_pulp = f"{obj_pulp:.2f}" if obj_pulp is not None else "—"

        print(f"{nome_instancia:<25} | {problema:<8} | {str_alg:<10} | {str_pulp:<10} | {bateu}")

if __name__ == "__main__":
    main()