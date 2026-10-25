from __future__ import annotations
import sys
from typing import Optional, List, Any
from modelos import ContaBancaria
from avl import ArvoreAVL


def _obter_classe_rubro_negra() -> Optional[Any]:
    try:
        import importlib
        return getattr(importlib.import_module("rubro_negra"), "ArvoreRubroNegra", None)
    except Exception:
        return None


class SistemaBancarioCLI:
    def __init__(self) -> None:
        self.arvore_avl: ArvoreAVL = ArvoreAVL()
        cls_rb = _obter_classe_rubro_negra()
        self.arvore_rb: Optional[Any] = cls_rb() if cls_rb is not None else None
        self.tipo_estrutura: str = "AVL"
        self.modo_detalhado: bool = False

    @property
    def arvore_ativa(self) -> Any:
        if self.tipo_estrutura == "AVL":
            return self.arvore_avl
        return self.arvore_rb

    def cabecalho(self) -> None:
        print("\n" + "=" * 70)
        print("         SISTEMA BANCARIO - ARVORES BALANCEADAS (AED II)")
        print("=" * 70)
        status_modo = "ATIVADO" if self.modo_detalhado else "DESATIVADO"
        alt_rb = self.arvore_rb.altura if self.arvore_rb is not None else 0
        print(f"Estrutura Inspecionada: [ {self.tipo_estrutura} ]   |   Modo Detalhado: [ {status_modo} ]")
        print(f"Colecao Sincronizada  : {self.arvore_ativa.tamanho} contas   |   AVL: h={self.arvore_avl.altura} | RN: h={alt_rb}")
        print("-" * 70)

    def pausar(self) -> None:
        input("\nPressione ENTER para continuar...")

    def ler_numero_conta(self, prompt: str) -> Optional[int]:
        while True:
            entrada = input(prompt).strip()
            if not entrada:
                return None
            if not entrada.isdigit():
                print("[Erro] O numero da conta deve conter apenas digitos numericos positivos.")
                continue
            numero = int(entrada)
            if numero <= 0:
                print("[Erro] O numero da conta deve ser maior que zero.")
                continue
            return numero

    def ler_saldo(self, prompt: str) -> float:
        while True:
            entrada = input(prompt).strip().replace(",", ".")
            if not entrada:
                return 0.0
            try:
                valor = float(entrada)
                if valor < 0:
                    print("[Erro] O saldo inicial nao pode ser negativo.")
                    continue
                return valor
            except ValueError:
                print("[Erro] Formato monetario invalido. Digite um numero como 1500.50 ou 1500,50.")

    def ler_tipo_conta(self) -> str:
        while True:
            print("\nTipos disponiveis: [1] Corrente | [2] Poupanca | [3] Salario")
            escolha = input("Selecione o tipo (1/2/3) [padrao 1]: ").strip()
            if not escolha or escolha == "1":
                return "Corrente"
            elif escolha == "2":
                return "Poupanca"
            elif escolha == "3":
                return "Salario"
            else:
                print("[Erro] Opcao invalida! Digite apenas 1 para Corrente, 2 para Poupanca ou 3 para Salario.")

    def opcao_1_selecionar_estrutura(self) -> None:
        self.cabecalho()
        print(">>> 1. ALTERNAR ESTRUTURA PARA INSPECAO (AVL <-> RUBRO-NEGRA)")
        if self.tipo_estrutura == "AVL":
            cls_rb = _obter_classe_rubro_negra()
            if cls_rb is None:
                print("\n[Aviso] A Arvore Rubro-Negra nao foi encontrada.")
                self.pausar()
                return
            if self.arvore_rb is None:
                self.arvore_rb = cls_rb(modo_detalhado=self.modo_detalhado)
            self.tipo_estrutura = "RUBRO-NEGRA"
        else:
            self.tipo_estrutura = "AVL"

        print(f"\n[Sucesso] Estrutura inspecionada alterada para: [ {self.tipo_estrutura} ]")
        print(f"A mesma colecao de {self.arvore_ativa.tamanho} contas esta sincronizada e disponivel para analise.")
        self.pausar()

    def opcao_2_cadastrar_conta(self) -> None:
        self.cabecalho()
        print(">>> 2. CADASTRAR CONTA BANCARIA (INSERIR)")
        print("(Dica: Deixe o numero da conta em branco para cancelar a operacao)\n")

        numero = self.ler_numero_conta("Numero da conta (inteiro positivo): ")
        if numero is None:
            print("\nOperacao cancelada pelo usuario.")
            self.pausar()
            return

        if self.arvore_avl.buscar(numero) is not None:
            print(f"\n[AVISO] A conta com numero {numero} ja existe no sistema!")
            print("Conforme a politica do projeto, chaves duplicadas sao rejeitadas. Cadastro cancelado.")
            self.pausar()
            return

        titular = input("Nome do titular: ").strip()
        if not titular:
            titular = f"Titular {numero}"

        agencia = input("Agencia bancaria (padrao 0001): ").strip()
        if not agencia:
            agencia = "0001"

        tipo = self.ler_tipo_conta()

        saldo = self.ler_saldo("Saldo inicial (R$): ")

        nova_conta = ContaBancaria(numero, titular, agencia, tipo, saldo)
        logs_antes = len(self.arvore_ativa.estatisticas.logs_detalhados)

        sucesso_avl = self.arvore_avl.inserir(nova_conta)
        sucesso_rb = self.arvore_rb.inserir(nova_conta) if self.arvore_rb is not None else True
        sucesso = sucesso_avl and sucesso_rb

        if sucesso:
            print(f"\n[SUCESSO] Conta {numero} ({titular}) inserida simultaneamente na AVL e na Rubro-Negra!")
            if self.modo_detalhado:
                print("\n" + "=" * 70)
                print(f"     PASSO A PASSO NA ESTRUTURA ATIVA: [ {self.tipo_estrutura} ] (MODO DETALHADO)")
                print("=" * 70)
                logs_novos = self.arvore_ativa.estatisticas.logs_detalhados[logs_antes:]
                if not logs_novos:
                    print("  -> Operacao concluida sem necessidade de rebalanceamento (arvore equilibrada).")
                else:
                    for log in logs_novos:
                        print(log + "\n")
                print(f"--- Estrutura Resultante [ {self.tipo_estrutura} ] Apos a Operacao ---")
                self.arvore_ativa.exibir_arvore()
        else:
            print(f"\n[AVISO] A conta com numero {numero} ja existe no sistema.")
            print("Conforme a politica do projeto, chaves duplicadas sao rejeitadas para preservar a integridade da arvore.")

        self.pausar()

    def opcao_3_buscar_conta(self) -> None:
        self.cabecalho()
        print(">>> 3. BUSCAR CONTA POR NUMERO")
        numero = self.ler_numero_conta("Digite o numero da conta a consultar: ")
        if numero is None:
            print("\nOperacao cancelada.")
            self.pausar()
            return

        nos_antes_avl = self.arvore_avl.estatisticas.nos_visitados
        conta_avl = self.arvore_avl.buscar(numero)
        custo_avl = self.arvore_avl.estatisticas.nos_visitados - nos_antes_avl

        if self.arvore_rb is not None:
            nos_antes_rb = self.arvore_rb.estatisticas.nos_visitados
            conta_rb = self.arvore_rb.buscar(numero)
            custo_rb = self.arvore_rb.estatisticas.nos_visitados - nos_antes_rb
        else:
            conta_rb = None
            custo_rb = 0

        conta = conta_avl or conta_rb

        if conta is not None:
            print("\n" + "-" * 50)
            print("DADOS DA CONTA ENCONTRADA:")
            print(f" Numero da Conta : {conta.numero_conta}")
            print(f" Titular         : {conta.titular}")
            print(f" Agencia         : {conta.agencia}")
            print(f" Tipo de Conta   : {conta.tipo}")
            print(f" Saldo Atual     : R$ {conta.saldo:,.2f}")
            print("-" * 50)
            print("Custo Comparativo da Busca (Nos Visitados):")
            print(f"  * Arvore AVL         : {custo_avl} nos visitados")
            print(f"  * Arvore Rubro-Negra : {custo_rb} nos visitados")
        else:
            print(f"\n[NAO ENCONTRADA] Nenhuma conta com numero {numero} existe no sistema.")
            print("Custo Comparativo ate Confirmar Inexistencia:")
            print(f"  * Arvore AVL         : {custo_avl} nos visitados")
            print(f"  * Arvore Rubro-Negra : {custo_rb} nos visitados")

        self.pausar()

    def opcao_4_remover_conta(self) -> None:
        self.cabecalho()
        print(">>> 4. REMOVER CONTA POR NUMERO")
        numero = self.ler_numero_conta("Digite o numero da conta a remover: ")
        if numero is None:
            print("\nOperacao cancelada.")
            self.pausar()
            return

        if self.arvore_ativa.buscar(numero) is None:
            print(f"\n[ERRO] A conta {numero} nao foi encontrada para remocao.")
            self.pausar()
            return

        logs_antes = len(self.arvore_ativa.estatisticas.logs_detalhados)
        removida_avl = self.arvore_avl.remover(numero)
        removida_rb = self.arvore_rb.remover(numero) if self.arvore_rb is not None else None
        removida = removida_avl or removida_rb

        if removida is not None:
            print(f"\n[SUCESSO] Conta {numero} ({removida.titular}) removida simultaneamente da AVL e da Rubro-Negra!")
            if self.modo_detalhado:
                print("\n" + "=" * 70)
                print(f"     PASSO A PASSO NA ESTRUTURA ATIVA: [ {self.tipo_estrutura} ] (MODO DETALHADO)")
                print("=" * 70)
                logs_novos = self.arvore_ativa.estatisticas.logs_detalhados[logs_antes:]
                if not logs_novos:
                    print("  -> Remocao concluida sem necessidade de rebalanceamento adicional.")
                else:
                    for log in logs_novos:
                        print(log + "\n")
                print(f"--- Estrutura Resultante [ {self.tipo_estrutura} ] Apos a Remocao ---")
                self.arvore_ativa.exibir_arvore()
        else:
            print(f"\n[ERRO] A conta {numero} nao foi encontrada para remocao.")

        self.pausar()

    def opcao_5_listar_contas(self) -> None:
        self.cabecalho()
        print(">>> 5. LISTAR CAMINHAMENTOS, MIN E MAX\n")
        contas: List[ContaBancaria] = self.arvore_ativa.caminhamento_em_ordem()

        if not contas:
            print("Nenhuma conta cadastrada na arvore ativa.")
        else:
            menor = self.arvore_ativa.obter_menor()
            maior = self.arvore_ativa.obter_maior()
            if menor and maior:
                print("=" * 75)
                print("           REGISTROS EXTREMOS DA ESTRUTURA (MINIMO E MAXIMO)")
                print("=" * 75)
                print(f"• MENOR CHAVE (MINIMO) : Conta {menor.numero_conta} | Titular: {menor.titular} | Agencia: {menor.agencia} | Saldo: R$ {menor.saldo:,.2f}")
                print(f"• MAIOR CHAVE (MAXIMO) : Conta {maior.numero_conta} | Titular: {maior.titular} | Agencia: {maior.agencia} | Saldo: R$ {maior.saldo:,.2f}")
                print("=" * 75 + "\n")

            print("[CAMINHAMENTO EM-ORDEM (ORDENADO PELO NUMERO DA CONTA)]")
            print(f"{'CONTA':<10} | {'TITULAR':<25} | {'AGENCIA':<8} | {'TIPO':<12} | {'SALDO':<15}")
            print("-" * 75)
            for c in contas:
                print(f"{c.numero_conta:<10} | {c.titular:<25} | {c.agencia:<8} | {c.tipo:<12} | R$ {c.saldo:>12,.2f}")
            print("-" * 75)
            print(f"Total de contas listadas: {len(contas)}")

            pre = self.arvore_ativa.caminhamento_pre_ordem()
            pos = self.arvore_ativa.caminhamento_pos_ordem()
            print("\n• Caminhamento Pre-Ordem : " + " -> ".join(str(c.numero_conta) for c in pre))
            print("• Caminhamento Pos-Ordem : " + " -> ".join(str(c.numero_conta) for c in pos))

        self.pausar()

    def opcao_6_exibir_arvore(self) -> None:
        self.cabecalho()
        print(">>> 6. EXIBIR ALTURA, QUANTIDADE DE NOS E ESTRUTURA NO TERMINAL\n")
        print(f"Estrutura Inspecionada : {self.tipo_estrutura}")
        print(f"Quantidade de Nos      : {self.arvore_ativa.tamanho}")
        print(f"Altura da Arvore       : {self.arvore_ativa.altura}\n")

        if self.modo_detalhado:
            logs = self.arvore_ativa.estatisticas.logs_detalhados
            print("=" * 70)
            print(f"   PASSO A PASSO DAS CORRECOES REGISTRADAS NA [ {self.tipo_estrutura} ]")
            print("=" * 70)
            if not logs:
                print("  -> Nao ocorreram desbalanceamentos ate o momento nesta estrutura.")
                print("     Todos os nos foram acomodados mantendo as propriedades de equilibrio.\n")
            else:
                limite = 5
                amostra = logs[-limite:] if len(logs) > limite else logs
                if len(logs) > limite:
                    print(f"(Mostrando os ultimos {limite} de {len(logs)} eventos de rebalanceamento registrados)\n")
                for log in amostra:
                    print(log + "\n" + "-" * 70)
                print()

        print(f"--- Estrutura Resultante [ {self.tipo_estrutura} ] no Terminal ---")
        self.arvore_ativa.exibir_arvore()
        self.pausar()

    def opcao_7_estatisticas(self) -> None:
        self.cabecalho()
        print(">>> 7. COMPARATIVO CONSOLIDADO DE ESTATISTICAS E REBALANCEAMENTO\n")
        est_avl = self.arvore_avl.estatisticas
        est_rb = self.arvore_rb.estatisticas if self.arvore_rb is not None else None

        rot_ll_rb = est_rb.rotacoes_simples_direita if est_rb else 0
        rot_rr_rb = est_rb.rotacoes_simples_esquerda if est_rb else 0
        rot_lr_rb = est_rb.rotacoes_duplas_esq_dir if est_rb else 0
        rot_rl_rb = est_rb.rotacoes_duplas_dir_esq if est_rb else 0
        tot_rot_rb = est_rb.total_rotacoes if est_rb else 0
        rec_rb = est_rb.recoloracoes if est_rb else 0
        vis_rb = est_rb.nos_visitados if est_rb else 0
        alt_rb = self.arvore_rb.altura if self.arvore_rb is not None else 0
        tam_rb = self.arvore_rb.tamanho if self.arvore_rb is not None else 0

        print("=" * 74)
        print("        QUADRO COMPARATIVO CONSOLIDADO (AVL vs. RUBRO-NEGRA)")
        print("=" * 74)
        print(f"{'METRICA / OPERACAO':<36} | {'ARVORE AVL':<16} | {'ARVORE RUBRO-NEGRA':<18}")
        print("-" * 74)
        print(f"{'Quantidade de Contas (Nos)':<36} | {self.arvore_avl.tamanho:<16} | {tam_rb:<18}")
        print(f"{'Altura Atual da Arvore (h)':<36} | {self.arvore_avl.altura:<16} | {alt_rb:<18}")
        print("-" * 74)
        print(f"{'Rotacoes Simples a Direita (LL)':<36} | {est_avl.rotacoes_simples_direita:<16} | {rot_ll_rb:<18}")
        print(f"{'Rotacoes Simples a Esquerda (RR)':<36} | {est_avl.rotacoes_simples_esquerda:<16} | {rot_rr_rb:<18}")
        print(f"{'Rotacoes Duplas Esquerda-Direita':<36} | {est_avl.rotacoes_duplas_esq_dir:<16} | {rot_lr_rb:<18}")
        print(f"{'Rotacoes Duplas Direita-Esquerda':<36} | {est_avl.rotacoes_duplas_dir_esq:<16} | {rot_rl_rb:<18}")
        print("-" * 74)
        print(f"{'TOTAL ACUMULADO DE ROTACOES':<36} | {est_avl.total_rotacoes:<16} | {tot_rot_rb:<18}")
        print(f"{'TOTAL DE RECOLORACOES':<36} | {'N/A':<16} | {rec_rb:<18}")
        print(f"{'TOTAL DE NOS VISITADOS EM CONSULTAS':<36} | {est_avl.nos_visitados:<16} | {vis_rb:<18}")
        print("=" * 74)
        tot_rot_combinado = est_avl.total_rotacoes + tot_rot_rb
        print(f"Total Combinado de Rotacoes no Sistema : {tot_rot_combinado}")
        print(f"Total de Recoloracoes na Rubro-Negra    : {rec_rb}")
        print(f"Total de Leituras de Nos em Consultas   : {est_avl.nos_visitados + vis_rb}")
        print("=" * 74)

        logs_avl = est_avl.logs_detalhados
        logs_rb = est_rb.logs_detalhados if est_rb else []
        if logs_avl or logs_rb:
            print("\nDeseja visualizar o historico detalhado de eventos registrados?")
            print(f"  [1] Ver historico da AVL ({len(logs_avl)} eventos)")
            print(f"  [2] Ver historico da Rubro-Negra ({len(logs_rb)} eventos)")
            print(f"  [3] Ver ambos os historicos")
            print("  [0] Nao exibir historico (Retornar ao menu)")
            escolha = input("Selecione uma opcao (0/1/2/3) [padrao 0]: ").strip()
            if escolha == "1":
                print("\n" + "=" * 70)
                print("           HISTORICO DE EVENTOS DETALHADOS - ARVORE AVL")
                print("=" * 70)
                if not logs_avl:
                    print("Nenhum evento de rebalanceamento registrado na AVL.")
                for log in logs_avl:
                    print(log + "\n" + "-" * 70)
            elif escolha == "2":
                print("\n" + "=" * 70)
                print("       HISTORICO DE EVENTOS DETALHADOS - ARVORE RUBRO-NEGRA")
                print("=" * 70)
                if not logs_rb:
                    print("Nenhum evento de rebalanceamento registrado na Rubro-Negra.")
                for log in logs_rb:
                    print(log + "\n" + "-" * 70)
            elif escolha == "3":
                print("\n" + "=" * 70)
                print("           HISTORICO DE EVENTOS DETALHADOS - ARVORE AVL")
                print("=" * 70)
                if not logs_avl:
                    print("Nenhum evento de rebalanceamento registrado na AVL.")
                for log in logs_avl:
                    print(log + "\n" + "-" * 70)
                print("\n" + "=" * 70)
                print("       HISTORICO DE EVENTOS DETALHADOS - ARVORE RUBRO-NEGRA")
                print("=" * 70)
                if not logs_rb:
                    print("Nenhum evento de rebalanceamento registrado na Rubro-Negra.")
                for log in logs_rb:
                    print(log + "\n" + "-" * 70)
        self.pausar()

    def opcao_8_validar_propriedades(self) -> None:
        self.cabecalho()
        print(">>> 8. VALIDAR AS PROPRIEDADES DAS DUAS ARVORES SIMULTANEAMENTE\n")
        valido_avl, msg_avl = self.arvore_avl.validar_propriedades()
        status_avl = "[APROVADO]" if valido_avl else "[REPROVADO]"
        print(f"1. ARVORE AVL: {status_avl}")
        print(f"   Laudo: {msg_avl}\n")

        if self.arvore_rb is not None:
            valido_rb, msg_rb = self.arvore_rb.validar_propriedades()
            status_rb = "[APROVADO]" if valido_rb else "[REPROVADO]"
            print(f"2. ARVORE RUBRO-NEGRA: {status_rb}")
            print(f"   Laudo: {msg_rb}\n")
        else:
            print("2. ARVORE RUBRO-NEGRA: [Indisponivel]")

        if valido_avl and (self.arvore_rb is None or valido_rb):
            print("=" * 70)
            print("[CONCLUSAO: INTEGRALMENTE CONFORME]")
            print("Ambas as estruturas atendem a todas as invariantes e propriedades do Edital.")
            print("=" * 70)
        else:
            print("=" * 70)
            print("[CONCLUSAO: ALERTA DE INCONSISTENCIA DETECTADA]")
            print("Pelo menos uma das arvores apresentou divergencia com suas propriedades formais.")
            print("=" * 70)

        self.pausar()

    def opcao_9_executar_experimentos(self) -> None:
        self.cabecalho()
        print(">>> 9. EXECUTAR OS EXPERIMENTOS AUTOMATICOS (SECAO 5)\n")
        try:
            import importlib
            mod_exp = importlib.import_module("experimentos")
            if hasattr(mod_exp, "executar_bateria_experimentos"):
                print("Iniciando bateria de experimentos comparativos...\n")
                mod_exp.executar_bateria_experimentos()
            else:
                print("O modulo experimentos.py foi encontrado, mas a rotina principal esta sendo desenvolvida.")
        except ModuleNotFoundError:
            print("[Em Desenvolvimento]")
            print("A bateria de testes automatizados (Experimentos A, B, C e D com n=100, 1.000 e 10.000)")
            print("sera implementada no arquivo 'experimentos.py' assim que concluirmos a Árvore Rubro-Negra.")

        self.pausar()

    def opcao_d_alternar_modo_detalhado(self) -> None:
        self.modo_detalhado = not self.modo_detalhado
        self.arvore_avl.modo_detalhado = self.modo_detalhado
        if self.arvore_rb is not None:
            self.arvore_rb.modo_detalhado = self.modo_detalhado
        status = "ATIVADO" if self.modo_detalhado else "DESATIVADO"
        print(f"\n[Modo Detalhado] Estado alterado para: [ {status} ]")
        self.pausar()

    def executar(self) -> None:
        while True:
            self.cabecalho()
            print("1. Selecionar Estrutura (AVL <-> Rubro-Negra)")
            print("2. Cadastrar Registro de Conta (Inserir)")
            print("3. Buscar Conta por Numero")
            print("4. Remover Conta por Numero")
            print("5. Listar Caminhamentos, Min e Max")
            print("6. Exibir Altura, Total de Nos e Estrutura no Terminal")
            print("7. Exibir Estatisticas de Rebalanceamento")
            print("8. Validar as Propriedades da Arvore")
            print("9. Executar os Experimentos Automaticos")
            print("-" * 70)
            print("D. Alternar Modo Detalhado (Explicativo Passo a Passo) [ON/OFF]")
            print("0. Sair do Sistema")
            print("=" * 70)

            entrada = input("Digite a opcao desejada: ").strip()

            if entrada == "0":
                print("\nEncerrando o Sistema Bancario. Ate logo!")
                sys.exit(0)
            elif entrada == "1":
                self.opcao_1_selecionar_estrutura()
            elif entrada == "2":
                self.opcao_2_cadastrar_conta()
            elif entrada == "3":
                self.opcao_3_buscar_conta()
            elif entrada == "4":
                self.opcao_4_remover_conta()
            elif entrada == "5":
                self.opcao_5_listar_contas()
            elif entrada == "6":
                self.opcao_6_exibir_arvore()
            elif entrada == "7":
                self.opcao_7_estatisticas()
            elif entrada == "8":
                self.opcao_8_validar_propriedades()
            elif entrada == "9":
                self.opcao_9_executar_experimentos()
            elif entrada.upper() == "D":
                self.opcao_d_alternar_modo_detalhado()
            else:
                print(f"\n[Erro] Opcao '{entrada}' invalida!")
                print("Por favor, digite apenas um numero de 0 a 9 ou a letra 'D'.")
                self.pausar()


if __name__ == "__main__":
    app = SistemaBancarioCLI()
    app.executar()
