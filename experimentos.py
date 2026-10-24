from __future__ import annotations
import time
import random
import csv
from typing import List, Dict, Any, Optional
from modelos import ContaBancaria
from avl import ArvoreAVL
from rubro_negra import ArvoreRubroNegra


def gerar_contas_crescentes(n: int) -> List[ContaBancaria]:
    return [
        ContaBancaria(
            numero_conta=i,
            titular=f"Titular {i}",
            agencia="0001",
            tipo="Corrente",
            saldo=1000.0 + (i % 500)
        )
        for i in range(1, n + 1)
    ]


def gerar_contas_aleatorias(n: int, semente: int = 42) -> List[ContaBancaria]:
    rng = random.Random(semente)
    limite_superior = max(n * 20, 1000000)
    chaves = rng.sample(range(1, limite_superior), n)
    tipos = ["Corrente", "Poupanca", "Salario"]
    return [
        ContaBancaria(
            numero_conta=chave,
            titular=f"Titular {chave}",
            agencia="0001",
            tipo=tipos[i % 3],
            saldo=500.0 + (chave % 10000)
        )
        for i, chave in enumerate(chaves)
    ]


def gerar_chaves_busca(contas_inseridas: List[ContaBancaria], semente: int = 42) -> List[int]:
    rng = random.Random(semente + 100)
    chaves_existentes = [c.numero_conta for c in contas_inseridas]
    qtd = len(chaves_existentes)
    metade = qtd // 2

    amostra_existentes = rng.sample(chaves_existentes, metade) if metade > 0 else chaves_existentes[:]
    conjunto_existentes = set(chaves_existentes)

    amostra_inexistentes: List[int] = []
    candidato = max(chaves_existentes) + 100
    while len(amostra_inexistentes) < metade:
        if candidato not in conjunto_existentes:
            amostra_inexistentes.append(candidato)
        candidato += rng.randint(1, 10)

    chaves_totais = amostra_existentes + amostra_inexistentes
    rng.shuffle(chaves_totais)
    return chaves_totais


def executar_experimento_crescente(n: int) -> Dict[str, Any]:
    contas = gerar_contas_crescentes(n)

    avl = ArvoreAVL(modo_detalhado=False)
    inicio_avl = time.perf_counter()
    for conta in contas:
        avl.inserir(conta)
    tempo_avl = (time.perf_counter() - inicio_avl) * 1000.0

    rb = ArvoreRubroNegra(modo_detalhado=False)
    inicio_rb = time.perf_counter()
    for conta in contas:
        rb.inserir(conta)
    tempo_rb = (time.perf_counter() - inicio_rb) * 1000.0

    return {
        "n": n,
        "cenario": "Ordem Crescente (Exp. A)",
        "avl_altura": avl.altura,
        "rb_altura": rb.altura,
        "avl_rot_ins": avl.estatisticas.total_rotacoes,
        "rb_rot_ins": rb.estatisticas.total_rotacoes,
        "rb_rec_ins": rb.estatisticas.recoloracoes,
        "avl_tempo_ins_ms": tempo_avl,
        "rb_tempo_ins_ms": tempo_rb,
    }


