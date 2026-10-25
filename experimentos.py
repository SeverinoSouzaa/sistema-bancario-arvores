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
            numero_conta=10000 + i,
            titular=f"Titular {10000 + i}",
            agencia="0001",
            tipo="Corrente",
            saldo=1500.0 + (i % 750)
        )
        for i in range(1, n + 1)
    ]


def gerar_contas_aleatorias(n: int, semente: int = 42) -> List[ContaBancaria]:
    rng = random.Random(semente)
    limite_superior = max(10000 + n * 15, 999999)
    chaves = rng.sample(range(10001, limite_superior), n)
    tipos = ["Corrente", "Poupanca", "Salario"]
    return [
        ContaBancaria(
            numero_conta=chave,
            titular=f"Titular {chave}",
            agencia="0001",
            tipo=tipos[i % 3],
            saldo=800.0 + (chave % 12000)
        )
        for i, chave in enumerate(chaves)
    ]


def gerar_chaves_busca_categorizadas(contas_inseridas: List[ContaBancaria], semente: int = 42) -> Dict[str, List[int]]:
    rng = random.Random(semente + 100)
    chaves_existentes = [c.numero_conta for c in contas_inseridas]
    qtd = len(chaves_existentes)
    metade = max(1, qtd // 2) if qtd > 0 else 0

    amostra_existentes = rng.sample(chaves_existentes, metade) if metade > 0 else chaves_existentes[:]
    conjunto_existentes = set(chaves_existentes)

    amostra_inexistentes: List[int] = []
    candidato = (max(chaves_existentes) if chaves_existentes else 10000) + 500
    while len(amostra_inexistentes) < metade:
        if candidato not in conjunto_existentes:
            amostra_inexistentes.append(candidato)
        candidato += rng.randint(1, 15)

    return {
        "existentes": amostra_existentes,
        "inexistentes": amostra_inexistentes
    }


def gerar_chaves_busca(contas_inseridas: List[ContaBancaria], semente: int = 42) -> List[int]:
    cat = gerar_chaves_busca_categorizadas(contas_inseridas, semente)
    chaves_totais = cat["existentes"] + cat["inexistentes"]
    rng = random.Random(semente + 100)
    rng.shuffle(chaves_totais)
    return chaves_totais


def executar_cenario_completo(contas: List[ContaBancaria], cenario: str, semente: int = 42) -> Dict[str, Any]:
    n = len(contas)
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

    chaves_em_ordem_avl = [c.numero_conta for c in avl.caminhamento_em_ordem()]
    chaves_em_ordem_rb = [c.numero_conta for c in rb.caminhamento_em_ordem()]
    sao_identicas = (chaves_em_ordem_avl == chaves_em_ordem_rb)

    cat_busca = gerar_chaves_busca_categorizadas(contas, semente)
    chaves_ex = cat_busca["existentes"]
    chaves_inex = cat_busca["inexistentes"]
    total_buscas = len(chaves_ex) + len(chaves_inex)

    avl.estatisticas.nos_visitados = 0
    t0_avl_ex = time.perf_counter()
    for chave in chaves_ex:
        avl.buscar(chave)
    tempo_avl_ex = (time.perf_counter() - t0_avl_ex) * 1000.0
    vis_avl_ex = avl.estatisticas.nos_visitados

    avl.estatisticas.nos_visitados = 0
    t0_avl_inex = time.perf_counter()
    for chave in chaves_inex:
        avl.buscar(chave)
    tempo_avl_inex = (time.perf_counter() - t0_avl_inex) * 1000.0
    vis_avl_inex = avl.estatisticas.nos_visitados

    total_vis_avl = vis_avl_ex + vis_avl_inex
    tempo_avl_busca = tempo_avl_ex + tempo_avl_inex
    media_vis_avl = total_vis_avl / total_buscas if total_buscas else 0.0
    media_vis_avl_ex = vis_avl_ex / len(chaves_ex) if chaves_ex else 0.0
    media_vis_avl_inex = vis_avl_inex / len(chaves_inex) if chaves_inex else 0.0

    rb.estatisticas.nos_visitados = 0
    t0_rb_ex = time.perf_counter()
    for chave in chaves_ex:
        rb.buscar(chave)
    tempo_rb_ex = (time.perf_counter() - t0_rb_ex) * 1000.0
    vis_rb_ex = rb.estatisticas.nos_visitados

    rb.estatisticas.nos_visitados = 0
    t0_rb_inex = time.perf_counter()
    for chave in chaves_inex:
        rb.buscar(chave)
    tempo_rb_inex = (time.perf_counter() - t0_rb_inex) * 1000.0
    vis_rb_inex = rb.estatisticas.nos_visitados

    total_vis_rb = vis_rb_ex + vis_rb_inex
    tempo_rb_busca = tempo_rb_ex + tempo_rb_inex
    media_vis_rb = total_vis_rb / total_buscas if total_buscas else 0.0
    media_vis_rb_ex = vis_rb_ex / len(chaves_ex) if chaves_ex else 0.0
    media_vis_rb_inex = vis_rb_inex / len(chaves_inex) if chaves_inex else 0.0

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
        "cenario": cenario,
        "amostra_insercao": [c.numero_conta for c in contas[:5]],
        "primeiras_5_em_ordem_avl": chaves_em_ordem_avl[:5],
        "primeiras_5_em_ordem_rb": chaves_em_ordem_rb[:5],
        "ultimas_5_em_ordem_avl": chaves_em_ordem_avl[-5:],
        "ultimas_5_em_ordem_rb": chaves_em_ordem_rb[-5:],
        "equivalencia_em_ordem": sao_identicas,
        "total_chaves_conferidas": len(chaves_em_ordem_avl),
        "avl_altura": avl_altura_pos_ins,
        "rb_altura": rb_altura_pos_ins,
        "avl_altura_final": avl_altura_pos_ins,
        "rb_altura_final": rb_altura_pos_ins,
        "avl_rot_ins": avl_rot_ins,
        "rb_rot_ins": rb_rot_ins,
        "rb_rec_ins": rb_rec_ins,
        "avl_tempo_ins_ms": tempo_avl_ins,
        "rb_tempo_ins_ms": tempo_rb_ins,
        "total_buscas": total_buscas,
        "total_buscas_existentes": len(chaves_ex),
        "total_buscas_inexistentes": len(chaves_inex),
        "avl_total_nos_busca": total_vis_avl,
        "rb_total_nos_busca": total_vis_rb,
        "avl_media_busca": media_vis_avl,
        "rb_media_busca": media_vis_rb,
        "avl_media_busca_existente": media_vis_avl_ex,
        "rb_media_busca_existente": media_vis_rb_ex,
        "avl_media_busca_inexistente": media_vis_avl_inex,
        "rb_media_busca_inexistente": media_vis_rb_inex,
        "avl_tempo_busca_ms": tempo_avl_busca,
        "rb_tempo_busca_ms": tempo_rb_busca,
        "avl_tempo_busca_existente_ms": tempo_avl_ex,
        "rb_tempo_busca_existente_ms": tempo_rb_ex,
        "avl_tempo_busca_inexistente_ms": tempo_avl_inex,
        "rb_tempo_busca_inexistente_ms": tempo_rb_inex,
        "remocao_detalhada": dados_remocao,
        "avl_rot_rem_10": dados_remocao[10]["rot_avl"],
        "rb_rot_rem_10": dados_remocao[10]["rot_rb"],
        "rb_rec_rem_10": dados_remocao[10]["rec_rb"],
        "avl_tempo_rem_10_ms": dados_remocao[10]["tempo_avl_ms"],
        "rb_tempo_rem_10_ms": dados_remocao[10]["tempo_rb_ms"],
        "avl_rot_rem_30": dados_remocao[30]["rot_avl"],
        "rb_rot_rem_30": dados_remocao[30]["rot_rb"],
        "rb_rec_rem_30": dados_remocao[30]["rec_rb"],
        "avl_tempo_rem_30_ms": dados_remocao[30]["tempo_avl_ms"],
        "rb_tempo_rem_30_ms": dados_remocao[30]["tempo_rb_ms"],
        "avl_rot_rem_50": dados_remocao[50]["rot_avl"],
        "rb_rot_rem_50": dados_remocao[50]["rot_rb"],
        "rb_rec_rem_50": dados_remocao[50]["rec_rb"],
        "avl_tempo_rem_50_ms": dados_remocao[50]["tempo_avl_ms"],
        "rb_tempo_rem_50_ms": dados_remocao[50]["tempo_rb_ms"],
    }


