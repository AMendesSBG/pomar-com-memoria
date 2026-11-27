# Pomar com Memória

Uma aplicação para registar colheitas e consultar o histórico de cada árvore. O projeto nasceu de uma necessidade real: acompanhar um pomar com cerca de 50 árvores sem depender da memória para recordar o que foi feito e quando.

**[Experimentar a demo do Pomar com Memória](https://pomar-com-memoria.streamlit.app/)**

## Experimentar

1. Abre a ficha da macieira **M-01** e escolhe **Registar colheita**.
2. Introduz **-5** no peso e tenta guardar. A interface explica como corrigir o campo e conserva o que preencheste.
3. Corrige para **5,5** e guarda. A nova colheita aparece no histórico. Usa **Podas** ou **Colheitas** para filtrar os registos.

## Decisões de design

- **Começar pela árvore.** Os mockups da unidade curricular de Programação por Objetos já organizavam a navegação por árvore. A demo mantém essa estrutura e concentra-se nas colheitas.
- **Corrigir no mesmo sítio.** A mensagem surge junto ao peso, onde o utilizador pode corrigir o valor sem voltar a escolher a data.
- **Mostrar onde ficou guardado.** Depois da gravação, a interface fecha o formulário, mostra uma confirmação e repõe o filtro em **Todas** para que o novo registo fique visível.

## Implementação e IA

O núcleo Python vem do trabalho de Programação por Objetos da Universidade Aberta. A interface web foi desenvolvida com assistência do ChatGPT, a partir dos fluxos e regras do protótipo académico. A interface chama o código Python para validar o peso, guardar colheitas e consultar o histórico. Foram testados o preenchimento inválido, a correção, a gravação, a filtragem e a navegação entre árvores.

A demo inclui três árvores fictícias. Cada sessão começa com os dados de exemplo e conserva as alterações enquanto estiver ativa.

## Executar localmente

Com Python 3.12, abre um terminal nesta pasta:

```text
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Para executar os 15 testes do núcleo:

```text
python -m unittest discover -v
```