def executar_experimentos_completos(n: int, semente: int = 42) -> Dict[str, Any]:
    contas = gerar_contas_aleatorias(n, semente)

    avl = ArvoreAVL(modo_detalhado=False)
    inicio_avl_ins = time.perf_counter()
    for conta in contas:
        avl.inserir(conta)
    tempo_avl_ins = (time.perf_counter() - inicio_avl_ins) * 1000.0

    rb = ArvoreRubroNegra(modo_detalhado=False)
    inicio_rb_ins = time.perf_counter()
    for conta in contas:
        rb.inserir(conta)
    tempo_rb_ins = (time.perf_counter() - inicio_rb_ins) * 1000.0

    avl_altura_pos_ins = avl.altura
    rb_altura_pos_ins = rb.altura

    avl_rot_ins = avl.estatisticas.total_rotacoes
    rb_rot_ins = rb.estatisticas.total_rotacoes
    rb_rec_ins = rb.estatisticas.recoloracoes

    chaves_busca = gerar_chaves_busca(contas, semente)

    avl.estatisticas.nos_visitados = 0
    inicio_avl_busca = time.perf_counter()
    for chave in chaves_busca:
        avl.buscar(chave)
    tempo_avl_busca = (time.perf_counter() - inicio_avl_busca) * 1000.0
    media_visitados_avl = avl.estatisticas.nos_visitados / len(chaves_busca) if chaves_busca else 0.0

    rb.estatisticas.nos_visitados = 0
    inicio_rb_busca = time.perf_counter()
    for chave in chaves_busca:
        rb.buscar(chave)
    tempo_rb_busca = (time.perf_counter() - inicio_rb_busca) * 1000.0
    media_visitados_rb = rb.estatisticas.nos_visitados / len(chaves_busca) if chaves_busca else 0.0

    rng_rem = random.Random(semente + 200)
    percentuais = [10, 30, 50]
    dados_remocao: Dict[int, Dict[str, Any]] = {}

    for pct in percentuais:
        qtd_remover = max(1, int(n * (pct / 100.0)))
        chaves_remover = rng_rem.sample([c.numero_conta for c in contas], qtd_remover)

        avl_clone = ArvoreAVL(modo_detalhado=False)
        for c in contas:
            avl_clone.inserir(c)
        avl_clone.estatisticas.resetar()

        rb_clone = ArvoreRubroNegra(modo_detalhado=False)
        for c in contas:
            rb_clone.inserir(c)
        rb_clone.estatisticas.resetar()

        alt_antes_avl = avl_clone.altura
        alt_antes_rb = rb_clone.altura

        inicio_rem_avl = time.perf_counter()
        for ch in chaves_remover:
            avl_clone.remover(ch)
        t_rem_avl = (time.perf_counter() - inicio_rem_avl) * 1000.0

        inicio_rem_rb = time.perf_counter()
        for ch in chaves_remover:
            rb_clone.remover(ch)
        t_rem_rb = (time.perf_counter() - inicio_rem_rb) * 1000.0

        dados_remocao[pct] = {
            "qtd_removida": qtd_remover,
            "alt_antes_avl": alt_antes_avl,
            "alt_depois_avl": avl_clone.altura,
            "alt_antes_rb": alt_antes_rb,
            "alt_depois_rb": rb_clone.altura,
            "rot_avl": avl_clone.estatisticas.total_rotacoes,
            "rot_rb": rb_clone.estatisticas.total_rotacoes,
            "rec_rb": rb_clone.estatisticas.recoloracoes,
            "tempo_avl_ms": t_rem_avl,
            "tempo_rb_ms": t_rem_rb,
        }

    return {
        "n": n,
        "semente": semente,
        "cenario": "Ordem Aleatoria (Exp. B, C e D)",
        "avl_altura_final": avl_altura_pos_ins,
        "rb_altura_final": rb_altura_pos_ins,
        "avl_rot_ins": avl_rot_ins,
        "rb_rot_ins": rb_rot_ins,
        "rb_rec_ins": rb_rec_ins,
        "avl_tempo_ins_ms": tempo_avl_ins,
        "rb_tempo_ins_ms": tempo_rb_ins,
        "avl_media_busca": media_visitados_avl,
        "rb_media_busca": media_visitados_rb,
        "avl_tempo_busca_ms": tempo_avl_busca,
        "rb_tempo_busca_ms": tempo_rb_busca,
        "remocao_detalhada": dados_remocao,
        "avl_rot_rem_30": dados_remocao[30]["rot_avl"],
        "rb_rot_rem_30": dados_remocao[30]["rot_rb"],
        "rb_rec_rem_30": dados_remocao[30]["rec_rb"],
        "avl_tempo_rem_30_ms": dados_remocao[30]["tempo_avl_ms"],
        "rb_tempo_rem_30_ms": dados_remocao[30]["tempo_rb_ms"],
    }