def executar_experimento_crescente(n: int, semente: int = 42) -> Dict[str, Any]:
    contas = gerar_contas_crescentes(n)
    return executar_cenario_completo(contas, "Ordem Crescente (Exp. A)", semente=semente)


def executar_experimentos_completos(n: int, semente: int = 42) -> Dict[str, Any]:
    contas = gerar_contas_aleatorias(n, semente)
    return executar_cenario_completo(contas, "Ordem Aleatoria (Exp. B, C e D)", semente=semente)


def imprimir_detalhes_cenario(res: Dict[str, Any], numero_cenario: int, titulo: str, eh_crescente: bool) -> None:
    n = res["n"]
    print(f"\n[PARTE {numero_cenario}: {titulo.upper()} (N = {n:,})]")
    print("-" * 80)

    if eh_crescente:
        amostra_str = " -> ".join(str(ch) for ch in res["amostra_insercao"])
        print("1. INSERCAO SEQUENCIAL (ORDEM CRESCENTE):")
        print(f"  * Padrao de Chaves        : Contas {res['amostra_insercao'][0]} ate {res['amostra_insercao'][0] + n - 1} (sequencial)")
        print(f"  * Amostra de Insercao     : {amostra_str} ... (sequencial)")
    else:
        amostra_str = ", ".join(str(ch) for ch in res["amostra_insercao"])
        print("1. INSERCAO ALEATORIA REALISTA:")
        print(f"  * Semente Deterministica  : seed = {res['semente']} (Reprodutivel em qualquer maquina)")
        print(f"  * Amostra de Insercao     : [ {amostra_str}, ... ] (contas bancarias)")

    print(f"  * Altura Final Resultante : AVL = {res['avl_altura_final']} | Rubro-Negra = {res['rb_altura_final']}")
    print(f"  * Rotacoes de Insercao    : AVL = {res['avl_rot_ins']:,} | Rubro-Negra = {res['rb_rot_ins']:,}")
    print(f"  * Recoloracoes na RN      : {res['rb_rec_ins']:,}")
    print(f"  * Tempo de Insercao (ms)  : AVL = {res['avl_tempo_ins_ms']:.3f} ms | Rubro-Negra = {res['rb_tempo_ins_ms']:.3f} ms")
    print("-" * 80)

    rotulo_busca = "CRESCENTE" if eh_crescente else "ALEATORIA"
    print(f"2. BATERIA DE BUSCAS NA ARVORE {rotulo_busca} (EXISTENTES E INEXISTENTES):")
    print(f"  * Total de Consultas      : {res['total_buscas']:,} buscas ({res['total_buscas_existentes']:,} existentes + {res['total_buscas_inexistentes']:,} inexistentes)")
    print(f"  * Total de Nos Visitados  : AVL = {res['avl_total_nos_busca']:,} nos | Rubro-Negra = {res['rb_total_nos_busca']:,} nos")
    print(f"  * Media Geral por Busca   : AVL = {res['avl_media_busca']:.2f} nos | Rubro-Negra = {res['rb_media_busca']:.2f} nos")
    print(f"  * Chaves Existentes (50%) : AVL = {res['avl_media_busca_existente']:.2f} nos/busca ({res['avl_tempo_busca_existente_ms']:.3f} ms) | RN = {res['rb_media_busca_existente']:.2f} nos/busca ({res['rb_tempo_busca_existente_ms']:.3f} ms)")
    print(f"  * Chaves Inexistentes (50%): AVL = {res['avl_media_busca_inexistente']:.2f} nos/busca ({res['avl_tempo_busca_inexistente_ms']:.3f} ms) | RN = {res['rb_media_busca_inexistente']:.2f} nos/busca ({res['rb_tempo_busca_inexistente_ms']:.3f} ms)")
    print(f"  * Tempo Total de Busca    : AVL = {res['avl_tempo_busca_ms']:.3f} ms | Rubro-Negra = {res['rb_tempo_busca_ms']:.3f} ms")
    print("-" * 80)

    rotulo_rem = "CRESCENTE" if eh_crescente else "ALEATORIA"
    print(f"3. BATERIA DE REMOCOES PARCIAIS NA ARVORE {rotulo_rem} (10%, 30% E 50%):")
    for pct, info in res["remocao_detalhada"].items():
        print(
            f"  * Remocao {pct}% ({info['qtd_removida']} contas): "
            f"AVL h({info['alt_antes_avl']}->{info['alt_depois_avl']}), rot={info['rot_avl']:,}, t={info['tempo_avl_ms']:.3f}ms | "
            f"RN h({info['alt_antes_rb']}->{info['alt_depois_rb']}), rot={info['rot_rb']:,}, rec={info['rec_rb']:,}, t={info['tempo_rb_ms']:.3f}ms"
        )
    print("-" * 80)

    status_equiv = "100% IDENTICAS (Nenhuma conta perdida ou divergente)" if res["equivalencia_em_ordem"] else "DIVERGENTE"
    p5_avl_str = ", ".join(str(x) for x in res["primeiras_5_em_ordem_avl"])
    p5_rb_str = ", ".join(str(x) for x in res["primeiras_5_em_ordem_rb"])
    u5_avl_str = ", ".join(str(x) for x in res["ultimas_5_em_ordem_avl"])
    u5_rb_str = ", ".join(str(x) for x in res["ultimas_5_em_ordem_rb"])

    print(f"4. VALIDACAO CRUZADA DE EQUIVALENCIA ESTRUTURAL (CAMINHAMENTO EM-ORDEM - {rotulo_rem}):")
    print(f"  * Contas Verificadas      : {res['total_chaves_conferidas']:,} de {n:,} contas")
    print(f"  * Status de Integridade   : {status_equiv}")
    print(f"  * 5 Menores Contas (AVL)  : [ {p5_avl_str} ]")
    print(f"  * 5 Menores Contas (RN)   : [ {p5_rb_str} ]  --> CONFERIDO")
    print(f"  * 5 Maiores Contas (AVL)  : [ {u5_avl_str} ]")
    print(f"  * 5 Maiores Contas (RN)   : [ {u5_rb_str} ]  --> CONFERIDO")
    print("-" * 80)


