from __future__ import annotations
from modelos import Cor, NoRB

class ArvoreRubroNegra:
	"""Árvore de busca balanceada por regras de cores e rotações."""

	def __init__(self):
		"""Inicializa a árvore com uma raiz vazia e uma sentinela preta.

		A sentinela `nil` representa todas as folhas ausentes. Reutilizá-la
		 simplifica os algoritmos: eles podem acessar filhos e pais sem testar
		`None` a cada operação. Em uma árvore rubro-negra, folhas nulas são
		consideradas pretas.
		"""
		self.nil = NoRB(None, Cor.PRETO)
		self.nil.esquerda = self.nil.direita = self.nil.pai = self.nil
		self.raiz = self.nil

	def buscar(self, chave):
		"""Procura uma chave seguindo a propriedade de busca binária.

		Em cada nó, compara a chave procurada com a chave atual e desce para a
		esquerda (menores) ou para a direita (maiores). Retorna o nó encontrado
		ou `None` se a chave não estiver na árvore. Custa O(log n) quando a
		árvore está balanceada.
		"""
		no = self.raiz
		while no is not self.nil:
			if chave == no.chave:
				return no
			no = no.esquerda if chave < no.chave else no.direita
		return None

	def inserir(self, chave):
		"""Insere uma chave e restaura as regras de balanceamento.

		Primeiro encontra a posição de uma folha, como em uma árvore binária de
		busca. Chaves duplicadas não são inseridas. O novo nó começa vermelho
		(assim não altera a quantidade de nós pretos em cada caminho); depois,
		`_corrigir_insercao` resolve possíveis violações envolvendo nós vermelhos.
		"""
		pai = self.nil
		no = self.raiz
		while no is not self.nil:
			pai = no
			if chave == no.chave:
				return no
			no = no.esquerda if chave < no.chave else no.direita

		novo = NoRB(chave)
		novo.esquerda = novo.direita = self.nil
		novo.pai = pai
		if pai is self.nil:
			self.raiz = novo
		elif chave < pai.chave:
			pai.esquerda = novo
		else:
			pai.direita = novo
		self._corrigir_insercao(novo)
		return novo

	def _rotacao_esquerda(self, no):
		"""Faz uma rotação à esquerda em torno de `no`, preservando a ordenação.

		O filho direito sobe e `no` passa a ser seu filho esquerdo; a subárvore
		intermediária é reposicionada. Rotações mudam a forma da árvore sem mudar
		a ordem de busca, e são usadas para corrigir o balanceamento.
		"""
		filho = no.direita
		no.direita = filho.esquerda
		if filho.esquerda is not self.nil:
			filho.esquerda.pai = no
		filho.pai = no.pai
		if no.pai is self.nil:
			self.raiz = filho
		elif no is no.pai.esquerda:
			no.pai.esquerda = filho
		else:
			no.pai.direita = filho
		filho.esquerda = no
		no.pai = filho

	def _rotacao_direita(self, no):
		"""Faz a rotação simétrica à esquerda em torno de `no`.

		O filho esquerdo sobe, `no` passa a ser seu filho direito e a subárvore
		intermediária é reposicionada. A ordem das chaves continua válida.
		"""
		filho = no.esquerda
		no.esquerda = filho.direita
		if filho.direita is not self.nil:
			filho.direita.pai = no
		filho.pai = no.pai
		if no.pai is self.nil:
			self.raiz = filho
		elif no is no.pai.direita:
			no.pai.direita = filho
		else:
			no.pai.esquerda = filho
		filho.direita = no
		no.pai = filho

	def _corrigir_insercao(self, no):
		"""Restaura as regras rubro-negras após uma inserção.

		A regra principal em risco é não permitir dois nós vermelhos seguidos.
		O algoritmo examina pai e tio: se o tio é vermelho, recolore a família e
		continua em direção à raiz; se é preto, usa rotações e recolorações para
		reorganizar a árvore. Ao final, a raiz é preta. As regras preservadas
		mantêm a altura da árvore em O(log n).
		"""
		while no.pai.cor == Cor.VERMELHO:
			if no.pai is no.pai.pai.esquerda:
				tio = no.pai.pai.direita
				if tio.cor == Cor.VERMELHO:
					no.pai.cor = tio.cor = Cor.PRETO
					no.pai.pai.cor = Cor.VERMELHO
					no = no.pai.pai
				else:
					if no is no.pai.direita:
						no = no.pai
						self._rotacao_esquerda(no)
					no.pai.cor = Cor.PRETO
					no.pai.pai.cor = Cor.VERMELHO
					self._rotacao_direita(no.pai.pai)
			else:
				tio = no.pai.pai.esquerda
				if tio.cor == Cor.VERMELHO:
					no.pai.cor = tio.cor = Cor.PRETO
					no.pai.pai.cor = Cor.VERMELHO
					no = no.pai.pai
				else:
					if no is no.pai.esquerda:
						no = no.pai
						self._rotacao_direita(no)
					no.pai.cor = Cor.PRETO
					no.pai.pai.cor = Cor.VERMELHO
					self._rotacao_esquerda(no.pai.pai)
		self.raiz.cor = Cor.PRETO

	def _transplantar(self, antigo, novo):
		"""Substitui `antigo` por `novo` na posição que ele ocupa na árvore.

		Atualiza o vínculo com o pai (ou a raiz) e o ponteiro de pai de `novo`.
		É uma operação estrutural auxiliar usada pela remoção; não copia chaves.
		"""
		if antigo.pai is self.nil:
			self.raiz = novo
		elif antigo is antigo.pai.esquerda:
			antigo.pai.esquerda = novo
		else:
			antigo.pai.direita = novo
		novo.pai = antigo.pai

	def _minimo(self, no):
		"""Retorna o nó de menor chave na subárvore enraizada em `no`.

		Pela propriedade de busca binária, basta seguir os filhos esquerdos até
		chegar à folha sentinela. É usado para encontrar o sucessor na remoção.
		"""
		while no.esquerda is not self.nil:
			no = no.esquerda
		return no

	def remover(self, chave):
		"""Remove a chave indicada e reequilibra a árvore, se necessário.

		Busca o nó e trata os casos de zero, um ou dois filhos. No caso de dois
		filhos, move o sucessor (menor nó da subárvore direita) para seu lugar.
		A remoção de um nó preto pode alterar a quantidade de nós pretos em um
		caminho; por isso, `_corrigir_remocao` restaura as propriedades. Retorna
		`True` quando removeu a chave e `False` quando ela não existia.
		"""
		alvo = self.raiz
		while alvo is not self.nil and alvo.chave != chave:
			alvo = alvo.esquerda if chave < alvo.chave else alvo.direita
		if alvo is self.nil:
			return False

		removido = alvo
		cor_original = removido.cor
		if alvo.esquerda is self.nil:
			x = alvo.direita
			self._transplantar(alvo, alvo.direita)
		elif alvo.direita is self.nil:
			x = alvo.esquerda
			self._transplantar(alvo, alvo.esquerda)
		else:
			removido = self._minimo(alvo.direita)
			cor_original = removido.cor
			x = removido.direita
			if removido.pai is alvo:
				x.pai = removido
			else:
				self._transplantar(removido, removido.direita)
				removido.direita = alvo.direita
				removido.direita.pai = removido
			self._transplantar(alvo, removido)
			removido.esquerda = alvo.esquerda
			removido.esquerda.pai = removido
			removido.cor = alvo.cor

		if cor_original == Cor.PRETO:
			self._corrigir_remocao(x)
		return True

	def _corrigir_remocao(self, no):
		"""Restaura as regras de cores e a altura preta após remover um nó.

		Quando um nó preto é retirado, seu lugar pode ficar com um déficit de
		altura preta. O algoritmo analisa o irmão e os filhos dele, aplicando
		recolorações e rotações em casos simétricos para deslocar ou eliminar o
		 déficit. Termina deixando o nó e a sentinela pretos; assim, todos os
		caminhos da raiz às folhas voltam a ter a mesma quantidade de nós pretos.
		"""
		while no is not self.raiz and no.cor == Cor.PRETO:
			if no is no.pai.esquerda:
				irmao = no.pai.direita
				if irmao.cor == Cor.VERMELHO:
					irmao.cor = Cor.PRETO
					no.pai.cor = Cor.VERMELHO
					self._rotacao_esquerda(no.pai)
					irmao = no.pai.direita
				if irmao.esquerda.cor == Cor.PRETO and irmao.direita.cor == Cor.PRETO:
					if irmao is not self.nil:
						irmao.cor = Cor.VERMELHO
					no = no.pai
				else:
					if irmao.direita.cor == Cor.PRETO:
						irmao.esquerda.cor = Cor.PRETO
						irmao.cor = Cor.VERMELHO
						self._rotacao_direita(irmao)
						irmao = no.pai.direita
					irmao.cor = no.pai.cor
					no.pai.cor = Cor.PRETO
					irmao.direita.cor = Cor.PRETO
					self._rotacao_esquerda(no.pai)
					no = self.raiz
			else:
				irmao = no.pai.esquerda
				if irmao.cor == Cor.VERMELHO:
					irmao.cor = Cor.PRETO
					no.pai.cor = Cor.VERMELHO
					self._rotacao_direita(no.pai)
					irmao = no.pai.esquerda
				if irmao.direita.cor == Cor.PRETO and irmao.esquerda.cor == Cor.PRETO:
					if irmao is not self.nil:
						irmao.cor = Cor.VERMELHO
					no = no.pai
				else:
					if irmao.esquerda.cor == Cor.PRETO:
						irmao.direita.cor = Cor.PRETO
						irmao.cor = Cor.VERMELHO
						self._rotacao_esquerda(irmao)
						irmao = no.pai.esquerda
					irmao.cor = no.pai.cor
					no.pai.cor = Cor.PRETO
					irmao.esquerda.cor = Cor.PRETO
					self._rotacao_direita(no.pai)
					no = self.raiz
		no.cor = Cor.PRETO
		self.nil.cor = Cor.PRETO

	def em_ordem(self):
		"""Retorna as chaves em ordem crescente por percurso em ordem.

		Visita recursivamente a subárvore esquerda, o nó e a subárvore direita.
		Como a árvore obedece à propriedade de busca binária, esse percurso
		produz os valores ordenados. O custo é O(n), pois visita cada nó uma vez.
		"""
		valores = []

		def percorrer(no):
			if no is self.nil:
				return
			percorrer(no.esquerda)
			valores.append(no.chave)
			percorrer(no.direita)

		percorrer(self.raiz)
		return valores
