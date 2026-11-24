# HortaSense — apresentação em Streamlit

## Arquivos
- `app.py`: aplicação Streamlit.
- `base_hortinha.csv`: base de dados utilizada nos gráficos.
- `requirements.txt`: dependências.

## Executar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar no Streamlit Community Cloud
1. Crie um repositório no GitHub.
2. Envie os três arquivos deste projeto para a raiz do repositório.
3. Entre em https://share.streamlit.io/ e conecte sua conta GitHub.
4. Selecione o repositório, a branch e o arquivo `app.py`.
5. Clique em Deploy.

A aplicação usa o CSV fornecido para exibir os registros. A seção Banco de dados explica o fluxo de importação para PostgreSQL; a aplicação não acessa diretamente o servidor do IESB.