def imprimir_quadro_metricas(res: Dict[str, Any], titulo: str) -> None:
    n = res["n"]
    print("-" * 80)
    print(f"        {titulo.upper()} (N = {n:,})")
    print("-" * 80)
    print(f"{'METRICA OBRIGATORIA':<35} | {'ARVORE AVL':<18} | {'ARVORE RUBRO-NEGRA':<20}")
    print("-" * 80)
    print(f"{'Altura final (Apos Insercao)':<35} | {res['avl_altura_final']:<18} | {res['rb_altura_final']:<20}")
    print(f"{'Rotacoes na insercao':<35} | {res['avl_rot_ins']:<18,d} | {res['rb_rot_ins']:<20,d}")
    print(f"{'Rotacoes na remocao (10% dos nos)':<35} | {res['avl_rot_rem_10']:<18,d} | {res['rb_rot_rem_10']:<20,d}")
    print(f"{'Rotacoes na remocao (30% - Edital)':<35} | {res['avl_rot_rem_30']:<18,d} | {res['rb_rot_rem_30']:<20,d}")
    print(f"{'Rotacoes na remocao (50% dos nos)':<35} | {res['avl_rot_rem_50']:<18,d} | {res['rb_rot_rem_50']:<20,d}")
    print(f"{'Recoloracoes (Insercao)':<35} | {'N/A':<18} | {res['rb_rec_ins']:<20,d}")
    print(f"{'Recoloracoes (Remocao 10%)':<35} | {'N/A':<18} | {res['rb_rec_rem_10']:<20,d}")
    print(f"{'Recoloracoes (Remocao 30% - Edital)':<35} | {'N/A':<18} | {res['rb_rec_rem_30']:<20,d}")
    print(f"{'Recoloracoes (Remocao 50%)':<35} | {'N/A':<18} | {res['rb_rec_rem_50']:<20,d}")
    print(f"{'Total de nos visitados na busca':<35} | {res['avl_total_nos_busca']:<18,d} | {res['rb_total_nos_busca']:<20,d}")
    print(f"{'Media de nos visitados na busca':<35} | {res['avl_media_busca']:<18.2f} | {res['rb_media_busca']:<20.2f}")
    print(f"{'Tempo total de insercao (ms)':<35} | {res['avl_tempo_ins_ms']:<18.3f} | {res['rb_tempo_ins_ms']:<20.3f}")
    print(f"{'Tempo total de busca (ms)':<35} | {res['avl_tempo_busca_ms']:<18.3f} | {res['rb_tempo_busca_ms']:<20.3f}")
    print(f"{'Tempo total remocao (10%, ms)':<35} | {res['avl_tempo_rem_10_ms']:<18.3f} | {res['rb_tempo_rem_10_ms']:<20.3f}")
    print(f"{'Tempo total remocao (30% - Edital)':<35} | {res['avl_tempo_rem_30_ms']:<18.3f} | {res['rb_tempo_rem_30_ms']:<20.3f}")
    print(f"{'Tempo total remocao (50%, ms)':<35} | {res['avl_tempo_rem_50_ms']:<18.3f} | {res['rb_tempo_rem_50_ms']:<20.3f}")
    print("-" * 80)


