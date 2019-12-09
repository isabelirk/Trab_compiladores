from Automatos import Automato
from Producao import Producao
import xml.etree.ElementTree as ET

class Inuteis(Automato):

    def __init__(self, automato):
        super(Inuteis, self).__init__()
        self.Estados = automato.Estados
        self.Alfabeto = automato.Alfabeto
        self.Finais = automato.Finais
        self.TransicoesVisitadas = automato.TransicoesVisitadas
        self.AutomatoMinimizado = automato.AutomatoMinimizado

    def gerarEstadosParaMinimizacao(self):
        estadosTemp = dict()
        AutomatoValido = self.pegarAutomato()

        for transicao in AutomatoValido:
            if (transicao in self.Finais) and (AutomatoValido[transicao] == {}):
                estadosTemp.update({transicao: {}})
                continue

            for producao in list(AutomatoValido[transicao]):
                if len(AutomatoValido[transicao][producao]) > 0:
                    if transicao not in estadosTemp: 
                        estadosTemp.update({transicao: {producao: Producao(AutomatoValido[transicao][producao][0])}})
                    else:
                        if producao not in estadosTemp[transicao]:
                            estadosTemp[transicao].update({producao: Producao(AutomatoValido[transicao][producao][0])})
                else:                    
                    if ((transicao in estadosTemp) and (producao not in estadosTemp[transicao])):
                        estadosTemp[transicao].update({producao: Producao(-1)})
                    elif transicao in self.Finais:
                        estadosTemp.update({transicao: {producao: Producao(-1)}})

        return estadosTemp

    def adicionaAutomatoMinimizado(self,transicao,producaoAtual,producaoInserir):
        if producaoAtual == -1:
            if transicao not in self.AutomatoMinimizado:
                self.AutomatoMinimizado.update({transicao: {}})
        else:
            if transicao not in self.AutomatoMinimizado:
                self.AutomatoMinimizado.update({transicao: {producaoAtual: [producaoInserir]}})
            else:
                if producaoAtual not in self.AutomatoMinimizado[transicao]:
                    self.AutomatoMinimizado[transicao].update({producaoAtual: [producaoInserir]})



############################## Organiza o automato para realizar as operacoes das classes abaixo ##############################
automato = Automato()                              
automato.carrega('entrada.txt')                      
#automato.imprimir('\n\n# AUTOMATO LIDO:\n', True)  


############################## Elimina Epsilon Transição ##############################
class EpsilonTransicao(Automato):
    
    def __init__(self, automato):
        super(EpsilonTransicao, self).__init__()

        self.Estados = automato.Estados
        self.Alfabeto = automato.Alfabeto
        self.Finais = automato.Finais

    def imprimir(self):
        return super().imprimir('\n\n# LIVRE DE EPSILON TRANSICOES:\n')


    def eliminarEpsilonTransicoes(self):
        self.buscarEpsilonTransicoes() 


    def buscarEpsilonTransicoes(self):        
        if super().EPSILON not in self.Alfabeto:
            return

        producoesComEpsilon = set()
        qtdEpsilon = len(producoesComEpsilon)
        qtdEstados = len(self.Estados) 
        idxEpsilon = self.Alfabeto
        i = 0

        while i < qtdEstados:   #percorre os estados
            if i in self.Estados and len(self.Estados[i][super().EPSILON]) > 0:   #verifica se tem epsilon
                self.removerEpsilonTransicoes(i, self.Estados[i][super().EPSILON][0], producoesComEpsilon)
                qtdEstados = len(self.Estados)                        #atualiza qtd de estados
            i += 1

        self.removerEpsilonTransicoesEstados()


    def removerEpsilonTransicoes(self, transicaoOriginal, transicaoEpsilon, producoesComEpsilon):
        if len(self.Estados[transicaoOriginal][self.EPSILON]) > 0:

            for producao in list(self.Estados[transicaoEpsilon]):
                if producao != self.EPSILON and len(self.Estados[transicaoEpsilon][producao]) > 0:                    
                    self.Estados[transicaoEpsilon][producao] = (list(set(self.Estados[transicaoEpsilon][producao] + self.Estados[transicaoOriginal][producao])))                    
                    producoesComEpsilon.update(set(self.Estados[transicaoOriginal][self.EPSILON]))                    
        
        if len(self.Estados[transicaoEpsilon][self.EPSILON]) > 0:            
            if self.Estados[transicaoEpsilon][self.EPSILON][0] not in producoesComEpsilon:
                self.removerEpsilonTransicoes(transicaoEpsilon, self.Estados[transicaoEpsilon][self.EPSILON][0], producoesComEpsilon)

    def removerEpsilonTransicoesEstados(self):
        if self.EPSILON not in self.Alfabeto:
            return

        qtdEstados = len(self.Estados) 
        i = 0
        while i < qtdEstados:            #percorre estados
            if i in self.Estados:            #verifica transição com epsilon
                self.Estados[i].pop(self.EPSILON)    #remove prod do ep
                qtdEstados = len(self.Estados)       #atualiza qtd estados
            i += 1

        self.Alfabeto.remove(self.EPSILON)