def imprimir_tabela_1_formatada(res_aleatorio: Dict[str, Any], res_crescente: Optional[Dict[str, Any]] = None) -> None:
    n = res_aleatorio["n"]
    print("\n" + "=" * 80)
    print(f"        TABELA 1: RESULTADOS COMPARATIVOS OFICIAIS (N = {n:,})")
    print("=" * 80)
    print(f"{'METRICA OBRIGATORIA':<35} | {'ARVORE AVL':<18} | {'ARVORE RUBRO-NEGRA':<20}")
    print("-" * 80)
    print(f"{'Altura final (Apos Insercao)':<35} | {res_aleatorio['avl_altura_final']:<18} | {res_aleatorio['rb_altura_final']:<20}")
    print(f"{'Rotacoes na insercao':<35} | {res_aleatorio['avl_rot_ins']:<18} | {res_aleatorio['rb_rot_ins']:<20}")
    print(f"{'Rotacoes na remocao (30% dos nos)':<35} | {res_aleatorio['avl_rot_rem_30']:<18} | {res_aleatorio['rb_rot_rem_30']:<20}")
    print(f"{'Recoloracoes (Insercao)':<35} | {'N/A':<18} | {res_aleatorio['rb_rec_ins']:<20}")
    print(f"{'Recoloracoes (Remocao 30%)':<35} | {'N/A':<18} | {res_aleatorio['rb_rec_rem_30']:<20}")
    print(f"{'Media de nos visitados na busca':<35} | {res_aleatorio['avl_media_busca']:<18.2f} | {res_aleatorio['rb_media_busca']:<20.2f}")
    print(f"{'Tempo total de insercao (ms)':<35} | {res_aleatorio['avl_tempo_ins_ms']:<18.3f} | {res_aleatorio['rb_tempo_ins_ms']:<20.3f}")
    print(f"{'Tempo total de busca (ms)':<35} | {res_aleatorio['avl_tempo_busca_ms']:<18.3f} | {res_aleatorio['rb_tempo_busca_ms']:<20.3f}")
    print(f"{'Tempo total de remocao (ms, 30%)':<35} | {res_aleatorio['avl_tempo_rem_30_ms']:<18.3f} | {res_aleatorio['rb_tempo_rem_30_ms']:<20.3f}")

    if res_crescente is not None:
        print("-" * 80)
        print(">>> COMPORTAMENTO EM ORDEM CRESCENTE (EXPERIMENTO A - PIOR CASO ABB):")
        print(f"  * Altura Final               : AVL = {res_crescente['avl_altura']} | Rubro-Negra = {res_crescente['rb_altura']}")
        print(f"  * Rotacoes de Insercao       : AVL = {res_crescente['avl_rot_ins']} | Rubro-Negra = {res_crescente['rb_rot_ins']}")
        print(f"  * Recoloracoes Rubro-Negra   : {res_crescente['rb_rec_ins']}")
        print(f"  * Tempo de Insercao (ms)     : AVL = {res_crescente['avl_tempo_ins_ms']:.3f} ms | Rubro-Negra = {res_crescente['rb_tempo_ins_ms']:.3f} ms")

    print("-" * 80)
    print(">>> DETALHAMENTO DE REMOCOES PARCIAIS (EXPERIMENTO D):")
    for pct, info in res_aleatorio["remocao_detalhada"].items():
        print(
            f"  * Remocao {pct}% ({info['qtd_removida']} nos): "
            f"AVL h({info['alt_antes_avl']}->{info['alt_depois_avl']}), rot={info['rot_avl']}, t={info['tempo_avl_ms']:.3f}ms | "
            f"RN h({info['alt_antes_rb']}->{info['alt_depois_rb']}), rot={info['rot_rb']}, rec={info['rec_rb']}, t={info['tempo_rb_ms']:.3f}ms"
        )
    print("=" * 80 + "\n")


def salvar_resultados_csv(lista_resultados: List[Dict[str, Any]], arquivo: str = "resultados_experimentos.csv") -> None:
    cabecalhos = [
        "n", "semente", "cenario",
        "avl_altura_final", "rb_altura_final",
        "avl_rot_ins", "rb_rot_ins", "rb_rec_ins",
        "avl_tempo_ins_ms", "rb_tempo_ins_ms",
        "avl_media_busca", "rb_media_busca",
        "avl_tempo_busca_ms", "rb_tempo_busca_ms",
        "avl_rot_rem_30", "rb_rot_rem_30", "rb_rec_rem_30",
        "avl_tempo_rem_30_ms", "rb_tempo_rem_30_ms"
    ]

    with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cabecalhos, extrasaction="ignore")
        writer.writeheader()
        for res in lista_resultados:
            writer.writerow(res)