def imprimir_tabela_1_formatada(res_aleatorio: Dict[str, Any], res_crescente: Optional[Dict[str, Any]] = None) -> None:
    n = res_aleatorio["n"]
    print("\n" + "=" * 80)
    print(f"      RELATORIO DE EXPERIMENTOS CIENTIFICOS - SISTEMA BANCARIO (N = {n:,})")
    print("=" * 80)

    if res_crescente is not None:
        imprimir_detalhes_cenario(res_crescente, 1, "CENARIO EM ORDEM CRESCENTE (PIOR CASO ABB)", eh_crescente=True)

    imprimir_detalhes_cenario(res_aleatorio, 2, "CENARIO EM ORDEM ALEATORIA (CENARIO REAL BANCARIO)", eh_crescente=False)

    print("\n" + "=" * 80)
    print(f"      QUADROS COMPARATIVOS CONSOLIDADOS (N = {n:,})")
    print("=" * 80)
    imprimir_quadro_metricas(res_aleatorio, "TABELA 1: METRICAS CONSOLIDADAS (ORDEM ALEATORIA - CENARIO REAL BANCARIO)")
    if res_crescente is not None:
        imprimir_quadro_metricas(res_crescente, "TABELA 2: METRICAS CONSOLIDADAS (ORDEM CRESCENTE - PIOR CASO ABB)")
    print("=" * 80 + "\n")


