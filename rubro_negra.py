from __future__ import annotations
from typing import Optional, List, Tuple
from modelos import ContaBancaria, NoRB, Cor, EstatisticasOperacao


class ArvoreRubroNegra:
    def __init__(self, modo_detalhado: bool = False) -> None:
        self.NIL: NoRB = NoRB(conta=None, cor=Cor.PRETO)
        self.NIL.esquerda = self.NIL
        self.NIL.direita = self.NIL
        self.NIL.pai = self.NIL
        self.raiz: NoRB = self.NIL
        self.quantidade_nos: int = 0
        self.modo_detalhado: bool = modo_detalhado
        self.estatisticas: EstatisticasOperacao = EstatisticasOperacao()

    @property
    def tamanho(self) -> int:
        return self.quantidade_nos

    @property
    def esta_vazia(self) -> bool:
        return self.raiz == self.NIL

    @property
    def altura(self) -> int:
        def _calc_altura(no: NoRB) -> int:
            if no == self.NIL:
                return -1
            return 1 + max(_calc_altura(no.esquerda), _calc_altura(no.direita))
        return _calc_altura(self.raiz)

    def calcular_altura_negra(self) -> int:
        no = self.raiz
        bh = 0
        while no != self.NIL:
            if no.cor == Cor.PRETO:
                bh += 1
            no = no.esquerda
        return bh

    def renderizar_subarvore(self, raiz_local: NoRB, marcador_raiz: str = "[RAIZ]") -> str:
        linhas: List[str] = []

        def _imprimir(no: NoRB, prefixo: str = "", eh_esq: Optional[bool] = None) -> None:
            if no == self.NIL:
                return

            if no.direita != self.NIL:
                _imprimir(no.direita, prefixo + ("|       " if eh_esq is True else "        "), False)

            if eh_esq is None:
                marcador = f"{marcador_raiz} "
            elif eh_esq is False:
                marcador = "/---[D] "
            else:
                marcador = "\\---[E] "

            cor_tag = "PRETO" if no.cor == Cor.PRETO else "VERM"
            linhas.append(f"{prefixo}{marcador}({no.chave}) [{cor_tag}] {no.conta.titular}")

            if no.esquerda != self.NIL:
                _imprimir(no.esquerda, prefixo + ("|       " if eh_esq is False else "        "), True)

        _imprimir(raiz_local)
        return "\n".join(linhas)

    def _rotacao_esquerda(self, x: NoRB) -> None:
        y = x.direita
        x.direita = y.esquerda
        if y.esquerda != self.NIL:
            y.esquerda.pai = x
        y.pai = x.pai
        if x.pai == self.NIL:
            self.raiz = y
        elif x == x.pai.esquerda:
            x.pai.esquerda = y
        else:
            x.pai.direita = y
        y.esquerda = x
        x.pai = y
        self.estatisticas.rotacoes_simples_esquerda += 1

    def _rotacao_direita(self, y: NoRB) -> None:
        x = y.esquerda
        y.esquerda = x.direita
        if x.direita != self.NIL:
            x.direita.pai = y
        x.pai = y.pai
        if y.pai == self.NIL:
            self.raiz = x
        elif y == y.pai.direita:
            y.pai.direita = x
        else:
            y.pai.esquerda = x
        x.direita = y
        y.pai = x
        self.estatisticas.rotacoes_simples_direita += 1

    def buscar(self, numero_conta: int) -> Optional[ContaBancaria]:
        atual = self.raiz
        while atual != self.NIL:
            self.estatisticas.comparacoes += 1
            self.estatisticas.nos_visitados += 1
            if numero_conta == atual.chave:
                return atual.conta
            elif numero_conta < atual.chave:
                atual = atual.esquerda
            else:
                atual = atual.direita
        return None

    def _menor_no(self, no: NoRB) -> NoRB:
        atual = no
        while atual.esquerda != self.NIL:
            atual = atual.esquerda
        return atual

    def _maior_no(self, no: NoRB) -> NoRB:
        atual = no
        while atual.direita != self.NIL:
            atual = atual.direita
        return atual

    def obter_menor(self) -> Optional[ContaBancaria]:
        if self.raiz == self.NIL:
            return None
        return self._menor_no(self.raiz).conta

    def obter_maior(self) -> Optional[ContaBancaria]:
        if self.raiz == self.NIL:
            return None
        return self._maior_no(self.raiz).conta

    def caminhamento_em_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _in_order(no: NoRB) -> None:
            if no != self.NIL:
                _in_order(no.esquerda)
                resultado.append(no.conta)
                _in_order(no.direita)

        _in_order(self.raiz)
        return resultado

    def caminhamento_pre_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pre_order(no: NoRB) -> None:
            if no != self.NIL:
                resultado.append(no.conta)
                _pre_order(no.esquerda)
                _pre_order(no.direita)

        _pre_order(self.raiz)
        return resultado

    def caminhamento_pos_ordem(self) -> List[ContaBancaria]:
        resultado: List[ContaBancaria] = []

        def _pos_order(no: NoRB) -> None:
            if no != self.NIL:
                _pos_order(no.esquerda)
                _pos_order(no.direita)
                resultado.append(no.conta)

        _pos_order(self.raiz)
        return resultado

    def inserir(self, conta: ContaBancaria) -> bool:
        if self.buscar(conta.numero_conta) is not None:
            if self.modo_detalhado:
                self.estatisticas.registrar_log(
                    f"[RUBRO-NEGRA] Falha na insercao: Conta com numero {conta.numero_conta} ja existente."
                )
            return False

        z = NoRB(conta=conta, cor=Cor.VERMELHO, esquerda=self.NIL, direita=self.NIL, pai=self.NIL)
        y = self.NIL
        x = self.raiz

        while x != self.NIL:
            y = x
            if z.chave < x.chave:
                x = x.esquerda
            else:
                x = x.direita

        z.pai = y
        if y == self.NIL:
            self.raiz = z
        elif z.chave < y.chave:
            y.esquerda = z
        else:
            y.direita = z

        self.quantidade_nos += 1

        if self.modo_detalhado:
            arv_pos = self.renderizar_subarvore(self.raiz)
            msg_ins = (
                f"[INSERCAO BST - NOVO NO VERMELHO]\n"
                f"  * Conta {conta.numero_conta} ({conta.titular}) inserida como novo no VERMELHO.\n\n"
                f"  >>> Estrutura da arvore logo apos a insercao da conta {conta.numero_conta} (antes do rebalanceamento):\n"
                + "\n".join("    " + l for l in arv_pos.splitlines())
            )
            self.estatisticas.registrar_log(msg_ins)

        self._inserir_fixup(z)
        return True

    def _inserir_fixup(self, z: NoRB) -> None:
        while z.pai.cor == Cor.VERMELHO:
            if z.pai == z.pai.pai.esquerda:
                u = z.pai.pai.direita
                if u.cor == Cor.VERMELHO:
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    pai_chave = z.pai.chave
                    tio_chave = u.chave
                    avo_chave = z.pai.pai.chave
                    z.pai.cor = Cor.PRETO
                    u.cor = Cor.PRETO
                    z.pai.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 3
                    if self.modo_detalhado:
                        depois_txt = self.renderizar_subarvore(z.pai.pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 1: TIO VERMELHO]\n"
                            f"  * Conflito Vermelho-Vermelho: No ({z.chave}) e Pai ({pai_chave})\n"
                            f"  * Tio ({tio_chave}) e VERMELHO -> Solucao: Recoloracao (sem rotacao):\n"
                            f"      - Pai ({pai_chave}) passa a ser PRETO\n"
                            f"      - Tio ({tio_chave}) passa a ser PRETO\n"
                            f"      - Avo ({avo_chave}) passa a ser VERMELHO\n\n"
                            f"  >>> Subarvore ANTES da Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Recoloracao:\n"
                            + "\n".join("    " + l for l in depois_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)
                    z = z.pai.pai
                else:
                    if z == z.pai.direita:
                        antes_lr_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                        pai_lr = z.pai
                        z = z.pai
                        self._rotacao_esquerda(z)
                        if self.modo_detalhado:
                            depois_lr_txt = self.renderizar_subarvore(z.pai.pai)
                            msg = (
                                f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 2: TIO PRETO EM ZIGUE-ZAGUE (LR)]\n"
                                f"  * Conflito no No ({z.direita.chave}) com Pai ({pai_lr.chave}) em formato Zigue-Zague (LR)\n"
                                f"  * Passo Preparatorio: Rotacao Simples a Esquerda no Pai ({pai_lr.chave}) -> Transforma no Caso LL\n\n"
                                f"  >>> Subarvore ANTES da Rotacao no Pai (Conflito LR):\n"
                                + "\n".join("    " + l for l in antes_lr_txt.splitlines()) +
                                f"\n\n  >>> Subarvore APOS Rotacao no Pai (Alinhada em Linha Reta LL):\n"
                                + "\n".join("    " + l for l in depois_lr_txt.splitlines())
                            )
                            self.estatisticas.registrar_log(msg)
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    avo = z.pai.pai
                    pai = z.pai
                    self._rotacao_direita(avo)
                    pos_rot_txt = self.renderizar_subarvore(pai) if self.modo_detalhado else ""
                    pai.cor = Cor.PRETO
                    avo.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    if self.modo_detalhado:
                        pos_recolor_txt = self.renderizar_subarvore(pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 3: TIO PRETO EM LINHA RETA (LL)]\n"
                            f"  * Conflito no No ({z.chave}) com Pai ({pai.chave}) - Ambos VERMELHOS\n"
                            f"  * Tio e PRETO (ou NIL) em linha reta -> Rebalanceamento em 2 Passos:\n"
                            f"      - Passo 1: Rotacao Simples a Direita no Avo ({avo.chave})\n"
                            f"      - Passo 2: Ajuste de Cores: Pai ({pai.chave}) -> PRETO, Avo ({avo.chave}) -> VERMELHO\n\n"
                            f"  >>> Estado Inicial: Subarvore ANTES da Rotacao e Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Passo 1: Apos Rotacao a Direita no Avo ({avo.chave}) [Estrutura Girada, Cores Originais]:\n"
                            + "\n".join("    " + l for l in pos_rot_txt.splitlines()) +
                            f"\n\n  >>> Passo 2: Apos Ajuste de Cores / Recoloracao [Pai ({pai.chave}) -> PRETO, Avo ({avo.chave}) -> VERMELHO]:\n"
                            + "\n".join("    " + l for l in pos_recolor_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)
            else:
                u = z.pai.pai.esquerda
                if u.cor == Cor.VERMELHO:
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    pai_chave = z.pai.chave
                    tio_chave = u.chave
                    avo_chave = z.pai.pai.chave
                    z.pai.cor = Cor.PRETO
                    u.cor = Cor.PRETO
                    z.pai.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 3
                    if self.modo_detalhado:
                        depois_txt = self.renderizar_subarvore(z.pai.pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 1: TIO VERMELHO]\n"
                            f"  * Conflito Vermelho-Vermelho: No ({z.chave}) e Pai ({pai_chave})\n"
                            f"  * Tio ({tio_chave}) e VERMELHO -> Solucao: Recoloracao (sem rotacao):\n"
                            f"      - Pai ({pai_chave}) passa a ser PRETO\n"
                            f"      - Tio ({tio_chave}) passa a ser PRETO\n"
                            f"      - Avo ({avo_chave}) passa a ser VERMELHO\n\n"
                            f"  >>> Subarvore ANTES da Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Recoloracao:\n"
                            + "\n".join("    " + l for l in depois_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)
                    z = z.pai.pai
                else:
                    if z == z.pai.esquerda:
                        antes_rl_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                        pai_rl = z.pai
                        z = z.pai
                        self._rotacao_direita(z)
                        if self.modo_detalhado:
                            depois_rl_txt = self.renderizar_subarvore(z.pai.pai)
                            msg = (
                                f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 2: TIO PRETO EM ZIGUE-ZAGUE (RL)]\n"
                                f"  * Conflito no No ({z.esquerda.chave}) com Pai ({pai_rl.chave}) em formato Zigue-Zague (RL)\n"
                                f"  * Passo Preparatorio: Rotacao Simples a Direita no Pai ({pai_rl.chave}) -> Transforma no Caso RR\n\n"
                                f"  >>> Subarvore ANTES da Rotacao no Pai (Conflito RL):\n"
                                + "\n".join("    " + l for l in antes_rl_txt.splitlines()) +
                                f"\n\n  >>> Subarvore APOS Rotacao no Pai (Alinhada em Linha Reta RR):\n"
                                + "\n".join("    " + l for l in depois_rl_txt.splitlines())
                            )
                            self.estatisticas.registrar_log(msg)
                    antes_txt = self.renderizar_subarvore(z.pai.pai) if self.modo_detalhado else ""
                    avo = z.pai.pai
                    pai = z.pai
                    self._rotacao_esquerda(avo)
                    pos_rot_txt = self.renderizar_subarvore(pai) if self.modo_detalhado else ""
                    pai.cor = Cor.PRETO
                    avo.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    if self.modo_detalhado:
                        pos_recolor_txt = self.renderizar_subarvore(pai)
                        msg = (
                            f"[REBALANCEAMENTO RUBRO-NEGRA - CASO 3: TIO PRETO EM LINHA RETA (RR)]\n"
                            f"  * Conflito no No ({z.chave}) com Pai ({pai.chave}) - Ambos VERMELHOS\n"
                            f"  * Tio e PRETO (ou NIL) em linha reta -> Rebalanceamento em 2 Passos:\n"
                            f"      - Passo 1: Rotacao Simples a Esquerda no Avo ({avo.chave})\n"
                            f"      - Passo 2: Ajuste de Cores: Pai ({pai.chave}) -> PRETO, Avo ({avo.chave}) -> VERMELHO\n\n"
                            f"  >>> Estado Inicial: Subarvore ANTES da Rotacao e Recoloracao:\n"
                            + "\n".join("    " + l for l in antes_txt.splitlines()) +
                            f"\n\n  >>> Passo 1: Apos Rotacao a Esquerda no Avo ({avo.chave}) [Estrutura Girada, Cores Originais]:\n"
                            + "\n".join("    " + l for l in pos_rot_txt.splitlines()) +
                            f"\n\n  >>> Passo 2: Apos Ajuste de Cores / Recoloracao [Pai ({pai.chave}) -> PRETO, Avo ({avo.chave}) -> VERMELHO]:\n"
                            + "\n".join("    " + l for l in pos_recolor_txt.splitlines())
                        )
                        self.estatisticas.registrar_log(msg)

        if self.raiz.cor != Cor.PRETO:
            antes_raiz_txt = self.renderizar_subarvore(self.raiz) if self.modo_detalhado else ""
            self.raiz.cor = Cor.PRETO
            self.estatisticas.recoloracoes += 1
            if self.modo_detalhado:
                depois_raiz_txt = self.renderizar_subarvore(self.raiz)
                msg = (
                    f"[AJUSTE FINAL - PROPRIEDADE 2: RAIZ PRETA]\n"
                    f"  * A raiz ({self.raiz.chave}) era VERMELHA -> Recolorida para PRETO para satisfazer a Propriedade 2.\n\n"
                    f"  >>> Subarvore ANTES do Ajuste da Raiz:\n"
                    + "\n".join("    " + l for l in antes_raiz_txt.splitlines()) +
                    f"\n\n  >>> Subarvore DEPOIS do Ajuste da Raiz (Propriedade 2 Satisfeita):\n"
                    + "\n".join("    " + l for l in depois_raiz_txt.splitlines())
                )
                self.estatisticas.registrar_log(msg)

    def _transplant(self, u: NoRB, v: NoRB) -> None:
        if u.pai == self.NIL:
            self.raiz = v
        elif u == u.pai.esquerda:
            u.pai.esquerda = v
        else:
            u.pai.direita = v
        v.pai = u.pai

    def remover(self, numero_conta: int) -> Optional[ContaBancaria]:
        z = self.raiz
        while z != self.NIL and z.chave != numero_conta:
            if numero_conta < z.chave:
                z = z.esquerda
            else:
                z = z.direita

        if z == self.NIL:
            return None

        conta_removida = z.conta
        arv_antes = self.renderizar_subarvore(self.raiz) if (self.modo_detalhado and self.raiz != self.NIL) else ""

        if z.esquerda == self.NIL and z.direita == self.NIL:
            tipo_rem = "No folha (grau 0) desconectado diretamente da arvore"
        elif z.esquerda == self.NIL:
            tipo_rem = f"No com 1 filho (grau 1): filho direito (Conta {z.direita.chave}) promovido para o lugar do pai"
        elif z.direita == self.NIL:
            tipo_rem = f"No com 1 filho (grau 1): filho esquerdo (Conta {z.esquerda.chave}) promovido para o lugar do pai"
        else:
            tipo_rem = "No com 2 filhos (grau 2): substituido pelo sucessor em-ordem"

        self.quantidade_nos -= 1

        y = z
        y_cor_original = y.cor
        z_cor_original = z.cor
        tem_dois_filhos = (z.esquerda != self.NIL and z.direita != self.NIL)

        if z.esquerda == self.NIL:
            x = z.direita
            self._transplant(z, z.direita)
        elif z.direita == self.NIL:
            x = z.esquerda
            self._transplant(z, z.esquerda)
        else:
            y = self._menor_no(z.direita)
            y_cor_original = y.cor
            x = y.direita
            if y.pai == z:
                x.pai = y
            else:
                self._transplant(y, y.direita)
                y.direita = z.direita
                y.direita.pai = y
            self._transplant(z, y)
            y.esquerda = z.esquerda
            y.esquerda.pai = y
            if y.cor != z.cor:
                y.cor = z.cor
                self.estatisticas.recoloracoes += 1
            else:
                y.cor = z.cor

        if self.modo_detalhado:
            if tem_dois_filhos:
                msg_rem = (
                    f"[REMOCAO BST - EXCLUSAO DA CONTA NA RUBRO-NEGRA]\n"
                    f"  * Conta Alvo: Conta {numero_conta} ({conta_removida.titular}) - Cor original: {z_cor_original.value}.\n"
                    f"  * Estrutura: No com 2 filhos (grau 2).\n"
                    f"  * Sucessor Em-Ordem localizado: Conta {y.chave} ({y.conta.titular}) - Cor original: {y_cor_original.value}.\n"
                    f"  * Operacao de Substituicao: O sucessor (Conta {y.chave}) assume a posicao fisica da Conta {numero_conta}."
                )
                self.estatisticas.registrar_log(msg_rem)
                if y_cor_original != z_cor_original:
                    msg_rec = (
                        f"[RECOLORACAO NA RUBRO-NEGRA - HERANCA DA COR DO NO ALVO]\n"
                        f"  * O sucessor (Conta {y.chave}) assume a cor do no que substituiu (Conta {numero_conta}).\n"
                        f"  * Acao: Conta {y.chave} e RECOLORIDA de {y_cor_original.value} para {z_cor_original.value}.\n"
                        f"  * Justificativa: Preserva a cor {z_cor_original.value} naquele ponto da arvore, satisfazendo as propriedades da raiz/ancestral."
                    )
                    self.estatisticas.registrar_log(msg_rec)
            else:
                msg_rem = (
                    f"[REMOCAO BST - EXCLUSAO DA CONTA NA RUBRO-NEGRA]\n"
                    f"  * Conta Alvo: Conta {numero_conta} ({conta_removida.titular}) - Cor original: {y_cor_original.value}.\n"
                    f"  * Estrutura: {tipo_rem}.\n"
                    f"  * Operacao: No desconectado diretamente da arvore."
                )
                self.estatisticas.registrar_log(msg_rem)

        if y_cor_original == Cor.PRETO:
            if self.modo_detalhado and self.raiz != self.NIL:
                no_saida = f"sucessor Conta {y.chave}" if tem_dois_filhos else f"Conta {numero_conta}"
                self.estatisticas.registrar_log(
                    f"[ANALISE DA ALTURA NEGRA - NO DESLOCADO ERA PRETO]\n"
                    f"  * O no que fisicamente desocupou sua posicao na base da arvore ({no_saida}) tinha cor PRETO.\n"
                    f"  * Consequencia: A perda de um no preto reduziu a altura negra (bh) nesse ramo.\n"
                    f"  * O no substituto x ({x.chave if x != self.NIL else 'NIL'}) recebe a 'dupla-preta'. Iniciando resolucao de fixup."
                )
            self._remover_fixup(x)
        else:
            if self.modo_detalhado:
                no_saida = f"sucessor Conta {y.chave}" if tem_dois_filhos else f"Conta {numero_conta}"
                msg_verm = (
                    f"[ANALISE DA ALTURA NEGRA - NO DESLOCADO ERA VERMELHO]\n"
                    f"  * O no que fisicamente desocupou sua posicao na base da arvore ({no_saida}) tinha cor VERMELHO.\n"
                    f"  * Consequencia: A remocao de um no vermelho nao reduz a contagem de nos pretos em nenhum caminho ate NIL.\n"
                    f"  * Propriedades Rubro-Negras (altura negra bh e ausencia de conflitos) preservadas intactas.\n"
                    f"  * Rebalanceamento concluido sem necessidade de fixup ou rotacoes."
                )
                self.estatisticas.registrar_log(msg_verm)

        if self.modo_detalhado:
            arv_depois = self.renderizar_subarvore(self.raiz) if self.raiz != self.NIL else "[Arvore Vazia]"
            msg_resumo = (
                f"[RESUMO VISUAL DA REMOCAO NA RUBRO-NEGRA - CONTA {numero_conta}]\n"
                f"  >>> Estrutura da Arvore ANTES da Remocao:\n"
                + "\n".join("    " + l for l in arv_antes.splitlines()) +
                f"\n\n  >>> Estrutura da Arvore DEPOIS da Remocao e Rebalanceamento:\n"
                + "\n".join("    " + l for l in arv_depois.splitlines())
            )
            self.estatisticas.registrar_log(msg_resumo)

        return conta_removida

    def _remover_fixup(self, x: NoRB) -> None:
        while x != self.raiz and x.cor == Cor.PRETO:
            if x == x.pai.esquerda:
                w = x.pai.direita
                if w.cor == Cor.VERMELHO:
                    antes_c1 = self.renderizar_subarvore(x.pai) if self.modo_detalhado else ""
                    w.cor = Cor.PRETO
                    x.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    self._rotacao_esquerda(x.pai)
                    if self.modo_detalhado:
                        depois_c1 = self.renderizar_subarvore(w)
                        msg_c1 = (
                            f"[REMOCAO RUBRO-NEGRA - CASO 1: IRMAO VERMELHO]\n"
                            f"  * Irmao ({w.chave if w != self.NIL else 'NIL'}) e VERMELHO.\n"
                            f"  * Acao: Inversao de cores (Irmao -> PRETO, Pai -> VERMELHO) e Rotacao a Esquerda no Pai ({x.pai.chave}).\n\n"
                            f"  >>> Subarvore ANTES do Caso 1:\n"
                            + "\n".join("    " + l for l in antes_c1.splitlines()) +
                            f"\n\n  >>> Subarvore APOS Caso 1 (Novo irmao e PRETO):\n"
                            + "\n".join("    " + l for l in depois_c1.splitlines())
                        )
                        self.estatisticas.registrar_log(msg_c1)
                    w = x.pai.direita

                if w.esquerda.cor == Cor.PRETO and w.direita.cor == Cor.PRETO:
                    antes_c2 = self.renderizar_subarvore(x.pai) if self.modo_detalhado else ""
                    w.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 1
                    if self.modo_detalhado:
                        depois_c2 = self.renderizar_subarvore(x.pai)
                        msg_c2 = (
                            f"[REMOCAO RUBRO-NEGRA - CASO 2: IRMAO PRETO COM AMBOS OS FILHOS PRETOS]\n"
                            f"  * Irmao ({w.chave if w != self.NIL else 'NIL'}) e seus 2 filhos sao PRETOS.\n"
                            f"  * Acao: Irmao passa a ser VERMELHO. O no duplo-preto sobe para o Pai ({x.pai.chave if x.pai != self.NIL else 'RAIZ'}).\n\n"
                            f"  >>> Subarvore ANTES da Recoloracao do Irmao:\n"
                            + "\n".join("    " + l for l in antes_c2.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Recoloracao do Irmao:\n"
                            + "\n".join("    " + l for l in depois_c2.splitlines())
                        )
                        self.estatisticas.registrar_log(msg_c2)
                    x = x.pai
                else:
                    if w.direita.cor == Cor.PRETO:
                        antes_c3 = self.renderizar_subarvore(w) if self.modo_detalhado else ""
                        w.esquerda.cor = Cor.PRETO
                        w.cor = Cor.VERMELHO
                        self.estatisticas.recoloracoes += 2
                        self._rotacao_direita(w)
                        if self.modo_detalhado:
                            depois_c3 = self.renderizar_subarvore(w.pai)
                            msg_c3 = (
                                f"[REMOCAO RUBRO-NEGRA - CASO 3: IRMAO PRETO EM ZIGUE-ZAGUE (RL)]\n"
                                f"  * Filho direito do irmao e PRETO, filho esquerdo e VERMELHO.\n"
                                f"  * Acao: Inversao de cores e Rotacao a Direita no Irmao -> Transforma em Caso 4.\n\n"
                                f"  >>> Subarvore do Irmao ANTES da Rotacao:\n"
                                + "\n".join("    " + l for l in antes_c3.splitlines()) +
                                f"\n\n  >>> Subarvore do Irmao APOS Rotacao (Alinhada no Caso 4):\n"
                                + "\n".join("    " + l for l in depois_c3.splitlines())
                            )
                            self.estatisticas.registrar_log(msg_c3)
                        w = x.pai.direita

                    antes_c4 = self.renderizar_subarvore(x.pai) if self.modo_detalhado else ""
                    pai_ref = x.pai
                    pai_cor_orig = pai_ref.cor
                    self._rotacao_esquerda(pai_ref)
                    pos_rot_c4 = self.renderizar_subarvore(w) if self.modo_detalhado else ""
                    w.cor = pai_cor_orig
                    pai_ref.cor = Cor.PRETO
                    w.direita.cor = Cor.PRETO
                    self.estatisticas.recoloracoes += 3
                    if self.modo_detalhado:
                        pos_rec_c4 = self.renderizar_subarvore(w)
                        msg_c4 = (
                            f"[REMOCAO RUBRO-NEGRA - CASO 4: IRMAO PRETO COM FILHO EXTERNO VERMELHO (RR)]\n"
                            f"  * Filho direito do irmao e VERMELHO.\n"
                            f"  * Passo 1: Rotacao a Esquerda no Pai ({pai_ref.chave})\n"
                            f"  * Passo 2: Ajuste de Cores (Irmao assume cor do pai, Pai e Filho Direito passam a PRETO)\n\n"
                            f"  >>> Subarvore ANTES da Rotacao e Ajuste:\n"
                            + "\n".join("    " + l for l in antes_c4.splitlines()) +
                            f"\n\n  >>> Passo 1: Apos Rotacao a Esquerda no Pai ({pai_ref.chave}) [Estrutura Girada]:\n"
                            + "\n".join("    " + l for l in pos_rot_c4.splitlines()) +
                            f"\n\n  >>> Passo 2: Apos Ajuste de Cores (Duplo-Preto Eliminado):\n"
                            + "\n".join("    " + l for l in pos_rec_c4.splitlines())
                        )
                        self.estatisticas.registrar_log(msg_c4)
                    x = self.raiz
            else:
                w = x.pai.esquerda
                if w.cor == Cor.VERMELHO:
                    antes_c1 = self.renderizar_subarvore(x.pai) if self.modo_detalhado else ""
                    w.cor = Cor.PRETO
                    x.pai.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 2
                    self._rotacao_direita(x.pai)
                    if self.modo_detalhado:
                        depois_c1 = self.renderizar_subarvore(w)
                        msg_c1 = (
                            f"[REMOCAO RUBRO-NEGRA - CASO 1: IRMAO VERMELHO]\n"
                            f"  * Irmao ({w.chave if w != self.NIL else 'NIL'}) e VERMELHO.\n"
                            f"  * Acao: Inversao de cores (Irmao -> PRETO, Pai -> VERMELHO) e Rotacao a Direita no Pai ({x.pai.chave}).\n\n"
                            f"  >>> Subarvore ANTES do Caso 1:\n"
                            + "\n".join("    " + l for l in antes_c1.splitlines()) +
                            f"\n\n  >>> Subarvore APOS Caso 1 (Novo irmao e PRETO):\n"
                            + "\n".join("    " + l for l in depois_c1.splitlines())
                        )
                        self.estatisticas.registrar_log(msg_c1)
                    w = x.pai.esquerda

                if w.direita.cor == Cor.PRETO and w.esquerda.cor == Cor.PRETO:
                    antes_c2 = self.renderizar_subarvore(x.pai) if self.modo_detalhado else ""
                    w.cor = Cor.VERMELHO
                    self.estatisticas.recoloracoes += 1
                    if self.modo_detalhado:
                        depois_c2 = self.renderizar_subarvore(x.pai)
                        msg_c2 = (
                            f"[REMOCAO RUBRO-NEGRA - CASO 2: IRMAO PRETO COM AMBOS OS FILHOS PRETOS]\n"
                            f"  * Irmao ({w.chave if w != self.NIL else 'NIL'}) e seus 2 filhos sao PRETOS.\n"
                            f"  * Acao: Irmao passa a ser VERMELHO. O no duplo-preto sobe para o Pai ({x.pai.chave if x.pai != self.NIL else 'RAIZ'}).\n\n"
                            f"  >>> Subarvore ANTES da Recoloracao do Irmao:\n"
                            + "\n".join("    " + l for l in antes_c2.splitlines()) +
                            f"\n\n  >>> Subarvore DEPOIS da Recoloracao do Irmao:\n"
                            + "\n".join("    " + l for l in depois_c2.splitlines())
                        )
                        self.estatisticas.registrar_log(msg_c2)
                    x = x.pai
                else:
                    if w.esquerda.cor == Cor.PRETO:
                        antes_c3 = self.renderizar_subarvore(w) if self.modo_detalhado else ""
                        w.direita.cor = Cor.PRETO
                        w.cor = Cor.VERMELHO
                        self.estatisticas.recoloracoes += 2
                        self._rotacao_esquerda(w)
                        if self.modo_detalhado:
                            depois_c3 = self.renderizar_subarvore(w.pai)
                            msg_c3 = (
                                f"[REMOCAO RUBRO-NEGRA - CASO 3: IRMAO PRETO EM ZIGUE-ZAGUE (LR)]\n"
                                f"  * Filho esquerdo do irmao e PRETO, filho direito e VERMELHO.\n"
                                f"  * Acao: Inversao de cores e Rotacao a Esquerda no Irmao -> Transforma em Caso 4.\n\n"
                                f"  >>> Subarvore do Irmao ANTES da Rotacao:\n"
                                + "\n".join("    " + l for l in antes_c3.splitlines()) +
                                f"\n\n  >>> Subarvore do Irmao APOS Rotacao (Alinhada no Caso 4):\n"
                                + "\n".join("    " + l for l in depois_c3.splitlines())
                            )
                            self.estatisticas.registrar_log(msg_c3)
                        w = x.pai.esquerda

                    antes_c4 = self.renderizar_subarvore(x.pai) if self.modo_detalhado else ""
                    pai_ref = x.pai
                    pai_cor_orig = pai_ref.cor
                    self._rotacao_direita(pai_ref)
                    pos_rot_c4 = self.renderizar_subarvore(w) if self.modo_detalhado else ""
                    w.cor = pai_cor_orig
                    pai_ref.cor = Cor.PRETO
                    w.esquerda.cor = Cor.PRETO
                    self.estatisticas.recoloracoes += 3
                    if self.modo_detalhado:
                        pos_rec_c4 = self.renderizar_subarvore(w)
                        msg_c4 = (
                            f"[REMOCAO RUBRO-NEGRA - CASO 4: IRMAO PRETO COM FILHO EXTERNO VERMELHO (LL)]\n"
                            f"  * Filho esquerdo do irmao e VERMELHO.\n"
                            f"  * Passo 1: Rotacao a Direita no Pai ({pai_ref.chave})\n"
                            f"  * Passo 2: Ajuste de Cores (Irmao assume cor do pai, Pai e Filho Esquerdo passam a PRETO)\n\n"
                            f"  >>> Subarvore ANTES da Rotacao e Ajuste:\n"
                            + "\n".join("    " + l for l in antes_c4.splitlines()) +
                            f"\n\n  >>> Passo 1: Apos Rotacao a Direita no Pai ({pai_ref.chave}) [Estrutura Girada]:\n"
                            + "\n".join("    " + l for l in pos_rot_c4.splitlines()) +
                            f"\n\n  >>> Passo 2: Apos Ajuste de Cores (Duplo-Preto Eliminado):\n"
                            + "\n".join("    " + l for l in pos_rec_c4.splitlines())
                        )
                        self.estatisticas.registrar_log(msg_c4)
                    x = self.raiz

        if x.cor != Cor.PRETO:
            antes_f = self.renderizar_subarvore(x) if (self.modo_detalhado and x != self.NIL) else ""
            x.cor = Cor.PRETO
            self.estatisticas.recoloracoes += 1
            if self.modo_detalhado and x != self.NIL:
                depois_f = self.renderizar_subarvore(x)
                msg_f = (
                    f"[AJUSTE FINAL - REMOCAO FIXUP]\n"
                    f"  * No ({x.chave}) era VERMELHO com duplo-preto absorvido -> Recolorido para PRETO.\n\n"
                    f"  >>> Subarvore ANTES do Ajuste Final:\n"
                    + "\n".join("    " + l for l in antes_f.splitlines()) +
                    f"\n\n  >>> Subarvore DEPOIS do Ajuste Final:\n"
                    + "\n".join("    " + l for l in depois_f.splitlines())
                )
                self.estatisticas.registrar_log(msg_f)

    def validar_propriedades(self) -> Tuple[bool, str]:
        if self.raiz == self.NIL:
            return True, "Arvore vazia e valida (raiz e sentinela NIL pretos)."

        if self.raiz.cor != Cor.PRETO:
            return False, f"Violacao da Propriedade 2: A raiz ({self.raiz.chave}) deve ser PRETA, mas e {self.raiz.cor.value}."

        if self.NIL.cor != Cor.PRETO:
            return False, "Violacao da Propriedade 3: O sentinela NIL deve ser PRETO."

        erro: Optional[str] = None
        altura_negra_esperada: Optional[int] = None

        def _validar_no(no: NoRB, min_val: Optional[int], max_val: Optional[int], bh_atual: int) -> bool:
            nonlocal erro, altura_negra_esperada
            if erro is not None:
                return False

            if no == self.NIL:
                if altura_negra_esperada is None:
                    altura_negra_esperada = bh_atual
                elif bh_atual != altura_negra_esperada:
                    erro = f"Violacao da Propriedade 5: Caminhos com alturas negras divergentes (esperada: {altura_negra_esperada}, encontrada: {bh_atual})."
                    return False
                return True

            if no.cor not in (Cor.VERMELHO, Cor.PRETO):
                erro = f"Violacao da Propriedade 1: No ({no.chave}) com cor invalida {no.cor}."
                return False

            if min_val is not None and no.chave <= min_val:
                erro = f"Violacao da propriedade de ABB: Chave {no.chave} <= minimo permitido {min_val}."
                return False
            if max_val is not None and no.chave >= max_val:
                erro = f"Violacao da propriedade de ABB: Chave {no.chave} >= maximo permitido {max_val}."
                return False

            if no.cor == Cor.VERMELHO:
                if no.esquerda.cor == Cor.VERMELHO:
                    erro = f"Violacao da Propriedade 4: No VERMELHO ({no.chave}) possui filho esquerdo VERMELHO ({no.esquerda.chave})."
                    return False
                if no.direita.cor == Cor.VERMELHO:
                    erro = f"Violacao da Propriedade 4: No VERMELHO ({no.chave}) possui filho direito VERMELHO ({no.direita.chave})."
                    return False

            proximo_bh = bh_atual + (1 if no.cor == Cor.PRETO else 0)

            if not _validar_no(no.esquerda, min_val, no.chave, proximo_bh):
                return False
            if not _validar_no(no.direita, no.chave, max_val, proximo_bh):
                return False

            return True

        valido = _validar_no(self.raiz, None, None, 0)
        if not valido or erro is not None:
            return False, erro if erro else "Violacao detectada nas propriedades da Arvore Rubro-Negra."

        return True, f"Todas as 5 propriedades Rubro-Negras estao satisfeitas com sucesso (Altura Negra bh={altura_negra_esperada})."

    def exibir_arvore(self) -> None:
        if self.raiz == self.NIL:
            print("[Arvore Rubro-Negra Vazia]")
            return

        def _imprimir_horizontal(no: NoRB, prefixo: str = "", eh_esq: Optional[bool] = None) -> None:
            if no == self.NIL:
                return

            if no.direita != self.NIL:
                _imprimir_horizontal(no.direita, prefixo + ("|       " if eh_esq is True else "        "), False)

            if eh_esq is None:
                marcador = "[RAIZ] "
            elif eh_esq is False:
                marcador = "/---[D] "
            else:
                marcador = "\\---[E] "

            cor_tag = "PRETO" if no.cor == Cor.PRETO else "VERM"
            print(f"{prefixo}{marcador}({no.chave}) [{cor_tag}] {no.conta.titular}")

            if no.esquerda != self.NIL:
                _imprimir_horizontal(no.esquerda, prefixo + ("|       " if eh_esq is False else "        "), True)

        print(f"=== ESTRUTURA VISUAL DA ARVORE RUBRO-NEGRA (Total de Nos: {self.quantidade_nos}, Altura: {self.altura}, Altura Negra: {self.calcular_altura_negra()}) ===")
        print("Legenda: /---[D] Subarvore Direita | \\---[E] Subarvore Esquerda | [PRETO] No Preto | [VERM] No Vermelho\n")
        _imprimir_horizontal(self.raiz)
