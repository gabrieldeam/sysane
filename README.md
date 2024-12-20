# Sysane Project

## Descrição
Sysane é um projeto de API RESTful com frontend em Next.js e backend em FastAPI, integrado ao PostgreSQL.

## Estrutura
- **server/**: Backend em FastAPI.
- **client/**: Frontend em Next.js.

## Instalação

### Backend
1. Ative o ambiente virtual:
   ```bash
   cd server
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

2. Instale as dependências:   
   pip install -r requirements.txt

3. Configure o banco no arquivo .env.

4. Execute:
   uvicorn app.main:app --reload



### Frontend
1. Instale as dependências:
   ```bash
   cd client
   npm install

2. Execute:
   npm run dev