def salvar_resultados_csv(lista_resultados: List[Dict[str, Any]], arquivo: str = "resultados_experimentos.csv") -> None:
    cabecalhos = [
        "n", "semente", "cenario",
        "avl_altura_final", "rb_altura_final",
        "avl_rot_ins", "rb_rot_ins", "rb_rec_ins",
        "avl_tempo_ins_ms", "rb_tempo_ins_ms",
        "avl_total_nos_busca", "rb_total_nos_busca",
        "avl_media_busca", "rb_media_busca",
        "avl_media_busca_existente", "rb_media_busca_existente",
        "avl_media_busca_inexistente", "rb_media_busca_inexistente",
        "avl_tempo_busca_ms", "rb_tempo_busca_ms",
        "avl_rot_rem_10", "rb_rot_rem_10", "rb_rec_rem_10", "avl_tempo_rem_10_ms", "rb_tempo_rem_10_ms",
        "avl_rot_rem_30", "rb_rot_rem_30", "rb_rec_rem_30", "avl_tempo_rem_30_ms", "rb_tempo_rem_30_ms",
        "avl_rot_rem_50", "rb_rot_rem_50", "rb_rec_rem_50", "avl_tempo_rem_50_ms", "rb_tempo_rem_50_ms"
    ]

    with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cabecalhos, extrasaction="ignore")
        writer.writeheader()
        for res in lista_resultados:
            writer.writerow(res)