livreEpsilon = EpsilonTransicao(automato)           
livreEpsilon.eliminarEpsilonTransicoes()      #busca e trata a epsilon                         

############################## Determiniza ##############################
class Determinizacao(Automato):
    def __init__(self, automato):
        super(Determinizacao, self).__init__()

        self.Estados = automato.Estados
        self.Alfabeto = automato.Alfabeto
        self.Finais = automato.Finais
    
    def imprimir(self):     #chama a função imprimir da classe pai
        return super().imprimir('\n\n# DETERMINIZADO:\n')

    def determinizar(self):     #inicia a determinização
        self.buscarIndeterminismo() #busca indeterminismos

    def adicionaEstadoFinal(self, producoes, novaProducao): #add nova prod ao conjunto de estados finais
        for producao in producoes:          
            if producao in self.Finais:         #se é producão final
                self.Finais.add(novaProducao)   #add nova prod ao conjunto de finais

    def substituiNovaProducao(self):        #substitui um indeterminismo por string concatenando as transições
        if len(self.NovosEstados) > 0:                  #criadas novas prod na determinização
            for estado in self.Estados:                 #percorre estado do automato
                for simbolo in sorted(self.Alfabeto):          #percorre símbolos do alfabeto
                    if len(self.Estados[estado][simbolo]) > 1:       #se qtd de transições por uma prod for > 1
                        producaoAgrupada = self.geraProducaoAgrupada(self.Estados[estado][simbolo])     #gera uma prod agrupada para conhecer a origem da nova prod
                        if producaoAgrupada in self.NovosEstados:                                       #se essa prod estiver nas novas prod automato recebe a nova prod gerada
                            self.Estados[estado][simbolo] = [self.NovosEstados[producaoAgrupada][0]]    

    def buscarIndeterminismo(self):     #percorre o autômato tratando seus indeterminismos
        qtdEstados = len(self.Estados)   #marca a qtd inicial de estados
        i = 0              
        while i < qtdEstados:  
            for j in sorted(self.Alfabeto):     #percorre conjunto de símbolos do alfabeto
                if i in self.Estados and len(self.Estados[i][j]) > 1:       #se transição indeterminada:
                    self.determinizarProducao(self.Estados[i][j])           #determiniza  estado

                    qtdEstados = len(self.Estados)        #atualiza qtd de estados
            i += 1            

            if i == qtdEstados:     #se último estado
                for novoEstado in list(self.NovosEstados):          #percorre novas prod
                    if self.NovosEstados[novoEstado][0] not in self.Estados:            #se não estiver no conjunto de estados do automato
                        self.determinizarProducao(self.NovosEstados[novoEstado][1])     #determiniza
                        qtdEstados = len(self.Estados)      #atualiza qtd de estados                     

    def determinizarProducao(self, producoes):      #determiniza x estado do automato
        estadoTemporario = dict()
        producaoAgrupada = self.geraProducaoAgrupada(producoes)

        if ((producaoAgrupada not in self.NovosEstados) or (self.NovosEstados[producaoAgrupada][0] not in self.Estados)):  #se prod agrupada não existir nas novas prod ou nova regra não estiver no automato
            if (len(producoes) > 1) and (not self.existeProducaoAgrupada(producoes)):      #se tamanho for > 1 e não existe prod agrupada pra ela
                novoEstado = self.pegarNovoEstadoDetrminizacao()                              #pega o novo estado determinizado
                self.NovosEstados.update({self.geraProducaoAgrupada(producoes): [novoEstado,producoes]})    #coloca na estrutura de novos estados

            for i in producoes:             #percorre prod que contém indeterminação
                for j in sorted(self.Alfabeto):     #percorre conjunto de símbolos do alfabeto
                    if j in estadoTemporario:              #se símbolo j já estiver no estado temporário
                        lista = list(set(estadoTemporario[j] + self.pegarProducaoOriginal(self.Estados[i][j]))) #add a lista de transições de j
                        estadoTemporario[j] = lista        #ao estado criado

                        if (len(lista) > 1) and (not self.existeProducaoAgrupada(lista)):       #se largura da lista for > 1 e não existe prod agrupada pra ela
                            novoEstado = self.pegarNovoEstadoDetrminizacao()              #enumera novo estado
                            self.NovosEstados.update({self.geraProducaoAgrupada(lista): [novoEstado,lista]})    #add aos novos estados

                    else:        #se símbolo j não estiver no estado temporário
                        producaoAtual = list(set(self.Estados[i][j]))      #concatena as transições de j

                        if len(producaoAtual) > 1:           #se tiver mais de uma prod
                            producaoAgrupadaTemp = self.geraProducaoAgrupada(producaoAtual)                     #gera nova prod agrupada
                            if self.existeProducaoAgrupada(producaoAgrupadaTemp):                               #se essa prod já existe
                                estadoTemporario.update({j: list(set(self.NovosEstados[producaoAgrupada][1]))}) #atualiza o estado temporário

                        elif (len(producaoAtual) > 0) and (self.existeNovoEstado(producaoAtual[0])):     #se não se essa prod não for nula e existe um estado para essa transição
                            for prod in self.NovosEstados:              #percorre novos estados 
                                if self.NovosEstados[prod][0] == producaoAtual[0]:      #estado que for igual à transição
                                    estadoTemporario.update({j: list(set(self.NovosEstados[prod][1]))})      #atualiza
                        else:                                 
                            estadoTemporario.update({j: producaoAtual})    #add uma nova transição ao estado temporário

            self.setAlfabetoEstado(estadoTemporario);           #relaciona estado temporário com símbolos do alfabeto
            self.Estados.update({self.NovosEstados[producaoAgrupada][0]: estadoTemporario});     #add o estado temporário ao dict de estados da classe
            self.adicionaEstadoFinal(producoes, self.NovosEstados[producaoAgrupada][0])      #verifica se deve add aos estados finais
            self.substituiNovaProducao()     #verifica as prod criadas

    def geraProducaoAgrupada(self, lista):      #insere elementos de uma lista para uma string
        estado = ''
        for item in lista:      #para cada item da lista dada
            if estado == '':        #se for no inicio
                estado += str(item)     #concatena o item
            else:       #se for no meio
                estado += ',' + str(item)   #concatena com a virgula

        return estado                  

    def existeProducaoAgrupada(self, lista):        #verifica se lista dada já foi inserida em um estado novo
        retorno = False

        if len(lista) > 1:                                          #se o tamanho da lista dada for > 1
            producaoAgrupadaTemp = self.geraProducaoAgrupada(lista) #verifica pela sua possível prod agrupada
            return (producaoAgrupadaTemp in self.NovosEstados)
        else:         
            for i in self.NovosEstados:         #percorre os novos estados
                if lista[0] in self.NovosEstados[i][1]:       #verifica se a prod já existe
                    return True
        return retorno

    def pegarNovoEstadoDetrminizacao(self):     #add uma nova prod para contabilizar o novo tamanho do automato
        novasProducoes = []
        for producao in self.NovosEstados:      #pra cada prod dos novos estados
            novasProducoes.append(self.NovosEstados[producao][0])   #add um na contagem
        return len(set(list(self.Estados) + novasProducoes))     #retorna a qtd. Usa lista pra tratar repetições

    def pegarProducaoOriginal(self, producaoOrig):      #retorna a prod que está na lista de estados novos a partir de uma prod do automato
        retorno = list(set(producaoOrig))
        for producao in self.NovosEstados:
            for prod in producaoOrig:
                if self.NovosEstados[producao][0] == prod:
                    retorno = list(set(self.NovosEstados[producao][1]))

        return retorno

    def existeNovoEstado(self, producao):       #verifica se uma prod está no conjunto de novos estados
        if len(self.NovosEstados) > 0:
            for producaoAgrupada in self.NovosEstados:
                if self.NovosEstados[producaoAgrupada][0] == producao:
                    return True

        return False

