import os
import sys
import time
from selenium import webdriver
from word2number import w2n

try:

    # Pega o caminho atual de onde o arquivo esta sendo executado
    currentPath = os.getcwd()

    # Abre um arquivo que a saída do robô será escreita (caso use linux, trocar o \\ por /)
    file = open("{}\\saida.txt".format(currentPath), "w", encoding="utf8")

    # Cria as variáveis que irão armazenar os gêneros enviados pelo usuário e a nota mínima dos livros que ele deseja buscar
    inputCategory = []
    inputRating = 0

    # Recebe as informações dos usuários
    inputCategory = input("Digite os genêros separados por uma vírgula: ")

    # Realiza um loop infinito até que a resposta inserida pelo usuário seja um número inteiro
    while True:
        try:
            inputRating = int(
                input(
                    "Digite a quantidade de estrelas da classificação do livro (1 a 5): "
                )
            )

            # Verifica se o número de estrelas enviado pelo usuário é menor ou igual à cinco, o limite de estrelas do site
            if inputRating <= 5 and inputRating >= 0:
                break
            else:
                print("Número de estrelas inexistente")
                continue
        except:
            print("Digite um número inteiro")

    # Realiza tratativas para utilizar as informações enviadas pelos usuários
    CategoryList = inputCategory.split(",")

    # O map faz com que todos os termos da lista tenham seus espaços adicionais excluídos
    CategoryList = map(str.strip, CategoryList)

    # Abre o chromedriver, que está na pasta atual de execução do código e a variável driver recebe as funções do selenium
    driver = webdriver.Chrome("{}\\chromedriver.exe".format(currentPath))

    # Abre o site desejado
    driver.get("http://books.toscrape.com/index.html")

    # Realiza um loop para todas as categorias digitadas pelo usuário
    for vCategory in CategoryList:

        # Inicia o contador que irá percorrer todos os livros de cada página
        elementCounter = 1

        # Verifica se o gênero atual do loop, digitado pelo usuário, exista na página web
        currentCategory = driver.find_elements_by_xpath(
            '//a[translate(normalize-space(.), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz") = "{}"]'.format(
                vCategory.lower()
            )
        )

        # Valida se a categoria digitada pelo usuário existe
        # Caso o gênero não exista, uma mensagem falando que o gênero não existe é exibida no cmd e a validação do próximo é feita
        if not currentCategory:
            print("Gênero {} não existe, continuando para o próximo".format(vCategory))
            continue
        # Se o gênero existir, o script irá clicar no gênero e abrir a página referente à ele
        else:
            driver.find_element_by_xpath(
                '//a[translate(normalize-space(.), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz") = "{}"]'.format(
                    vCategory.lower()
                )
            ).click()

            # Entra em loop infinito, que permite que o robô passe por todos os livros de todos os gêneros, até que sejam finalizados
            while True:

                # Coleta as informações dos livros, de acordo com o contador do elemento
                livro = driver.find_elements_by_xpath(
                    '//div[@class="col-sm-8 col-md-9"]/section/div[2]/ol/li[{}]'.format(
                        elementCounter
                    )
                )

                # A linha anterior retorna uma lista. Caso essa lista exista, quer dizer que o elemento existe e ele deve ser validado
                if livro:

                    # Busca o elemento do livro que possui a classificação
                    starNumberElement = driver.find_element_by_xpath(
                        '//div[@class="col-sm-8 col-md-9"]/section/div[2]/ol/li[{}]/article/p'.format(
                            elementCounter
                        )
                    )
                    # Busca o atributo classe desse elemento, que possui a classificação do livro
                    starNumberCount = starNumberElement.get_attribute("class").replace(
                        "star-rating ", ""
                    )

                    # Utiliza a biblioteca word2number para converter a classificação por extenso do site para um número e comparar com o input do usuário do SAP
                    if w2n.word_to_num(starNumberCount) >= inputRating:

                        # Caso a classicação do livro seja igual ou maior que a informada pelo usuário, o robô coleta o titulo da obra através do atributo título do elemento
                        bookTitle = driver.find_element_by_xpath(
                            '//div[@class="col-sm-8 col-md-9"]/section/div[2]/ol/li[{}]/article/h3/a'.format(
                                elementCounter
                            )
                        )
                        bookTitle = bookTitle.get_attribute("title")

                        # Escreve no arquivo de saída o título do livro e sua nota
                        file.write(
                            "Gênero: {} | Título: {} | Nota: {}\n".format(
                                vCategory, bookTitle, starNumberCount
                            )
                        )

                        # Aumenta o contador e vai para o próximo registro
                        elementCounter += 1
                    else:
                        # Caso o valor da nota do livro seja menor que a pedida pela usuário, vai para o próximo livro
                        elementCounter += 1

                # Caso o elemento do livro não exista, ele verifica se existe um botão para ir para a próxima página do gênero
                else:
                    # Caso o botão exista, clica no botão e reseta o contador de elementos
                    nextButton = driver.find_elements_by_xpath('//li[@class="next"]')

                    if nextButton:
                        driver.find_element_by_xpath('//li[@class="next"]/a').click()

                        elementCounter = 1

                    # Caso o botão não exista, finaliza o while e vai para o próximo gênero digitado
                    else:
                        break

        time.sleep(5)

    # Fecha o navegador do selenium
    driver.close()

    # Fecha o arquivo criado para escrever o resultado
    file.close()

    # Printa uma mensagem de finalização
    print("\nProcesso finalizado")

except Exception as e:
    trace_back = sys.exc_info()[2]
    line = trace_back.tb_lineno
    print("Process Exception in line {}".format(line), e)
    sys.exit(0)