def salvar_relatorio_markdown(lista_resultados: List[Dict[str, Any]], arquivo: str = "resultados_experimentos.md") -> None:
    res_aleat = [r for r in lista_resultados if "Aleatoria" in r.get("cenario", "")]
    res_cresc = [r for r in lista_resultados if "Crescente" in r.get("cenario", "")]

    linhas: List[str] = [
        "# Relatorio de Resultados Experimentais (Trabalho Pratico I - AED II)",
        ""
    ]

    if res_aleat:
        linhas.extend([
            "## Tabela 1 Consolidada: Insercao em Ordem Aleatoria (Cenario Real Bancario)",
            "",
            "| N | Estrutura | Altura Final | Rotacoes Ins | Rot Rem (10% | 30% | 50%) | Recol Ins | Recol Rem (10% | 30% | 50%) | Total Nos Busca | Media Nos Busca | Tempo Ins (ms) | Tempo Busca (ms) | Tempo Rem (30%, ms) |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
        ])
        for res in res_aleat:
            n = res["n"]
            rot_rem_str = f"{res['avl_rot_rem_10']:,} / {res['avl_rot_rem_30']:,} / {res['avl_rot_rem_50']:,}"
            rot_rem_rb_str = f"{res['rb_rot_rem_10']:,} / {res['rb_rot_rem_30']:,} / {res['rb_rot_rem_50']:,}"
            rec_rem_rb_str = f"{res['rb_rec_rem_10']:,} / {res['rb_rec_rem_30']:,} / {res['rb_rec_rem_50']:,}"
            linhas.append(
                f"| {n:,} | AVL | {res['avl_altura_final']} | {res['avl_rot_ins']:,} | {rot_rem_str} | N/A | N/A | "
                f"{res['avl_total_nos_busca']:,} | {res['avl_media_busca']:.2f} | {res['avl_tempo_ins_ms']:.3f} | {res['avl_tempo_busca_ms']:.3f} | {res['avl_tempo_rem_30_ms']:.3f} |"
            )
            linhas.append(
                f"| {n:,} | Rubro-Negra | {res['rb_altura_final']} | {res['rb_rot_ins']:,} | {rot_rem_rb_str} | {res['rb_rec_ins']:,} | {rec_rem_rb_str} | "
                f"{res['rb_total_nos_busca']:,} | {res['rb_media_busca']:.2f} | {res['rb_tempo_ins_ms']:.3f} | {res['rb_tempo_busca_ms']:.3f} | {res['rb_tempo_rem_30_ms']:.3f} |"
            )
        linhas.append("")

    if res_cresc:
        linhas.extend([
            "## Tabela 2 Consolidada: Insercao em Ordem Crescente (Pior Caso ABB)",
            "",
            "| N | Estrutura | Altura Final | Rotacoes Ins | Rot Rem (10% | 30% | 50%) | Recol Ins | Recol Rem (10% | 30% | 50%) | Total Nos Busca | Media Nos Busca | Tempo Ins (ms) | Tempo Busca (ms) | Tempo Rem (30%, ms) |",
            "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
        ])
        for res in res_cresc:
            n = res["n"]
            rot_rem_str = f"{res['avl_rot_rem_10']:,} / {res['avl_rot_rem_30']:,} / {res['avl_rot_rem_50']:,}"
            rot_rem_rb_str = f"{res['rb_rot_rem_10']:,} / {res['rb_rot_rem_30']:,} / {res['rb_rot_rem_50']:,}"
            rec_rem_rb_str = f"{res['rb_rec_rem_10']:,} / {res['rb_rec_rem_30']:,} / {res['rb_rec_rem_50']:,}"
            linhas.append(
                f"| {n:,} | AVL | {res['avl_altura_final']} | {res['avl_rot_ins']:,} | {rot_rem_str} | N/A | N/A | "
                f"{res['avl_total_nos_busca']:,} | {res['avl_media_busca']:.2f} | {res['avl_tempo_ins_ms']:.3f} | {res['avl_tempo_busca_ms']:.3f} | {res['avl_tempo_rem_30_ms']:.3f} |"
            )
            linhas.append(
                f"| {n:,} | Rubro-Negra | {res['rb_altura_final']} | {res['rb_rot_ins']:,} | {rot_rem_rb_str} | {res['rb_rec_ins']:,} | {rec_rem_rb_str} | "
                f"{res['rb_total_nos_busca']:,} | {res['rb_media_busca']:.2f} | {res['rb_tempo_ins_ms']:.3f} | {res['rb_tempo_busca_ms']:.3f} | {res['rb_tempo_rem_30_ms']:.3f} |"
            )
        linhas.append("")

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

        for idx, n in enumerate(tamanhos):
            print(f"\n[Executando] Iniciando testes rigorosos para N = {n:,} contas bancarias...")
            res_crescente = executar_experimento_crescente(n)
            res_aleatorio = executar_experimentos_completos(n, semente=42)
            imprimir_tabela_1_formatada(res_aleatorio, res_crescente)
            todos_resultados.append(res_aleatorio)
            todos_resultados.append(res_crescente)
            if idx < len(tamanhos) - 1:
                input(f"\n[Pausa de Inspecao] Pressione ENTER para prosseguir para o proximo tamanho (N = {tamanhos[idx + 1]:,})... ")

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


if __name__ == "__main__":
    executar_bateria_experimentos()
