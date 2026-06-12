"""
Ativacao opcional do backend de GPU (nx-cugraph) para o NetworkX.

A ideia e habilitar aceleracao por GPU se for possível e caso contrário enviar para CPU:
o NetworkX despacha automaticamente os algoritmos suportados (Louvain,
PageRank, k-core, HITS, componentes conexos) para a GPU quando o backend
nx-cugraph esta instalado e habilitado.

Requisitos: Linux (ou WSL2 no Windows), GPU NVIDIA com compute capability
7.0+, CUDA 12.2+ e o pacote nx-cugraph. Instale o pacote correspondente a sua versao do CUDA:

    CUDA 12.x:
        pip install cupy-cuda12x nx-cugraph-cu12 --extra-index-url https://pypi.nvidia.com

    CUDA 13.x:
        pip install cupy-cuda13x nx-cugraph-cu13 --extra-index-url https://pypi.nvidia.com

Uso tipico (a partir de um runner):

    from src.gpu import enable_gpu
    enable_gpu()  # antes de chamar as analises
"""

import os


INSTALL_HINT = (
    "pip install nx-cugraph-cu12 --extra-index-url https://pypi.nvidia.com"
)


def enable_gpu(verbose: bool = True) -> bool:

    """
    Tenta habilitar o backend nx-cugraph do NetworkX em tempo de execucao.

    Retorna True se o backend foi habilitado, False caso contrario
    (por exemplo, se nx-cugraph nao estiver instalado). Em caso de falha,
    o codigo continua normalmente na CPU.
    """
    os.environ["NX_CUGRAPH_AUTOCONFIG"] = "True"

    try:
        import nx_cugraph  # noqa: F401
    except ImportError:
        if verbose:
            print("[gpu] Backend nx-cugraph nao encontrado; rodando na CPU.")
            print(f"[gpu] Para habilitar a GPU, instale: {INSTALL_HINT}")
        return False

    try:
        import networkx as nx
    except ImportError:
        if verbose:
            print("[gpu] NetworkX nao encontrado; impossivel habilitar a GPU.")
        return False

    # Configura a prioridade de backend em tempo de execucao. O NetworkX le
    # essa configuracao no momento da chamada de cada algoritmo, entao
    # defini-la aqui e suficiente. Tenta variacoes de API entre versoes.
    enabled = False
    try:
        nx.config.backend_priority = ["cugraph"]
        enabled = True
    except Exception:
        try:
            nx.config.backend_priority.algos = ["cugraph"]
            enabled = True
        except Exception:
            enabled = False

    if verbose:
        if enabled:
            print("[gpu] Backend nx-cugraph habilitado.")
            print("[gpu] Algoritmos suportados (Louvain, PageRank, "
                  "HITS, componentes, k-core) rodarao na GPU.")
            nx.config.warnings_to_ignore.add("cache")
        else:
            print("[gpu] nx-cugraph esta instalado, mas nao foi possivel "
                  "configurar o backend nesta versao do NetworkX.")
            print("[gpu] Tente: NX_CUGRAPH_AUTOCONFIG=True python <script>.py")

    return enabled
