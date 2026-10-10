def ler_instancia(caminho_arquivo):
    dados = {
        'tipo_problema': None,
        'num_vertices': 0,
        'num_arestas': 0,
        'num_commodities': None,
        's': None,
        't': None,
        'fontes': {},
        'sumidouros': {},
        'premios': {},
        'arestas': []
    }
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            
            partes = linha.split()
            tipo = partes[0]
            
            if tipo == 'c':
                continue
            elif tipo == 'p':
                dados['tipo_problema'] = partes[1]
                dados['num_vertices'] = int(partes[2])
                if len(partes) > 4:
                    dados['num_commodities'] = int(partes[4])
            elif tipo == 'n':
                no = int(partes[1])
                papel = partes[2]
                if len(partes) > 3:
                    commodity = int(partes[3])
                    if papel == 's':
                        dados['fontes'][commodity] = no
                    elif papel == 't':
                        dados['sumidouros'][commodity] = no
                else:
                    if papel == 's':
                        dados['s'] = no
                    elif papel == 't':
                        dados['t'] = no
            elif tipo == 'w':
                commodity = int(partes[1])
                dados['premios'][commodity] = int(partes[2])
            elif tipo == 'a':
                dados['arestas'].append((int(partes[1]), int(partes[2]), int(partes[3])))
                
    dados['num_arestas'] = len(dados['arestas'])
    return dados