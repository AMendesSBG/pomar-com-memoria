# Pomar com Memória

Aplicação em Python e Streamlit para acompanhar árvores de fruto. Nasceu de uma necessidade real: gerir um pomar com cerca de 50 árvores e consultar, por árvore, o que foi feito e quando surgiram problemas.

[Experimentar a demo do Pomar com Memória](https://pomar-com-memoria.streamlit.app/)

## O que podes fazer

- Adicionar árvores com código, espécie e variedade.
- Registar colheitas e filtrar o histórico de intervenções por podas e colheitas.
- Registar sintomas com data, mesmo quando a causa ainda é desconhecida.
- Consultar fichas ilustradas de pedrado da macieira, fogo bacteriano e mancha foliar da cerejeira. As fichas incluem fotografias e referências da University of Minnesota Extension.
- Associar manualmente uma doença a uma ocorrência, fechar o episódio e consultar o histórico. A mesma doença pode voltar a ser registada depois do fecho.

## Percurso da demonstração

1. Em **Pomar**, abre a ficha da macieira **M-01** e escolhe **Saúde**. Há um exemplo ativo de pedrado.
2. Abre **Registar sintomas** e escreve «Rebentos com a ponta encurvada». A nova ocorrência fica **Em dúvida**.
3. Abre **Biblioteca de doenças** na barra lateral e filtra por **Macieira** para comparar as fichas. Regressa a **Pomar → Saúde**, abre **Confirmar doença** e escolhe **Fogo bacteriano** para este cenário fictício.
4. Usa **Fechar ocorrência**, guarda a data e consulta o resultado em **Fechadas**.
5. Na secção **Histórico**, tenta registar uma colheita com **-5 kg**. Corrige para **5,5 kg** e confirma que a colheita aparece no histórico.

## Executar localmente

Requer Python 3.12. Na pasta do projeto, executa:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Por omissão, a aplicação funciona em **modo demonstração**. Cada sessão começa com três árvores fictícias e mantém os registos durante essa sessão.

Para usar um **pomar próprio**, pára a aplicação e executa no PowerShell:

```powershell
$env:POMAR_DB_PATH = "dados/pomar.sqlite3"
python -m streamlit run app.py --server.address localhost
```

Em Bash, usa `POMAR_DB_PATH=dados/pomar.sqlite3 python -m streamlit run app.py --server.address localhost`. A primeira execução cria uma base de dados vazia. Usa **Adicionar árvore** para começar. Mantém o mesmo caminho nas execuções seguintes para recuperar os registos. Para fazer uma cópia de segurança, fecha a aplicação e copia o ficheiro SQLite. Mantém a demo pública em modo demonstração, já que o modo persistente local não tem autenticação.

As fotografias de referência são carregadas a partir das páginas dos autores e precisam de ligação à Internet. As descrições e os registos continuam acessíveis localmente.

## Decisões de implementação

- A ficha de doença descreve a referência e as espécies abrangidas. A ocorrência guarda o episódio e o contexto de uma árvore.
- Um caso pode ficar em dúvida ou ser fechado sem identificação. Depois da confirmação, a base de dados impede duas ocorrências ativas da mesma doença na mesma árvore.
- `pomar.py` contém o núcleo académico e os contratos das intervenções. `armazenamento.py` implementa o mesmo contrato de armazenamento para integrar as colheitas existentes com SQLite. `doencas.py` contém as fichas de referência e `saude_ui.py` apresenta os fluxos de saúde.
- O núcleo original foi desenvolvido na unidade curricular de Programação por Objetos da Universidade Aberta. A interface e esta extensão foram desenvolvidas com assistência do ChatGPT.

## Testes

```powershell
python -m unittest discover -v
```

Os testes cobrem a validação de intervenções, a importação, o isolamento por árvore, as datas de fecho, a recorrência e a persistência.