determinizado = Determinizacao(automato) 
determinizado.determinizar()                   


############################## Elimina inalcançaveis ##############################
class Inalcancaveis(Inuteis):
    
    def __init__(self, automato):
        super(Inalcancaveis, self).__init__(automato)

    def imprimir(self):
        return super().imprimir('\n\n# SEM INALCANCAVEIS:\n')
          
    def removerInalcancaveis(self):
        estados = self.gerarEstadosParaMinimizacao()
        self.visitaNovaProducaoInalcancavel(estados, 0) #passa 0 fixo pois para remover os inalcançáveis parte do estado incial

    def visitaNovaProducaoInalcancavel(self, estados, transicao):
         if transicao in estados:
             if transicao in self.Finais:              #se a transição for um estado final
                 self.adicionaAutomatoMinimizado(transicao,-1,-1)        #add no automato pois pelo estado inicial o atual é alcançado

             for producao in estados[transicao]:                   #percorre todas as prod daquela transição e então segue com busca em profundidade
                if not estados[transicao][producao].temProducao():       #caso não tenha uma prod válida finaliza a recursão atual
                    continue
                if estados[transicao][producao].visitado:              #Se a prod já foi visitada finaliza a recursão atual
                    return
        
                estados[transicao][producao].visitado = True
                self.adicionaAutomatoMinimizado(transicao,producao,estados[transicao][producao].producao);  #add a prod no automato
                self.visitaNovaProducaoInalcancavel(estados, estados[transicao][producao].producao);     #busca recursivamente o estado final

