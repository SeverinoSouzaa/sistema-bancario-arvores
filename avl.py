from __future__ import annotations
from typing import Optional, List, Tuple
from modelos import ContaBancaria, NoAVL, EstatisticasOperacao


class ArvoreAVL:
    def __init__(self, modo_detalhado: bool = False) -> None:
        self.raiz: Optional[NoAVL] = None
        self.quantidade_nos: int = 0
        self.modo_detalhado: bool = modo_detalhado
        self.estatisticas: EstatisticasOperacao = EstatisticasOperacao()

    @property
    def tamanho(self) -> int:
        return self.quantidade_nos

    @property
    def altura(self) -> int:
        return NoAVL.get_altura(self.raiz)

    @property
    def esta_vazia(self) -> bool:
        return self.raiz is None

    @staticmethod
    def renderizar_subarvore(raiz_local: Optional[NoAVL], marcador_raiz: str = "[RAIZ]") -> str:
        linhas: List[str] = []

        def _imprimir(no: Optional[NoAVL], prefixo: str = "", eh_esq: Optional[bool] = None) -> None:
            if no is None:
                return

            if no.direita is not None:
                _imprimir(no.direita, prefixo + ("|       " if eh_esq is True else "        "), False)

            if eh_esq is None:
                marcador = f"{marcador_raiz} "
            elif eh_esq is False:
                marcador = "/---[D] "
            else:
                marcador = "\\---[E] "

            fb_sinal = f"+{no.fator_balanceamento}" if no.fator_balanceamento > 0 else str(no.fator_balanceamento)
            linhas.append(f"{prefixo}{marcador}({no.chave}) [h={no.altura}, FB={fb_sinal}] {no.conta.titular}")

            if no.esquerda is not None:
                _imprimir(no.esquerda, prefixo + ("|       " if eh_esq is False else "        "), True)

        _imprimir(raiz_local)
        return "\n".join(linhas)

    def _rotacao_simples_direita(self, k2: NoAVL) -> NoAVL:
        antes_txt = self.renderizar_subarvore(k2, "[RAIZ]") if self.modo_detalhado else ""
        k1 = k2.esquerda
        fb_filho = k1.fator_balanceamento
        k2.esquerda = k1.direita
        k1.direita = k2
        k2.atualizar_altura()
        k1.atualizar_altura()
        self.estatisticas.rotacoes_simples_direita += 1
        if self.modo_detalhado:
            depois_txt = self.renderizar_subarvore(k1, "[RAIZ]")
            linhas_antes = "\n".join("    " + linha for linha in antes_txt.splitlines())
            linhas_depois = "\n".join("    " + linha for linha in depois_txt.splitlines())
            fb_filho_sinal = f"+{fb_filho}" if fb_filho > 0 else str(fb_filho)
            msg = (
                f"[REBALANCEAMENTO AVL - CASO LL]\n"
                f"  * Desbalanceamento detectado no No ({k2.chave}) com FB=+2\n"
                f"  * Filho Esquerdo ({k1.chave}) com FB={fb_filho_sinal} (>= 0)\n"
                f"  * Tipo de Rotacao: Rotacao Simples a Direita (SD) no No ({k2.chave})\n"
                f"  * Nova raiz local promovida: No ({k1.chave})\n\n"
                f"  >>> Subarvore ANTES da Rotacao (Desbalanceada):\n"
                f"{linhas_antes}\n\n"
                f"  >>> Subarvore DEPOIS da Rotacao (Balanceada):\n"
                f"{linhas_depois}"
            )
            self.estatisticas.registrar_log(msg)
        return k1

    def _rotacao_simples_esquerda(self, k1: NoAVL) -> NoAVL:
        antes_txt = self.renderizar_subarvore(k1, "[RAIZ]") if self.modo_detalhado else ""
        k2 = k1.direita
        fb_filho = k2.fator_balanceamento
        k1.direita = k2.esquerda
        k2.esquerda = k1
        k1.atualizar_altura()
        k2.atualizar_altura()
        self.estatisticas.rotacoes_simples_esquerda += 1
        if self.modo_detalhado:
            depois_txt = self.renderizar_subarvore(k2, "[RAIZ]")
            linhas_antes = "\n".join("    " + linha for linha in antes_txt.splitlines())
            linhas_depois = "\n".join("    " + linha for linha in depois_txt.splitlines())
            fb_filho_sinal = f"+{fb_filho}" if fb_filho > 0 else str(fb_filho)
            msg = (
                f"[REBALANCEAMENTO AVL - CASO RR]\n"
                f"  * Desbalanceamento detectado no No ({k1.chave}) com FB=-2\n"
                f"  * Filho Direito ({k2.chave}) com FB={fb_filho_sinal} (<= 0)\n"
                f"  * Tipo de Rotacao: Rotacao Simples a Esquerda (SE) no No ({k1.chave})\n"
                f"  * Nova raiz local promovida: No ({k2.chave})\n\n"
                f"  >>> Subarvore ANTES da Rotacao (Desbalanceada):\n"
                f"{linhas_antes}\n\n"
                f"  >>> Subarvore DEPOIS da Rotacao (Balanceada):\n"
                f"{linhas_depois}"
            )
            self.estatisticas.registrar_log(msg)
        return k2

    def _rotacao_dupla_esquerda_direita(self, k3: NoAVL) -> NoAVL:
        antes_txt = self.renderizar_subarvore(k3, "[RAIZ]") if self.modo_detalhado else ""
        k1 = k3.esquerda
        fb_filho = k1.fator_balanceamento
        k2 = k1.direita
        k1.direita = k2.esquerda
        k2.esquerda = k1
        k1.atualizar_altura()
        k2.atualizar_altura()
        k3.esquerda = k2
        k3.atualizar_altura()
        passo1_txt = self.renderizar_subarvore(k3, "[RAIZ]") if self.modo_detalhado else ""

        y = k3.esquerda
        k3.esquerda = y.direita
        y.direita = k3
        k3.atualizar_altura()
        y.atualizar_altura()
        self.estatisticas.rotacoes_duplas_esq_dir += 1
        if self.modo_detalhado:
            depois_txt = self.renderizar_subarvore(y, "[RAIZ]")
            linhas_antes = "\n".join("    " + linha for linha in antes_txt.splitlines())
            linhas_p1 = "\n".join("    " + linha for linha in passo1_txt.splitlines())
            linhas_depois = "\n".join("    " + linha for linha in depois_txt.splitlines())
            fb_filho_sinal = f"+{fb_filho}" if fb_filho > 0 else str(fb_filho)
            msg = (
                f"[REBALANCEAMENTO AVL - CASO LR (ROTACAO DUPLA ESQUERDA-DIREITA)]\n"
                f"  * Desbalanceamento detectado no No ({k3.chave}) com FB=+2\n"
                f"  * Filho Esquerdo ({k1.chave}) com FB={fb_filho_sinal} (< 0)\n"
                f"  * Passo 1: Rotacao Simples a Esquerda no filho ({k1.chave}) -> Alinha em Caso LL\n"
                f"  * Passo 2: Rotacao Simples a Direita no No ({k3.chave}) -> Promove No ({y.chave})\n\n"
                f"  >>> Subarvore ANTES da Correcao (Desbalanceada em LR):\n"
                f"{linhas_antes}\n\n"
                f"  >>> Subarvore APOS PASSO 1 (Alinhamento em LL):\n"
                f"{linhas_p1}\n\n"
                f"  >>> Subarvore DEPOIS DO PASSO 2 (Balanceamento Concluido):\n"
                f"{linhas_depois}"
            )
            self.estatisticas.registrar_log(msg)
        return y

    def _rotacao_dupla_direita_esquerda(self, k1: NoAVL) -> NoAVL:
        antes_txt = self.renderizar_subarvore(k1, "[RAIZ]") if self.modo_detalhado else ""
        k3 = k1.direita
        fb_filho = k3.fator_balanceamento
        k2 = k3.esquerda
        k3.esquerda = k2.direita
        k2.direita = k3
        k3.atualizar_altura()
        k2.atualizar_altura()
        k1.direita = k2
        k1.atualizar_altura()
        passo1_txt = self.renderizar_subarvore(k1, "[RAIZ]") if self.modo_detalhado else ""

        y = k1.direita
        k1.direita = y.esquerda
        y.esquerda = k1
        k1.atualizar_altura()
        y.atualizar_altura()
        self.estatisticas.rotacoes_duplas_dir_esq += 1
        if self.modo_detalhado:
            depois_txt = self.renderizar_subarvore(y, "[RAIZ]")
            linhas_antes = "\n".join("    " + linha for linha in antes_txt.splitlines())
            linhas_p1 = "\n".join("    " + linha for linha in passo1_txt.splitlines())
            linhas_depois = "\n".join("    " + linha for linha in depois_txt.splitlines())
            fb_filho_sinal = f"+{fb_filho}" if fb_filho > 0 else str(fb_filho)
            msg = (
                f"[REBALANCEAMENTO AVL - CASO RL (ROTACAO DUPLA DIREITA-ESQUERDA)]\n"
                f"  * Desbalanceamento detectado no No ({k1.chave}) com FB=-2\n"
                f"  * Filho Direito ({k3.chave}) com FB={fb_filho_sinal} (> 0)\n"
                f"  * Passo 1: Rotacao Simples a Direita no filho ({k3.chave}) -> Alinha em Caso RR\n"
                f"  * Passo 2: Rotacao Simples a Esquerda no No ({k1.chave}) -> Promove No ({y.chave})\n\n"
                f"  >>> Subarvore ANTES da Correcao (Desbalanceada em RL):\n"
                f"{linhas_antes}\n\n"
                f"  >>> Subarvore APOS PASSO 1 (Alinhamento em RR):\n"
                f"{linhas_p1}\n\n"
                f"  >>> Subarvore DEPOIS DO PASSO 2 (Balanceamento Concluido):\n"
                f"{linhas_depois}"
            )
            self.estatisticas.registrar_log(msg)
        return y

    def _rebalancear(self, no: NoAVL) -> NoAVL:
        no.atualizar_altura()
        fb = no.fator_balanceamento

        if fb > 1:
            if no.esquerda is not None and no.esquerda.fator_balanceamento >= 0:
                return self._rotacao_simples_direita(no)
            else:
                return self._rotacao_dupla_esquerda_direita(no)

        if fb < -1:
            if no.direita is not None and no.direita.fator_balanceamento <= 0:
                return self._rotacao_simples_esquerda(no)
            else:
                return self._rotacao_dupla_direita_esquerda(no)

        return no

    def inserir(self, conta: ContaBancaria) -> bool:
        inserido = False

        def _inserir_rec(no_atual: Optional[NoAVL]) -> Optional[NoAVL]:
            nonlocal inserido
            if no_atual is None:
                inserido = True
                self.quantidade_nos += 1
                if self.modo_detalhado:
                    self.estatisticas.registrar_log(
                        f"[AVL] Insercao da conta {conta.numero_conta} como novo no folha."
                    )
                return NoAVL(conta)

            if conta.numero_conta < no_atual.chave:
                no_atual.esquerda = _inserir_rec(no_atual.esquerda)
            elif conta.numero_conta > no_atual.chave:
                no_atual.direita = _inserir_rec(no_atual.direita)
            else:
                inserido = False
                if self.modo_detalhado:
                    self.estatisticas.registrar_log(
                        f"[AVL] Falha na insercao: Conta com numero {conta.numero_conta} ja existente."
                    )
                return no_atual

            return self._rebalancear(no_atual)

        self.raiz = _inserir_rec(self.raiz)
        return inserido

    def _menor_no(self, no: NoAVL) -> NoAVL:
        atual = no
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    def remover(self, numero_conta: int) -> Optional[ContaBancaria]:
        removido: Optional[ContaBancaria] = None
        rotacoes_antes = self.estatisticas.total_rotacoes
        arv_antes = self.renderizar_subarvore(self.raiz) if (self.modo_detalhado and self.raiz is not None) else ""

        def _remover_rec(no_atual: Optional[NoAVL], chave_alvo: int) -> Optional[NoAVL]:
            nonlocal removido
            if no_atual is None:
                return None

            if chave_alvo < no_atual.chave:
                no_atual.esquerda = _remover_rec(no_atual.esquerda, chave_alvo)
            elif chave_alvo > no_atual.chave:
                no_atual.direita = _remover_rec(no_atual.direita, chave_alvo)
            else:
                if removido is None:
                    removido = no_atual.conta
                    self.quantidade_nos -= 1

                eh_sucessor = (chave_alvo != numero_conta)
                rotulo = f"Conta {no_atual.chave} ({no_atual.conta.titular})"
                if eh_sucessor:
                    rotulo += " [SUCESSOR EM-ORDEM]"

                if no_atual.esquerda is None and no_atual.direita is None:
                    if self.modo_detalhado:
                        msg = (
                            f"[REMOCAO AVL - CASO 1: NO FOLHA (GRAU 0)]\n"
                            f"  * {rotulo} nao possui filhos.\n"
                            f"  * Operacao: No folha desconectado diretamente da arvore.\n"
                            f"  * Proximo passo: Recalculo de alturas e fatores de balanceamento dos ancestrais."
                        )
                        self.estatisticas.registrar_log(msg)
                    return None

                if no_atual.esquerda is None:
                    filho = no_atual.direita
                    if self.modo_detalhado:
                        msg = (
                            f"[REMOCAO AVL - CASO 2: NO COM 1 FILHO (GRAU 1)]\n"
                            f"  * {rotulo} possui apenas filho direito (Conta {filho.chave}).\n"
                            f"  * Operacao: Filho {filho.chave} ({filho.conta.titular}) promovido para a posicao do pai.\n"
                            f"  * Proximo passo: Recalculo de alturas e fatores de balanceamento dos ancestrais."
                        )
                        self.estatisticas.registrar_log(msg)
                    return filho
                elif no_atual.direita is None:
                    filho = no_atual.esquerda
                    if self.modo_detalhado:
                        msg = (
                            f"[REMOCAO AVL - CASO 2: NO COM 1 FILHO (GRAU 1)]\n"
                            f"  * {rotulo} possui apenas filho esquerdo (Conta {filho.chave}).\n"
                            f"  * Operacao: Filho {filho.chave} ({filho.conta.titular}) promovido para a posicao do pai.\n"
                            f"  * Proximo passo: Recalculo de alturas e fatores de balanceamento dos ancestrais."
                        )
                        self.estatisticas.registrar_log(msg)
                    return filho

                sucessor = self._menor_no(no_atual.direita)
                no_atual.conta = sucessor.conta
                if self.modo_detalhado:
                    msg = (
                        f"[REMOCAO AVL - CASO 3: NO COM 2 FILHOS (GRAU 2)]\n"
                        f"  * {rotulo} possui subarvores esquerda e direita.\n"
                        f"  * Localizado o sucessor em-ordem: Conta {sucessor.chave} ({sucessor.conta.titular}) - menor elemento da subarvore direita.\n"
                        f"  * Operacao: Conteudo da Conta {sucessor.chave} copiado para a posicao do no atual.\n"
                        f"  * Proximo passo: Remocao recursiva do sucessor (Conta {sucessor.chave}) na subarvore direita."
                    )
                    self.estatisticas.registrar_log(msg)
                no_atual.direita = _remover_rec(no_atual.direita, sucessor.chave)

            return self._rebalancear(no_atual)

        self.raiz = _remover_rec(self.raiz, numero_conta)
        if self.modo_detalhado and removido is not None:
            if rotacoes_antes == self.estatisticas.total_rotacoes:
                msg = (
                    f"[VERIFICACAO DE BALANCEAMENTO POS-REMOCAO AVL]\n"
                    f"  * Alturas e fatores de balanceamento recalculados ate a raiz.\n"
                    f"  * Todos os nos ancestrais permaneceram com |FB| <= 1. Nenhuma rotacao foi necessaria."
                )
                self.estatisticas.registrar_log(msg)

            arv_depois = self.renderizar_subarvore(self.raiz) if self.raiz is not None else "[Arvore Vazia]"
            msg_resumo = (
                f"[RESUMO VISUAL DA REMOCAO NA AVL - CONTA {numero_conta}]\n"
                f"  >>> Estrutura da Arvore ANTES da Remocao:\n"
                + "\n".join("    " + l for l in arv_antes.splitlines()) +
                f"\n\n  >>> Estrutura da Arvore DEPOIS da Remocao e Rebalanceamento:\n"
                + "\n".join("    " + l for l in arv_depois.splitlines())
            )
            self.estatisticas.registrar_log(msg_resumo)

        return removido

    def buscar(self, numero_conta: int) -> Optional[ContaBancaria]:
        atual = self.raiz
        while atual is not None:
            self.estatisticas.comparacoes += 1
            self.estatisticas.nos_visitados += 1
            if numero_conta == atual.chave:
                return atual.conta
            elif numero_conta < atual.chave:
                atual = atual.esquerda
            else:
                atual = atual.direita
        return None

    def obter_menor(self) -> Optional[ContaBancaria]:
        if self.raiz is None:
            return None
        return self._menor_no(self.raiz).conta

    def obter_maior(self) -> Optional[ContaBancaria]:
        if self.raiz is None:
            return None
        atual = self.raiz
        while atual.direita is not None:
            atual = atual.direita
        return atual.conta

    def caminhamento_em_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _in_order(no: Optional[NoAVL]) -> None:
            if no is not None:
                _in_order(no.esquerda)
                resultado.append(no.conta)
                _in_order(no.direita)

        _in_order(self.raiz)
        return resultado

    def caminhamento_pre_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pre_order(no: Optional[NoAVL]) -> None:
            if no is not None:
                resultado.append(no.conta)
                _pre_order(no.esquerda)
                _pre_order(no.direita)

        _pre_order(self.raiz)
        return resultado

    def caminhamento_pos_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pos_order(no: Optional[NoAVL]) -> None:
            if no is not None:
                _pos_order(no.esquerda)
                _pos_order(no.direita)
                resultado.append(no.conta)

        _pos_order(self.raiz)
        return resultado

    def validar_propriedades(self) -> Tuple[bool, str]:
        def _validar_no(
            no: Optional[NoAVL],
            min_val: Optional[int],
            max_val: Optional[int]
        ) -> Tuple[bool, str]:
            if no is None:
                return True, ""

            if min_val is not None and no.chave <= min_val:
                return False, f"Violacao da propriedade de ABB: chave {no.chave} <= minimo permitido {min_val}"
            if max_val is not None and no.chave >= max_val:
                return False, f"Violacao da propriedade de ABB: chave {no.chave} >= maximo permitido {max_val}"

            alt_esq = NoAVL.get_altura(no.esquerda)
            alt_dir = NoAVL.get_altura(no.direita)
            alt_esperada = 1 + max(alt_esq, alt_dir)

            if no.altura != alt_esperada:
                return False, f"Altura inconsistente no no {no.chave}: gravada={no.altura}, calculada={alt_esperada}"

            fb = alt_esq - alt_dir
            if abs(fb) > 1:
                return False, f"Desbalanceamento detectado no no {no.chave}: FB={fb} fora do intervalo [-1, 1]"

            valido_esq, erro_esq = _validar_no(no.esquerda, min_val, no.chave)
            if not valido_esq:
                return False, erro_esq

            valido_dir, erro_dir = _validar_no(no.direita, no.chave, max_val)
            if not valido_dir:
                return False, erro_dir

            return True, ""

        if self.raiz is None:
            return True, "Arvore vazia e valida."
        valido, msg = _validar_no(self.raiz, None, None)
        if valido:
            return True, "Todas as propriedades da Arvore AVL estao satisfeitas com sucesso."
        return False, msg

    def exibir_arvore(self) -> None:
        if self.raiz is None:
            print("[Arvore AVL Vazia]")
            return

        def _imprimir_horizontal(no: Optional[NoAVL], prefixo: str = "", eh_esq: Optional[bool] = None) -> None:
            if no is None:
                return

            if no.direita is not None:
                _imprimir_horizontal(no.direita, prefixo + ("|       " if eh_esq is True else "        "), False)

            if eh_esq is None:
                marcador = "[RAIZ] "
            elif eh_esq is False:
                marcador = "/---[D] "
            else:
                marcador = "\\---[E] "

            fb_sinal = f"+{no.fator_balanceamento}" if no.fator_balanceamento > 0 else str(no.fator_balanceamento)
            print(f"{prefixo}{marcador}({no.chave}) [h={no.altura}, FB={fb_sinal}] {no.conta.titular}")

            if no.esquerda is not None:
                _imprimir_horizontal(no.esquerda, prefixo + ("|       " if eh_esq is False else "        "), True)

        print(f"=== ESTRUTURA VISUAL DA ARVORE AVL (Total de Nos: {self.quantidade_nos}, Altura: {self.altura}) ===")
        print("Legenda: /---[D] Subarvore Direita | \\---[E] Subarvore Esquerda\n")
        _imprimir_horizontal(self.raiz)