def salvar_relatorio_markdown(lista_resultados: List[Dict[str, Any]], arquivo: str = "resultados_experimentos.md") -> None:
    linhas: List[str] = [
        "# Relatorio de Resultados Experimentais (Trabalho Pratico I - AED II)",
        "",
        "## Tabela 1 Consolidada: Comparacao AVL vs Rubro-Negra",
        "",
        "| N | Estrutura | Altura Final | Rotacoes Ins | Rotacoes Rem (30%) | Recoloracoes Ins | Recoloracoes Rem | Media Nos Busca | Tempo Ins (ms) | Tempo Busca (ms) | Tempo Rem (ms) |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]

    for res in lista_resultados:
        n = res["n"]
        linhas.append(
            f"| {n:,} | AVL | {res['avl_altura_final']} | {res['avl_rot_ins']:,} | {res['avl_rot_rem_30']:,} | N/A | N/A | "
            f"{res['avl_media_busca']:.2f} | {res['avl_tempo_ins_ms']:.3f} | {res['avl_tempo_busca_ms']:.3f} | {res['avl_tempo_rem_30_ms']:.3f} |"
        )
        linhas.append(
            f"| {n:,} | Rubro-Negra | {res['rb_altura_final']} | {res['rb_rot_ins']:,} | {res['rb_rot_rem_30']:,} | {res['rb_rec_ins']:,} | {res['rb_rec_rem_30']:,} | "
            f"{res['rb_media_busca']:.2f} | {res['rb_tempo_ins_ms']:.3f} | {res['rb_tempo_busca_ms']:.3f} | {res['rb_tempo_rem_30_ms']:.3f} |"
        )

    with open(arquivo, mode="w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


def executar_bateria_experimentos(tamanhos_personalizados: Optional[List[int]] = None) -> None:
    while True:
        print("\n" + "=" * 70)
        print("          BATERIA DE EXPERIMENTOS CIENTIFICOS (SECAO 5 - AED II)")
        print("=" * 70)
        print("1. Executar Bateria Padrao do Edital (N = 100, 1.000 e 10.000)")
        print("2. Executar Bateria Rapida de Validacao (N = 100)")
        print("3. Executar com Tamanho Personalizado (Definir N livremente)")
        print("0. Voltar ao Menu Principal")
        print("-" * 70)

        opcao = input("Selecione a opcao desejada: ").strip()

        if opcao == "0":
            break
        elif opcao == "1":
            tamanhos = [100, 1000, 10000]
        elif opcao == "2":
            tamanhos = [100]
        elif opcao == "3":
            entrada = input("Digite o tamanho N desejado (inteiro positivo, ex: 500, 5000): ").strip()
            if not entrada.isdigit() or int(entrada) <= 0:
                print("[Erro] Tamanho invalido. Operacao cancelada.")
                continue
            tamanhos = [int(entrada)]
        else:
            print("[Erro] Opcao invalida. Digite 1, 2, 3 ou 0.")
            continue

        todos_resultados: List[Dict[str, Any]] = []

        for n in tamanhos:
            print(f"\n[Executando] Iniciando testes rigorosos para N = {n:,} contas...")
            res_crescente = executar_experimento_crescente(n)
            res_aleatorio = executar_experimentos_completos(n, semente=42)
            imprimir_tabela_1_formatada(res_aleatorio, res_crescente)
            todos_resultados.append(res_aleatorio)

        deseja_salvar = input("\nDeseja exportar esses resultados para arquivo CSV e Markdown? (s/N) [padrao N]: ").strip().lower()
        if deseja_salvar == "s":
            salvar_resultados_csv(todos_resultados)
            salvar_relatorio_markdown(todos_resultados)
            print("[Concluido com Sucesso] Resultados brutos exportados:")
            print("  -> Planilha CSV gerada : resultados_experimentos.csv")
            print("  -> Relatorio Markdown : resultados_experimentos.md")
        else:
            print("[Info] Nenhum arquivo foi gerado no disco.")

        input("\nPressione ENTER para voltar ao menu de experimentos...")