semInalcancaveis = Inalcancaveis(automato)
semInalcancaveis.removerInalcancaveis()     


############################## Elimina mortos ##############################
class Mortos(Inuteis):
    
    def __init__(self, automato):
        super(Mortos, self).__init__(automato)
    
    def imprimir(self):
        return super().imprimir('#DETERMINIZADO, LIVRE DE EPSILON TRANSIÇÃO E LIVRE DE MORTOS E INALCANÇAVÉIS:\n')

    def removerMortos(self):
        estados = self.gerarEstadosParaMinimizacao()
        self.AutomatoMinimizado = dict()
        for transicao in estados:
            for producao in estados[transicao]:
                self.visitaNovaProducaoMortos(estados, transicao)
                estados[transicao][producao].chegouEstadoTerminal = self.adicionaAutomatoMinimizado(transicao,producao,estados[transicao][producao].producao)
    
    def visitaNovaProducaoMortos(self, estados, transicao):
        if transicao in estados:
            if (transicao in self.Finais) and (estados[transicao] == {}) :
                self.adicionaAutomatoMinimizado(transicao,-1,-1)
                return True

            for producao in estados[transicao]:
                if estados[transicao][producao].chegouEstadoTerminal or (transicao in self.Finais):
                    return True
                if not estados[transicao][producao].temProducao():      
                    return False
                if estados[transicao][producao].visitado:
                    continue
                
            estados[transicao][producao].visitado = True
            if self.visitaNovaProducaoMortos(estados, estados[transicao][producao].producao):
                estados[transicao][producao].chegouEstadoTerminal = True
                self.adicionaAutomatoMinimizado(transicao,producao,estados[transicao][producao].producao)
                return True

        return False


semMortos = Mortos(semInalcancaveis)      
semMortos.removerMortos()                 
semMortos.imprimir()

############################## Analise Léxica / Sintática ##############################
class Analise(Inuteis):
    def __init__(self, automato):
        super(Analise, self).__init__(automato)

    def imprimir(self):
        return super().imprimir('#DETERMINIZADO, LIVRE DE EPSILON TRANSIÇÃO E LIVRE DE MORTOS E INALCANÇAVÉIS:\n')

    def analisador_lexico_sintatico(self):
        tabela = self.pegarAutomato()
        fitaS = [] 
        Ts = []    
        codigoFonte = list(open('codigo.txt'))
        separador = [' ', '\n', '\t']
        palavra = ''
        count = 0
        estado = 0
        for linha in codigoFonte:
            count += 1
            for caracter in linha:
                if caracter in separador and palavra:
                    Ts.append({'Linha': str(count), 'Estado': str(estado), 'Rotulo': palavra.strip('\n')})
                    # fitaS.append(estado) //alterado para append após o mapeamento da GLC.xml
                    estado = 0
                    palavra = ''
                else:    
                    try:
                        estado = tabela[estado][caracter][0]
                    except KeyError:
                        estado = -1
                    if caracter != ' ':
                        palavra += caracter

        xml_parser = "GLC.xml"
        tree = ET.parse(xml_parser)
        root = tree.getroot()
        for symbol in root.iter('Symbol'):
            for x in Ts:
                if x['Rotulo'] == symbol.attrib['Name']:
                    x['Estado'] = symbol.attrib['Index'] 
                elif x['Rotulo'][0] == '.' and x['Rotulo'][-1] == '.' and symbol.attrib['Name'] == '.name.':
                    x['Estado'] = symbol.attrib['Index']
                elif x['Rotulo'][0] == '0' and symbol.attrib['Name'] == '0constant':
                    x['Estado'] = symbol.attrib['Index']  

        print("\n")
        for x in Ts:
            fitaS.append(x['Estado'])
            print(x)
        print("\n Fita de saída:", fitaS, "\n")

        for erro in Ts:
            if erro['Estado'] == '-1':
                print('Erro Léxico: linha "{}", erro "{}"' .format(erro['Linha'], erro['Rotulo']))

        # fitaS -> fita de saída com os tokens/estados que reconhecem
        # pilha -> vetor que inicia em 0 (guarda as ações e desempilha)

        pilha = []
        pilha.append(0)
        for fita in fitaS:
            for linha in root.iter('LALRState'):    
                if linha.attrib['Index'] == str(pilha[-1]):
                    for coluna in linha:
                        if coluna.attrib['SymbolIndex'] == fita:
                            pilha.append(fita)
                            pilha.append(coluna.attrib['Value'])
            break
        print(pilha)

analise = Analise(semInalcancaveis)
analise.analisador_lexico_sintatico()