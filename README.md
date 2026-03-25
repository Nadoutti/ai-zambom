# API de Pagamentos

API simples para gerenciamento de pagamentos usando Flask e MongoDB.

## Requisitos

- Python 3.x
- MongoDB rodando localmente na porta 27017

## Instalação

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Executar a API

```bash
python main.py
```

A API estará disponível em `http://localhost:5000`

## Rotas

### 1. GET /pagamento

Lista todos os pagamentos cadastrados. Opcionalmente filtra por cliente_id.

**Parâmetros opcionais:**
- `cliente_id` (query parameter)

**Exemplos:**

```bash
# Listar todos os pagamentos
curl http://localhost:5000/pagamento

# Listar pagamentos de um cliente específico
curl http://localhost:5000/pagamento?cliente_id=123
```

**Resposta de sucesso (200):**
```json
{
  "success": true,
  "data": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "cliente_id": "123",
      "codigo_pagamento": "PAG001",
      "valor_total": 1000.0,
      "tipo_pagamento": "Credito",
      "numero_parcelas": 10,
      "valor_parcela": 100.0,
      "data_pagamento": "2026-03-25T12:00:00",
      "criado_em": "2026-03-25T12:00:00"
    }
  ],
  "total": 1
}
```

### 2. POST /pagamento

Cria um novo pagamento.

**Body (JSON):**
```json
{
  "cliente_id": "123",
  "codigo_pagamento": "PAG001",
  "valor_total": 1000.0,
  "tipo_pagamento": "Credito",
  "numero_parcelas": 10,
  "data_pagamento": "2026-03-25T12:00:00"
}
```

**Campos obrigatórios:**
- `cliente_id`: ID do cliente que fez o pagamento
- `codigo_pagamento`: Código único do pagamento
- `valor_total`: Valor total do pagamento
- `tipo_pagamento`: "PIX" ou "Credito"
- `numero_parcelas`: Número de parcelas

**Campos opcionais:**
- `data_pagamento`: Data do pagamento (padrão: data/hora atual)

**Nota:** O campo `valor_parcela` é calculado automaticamente no backend.

**Exemplo:**

```bash
curl -X POST http://localhost:5000/pagamento \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "123",
    "codigo_pagamento": "PAG001",
    "valor_total": 1000.0,
    "tipo_pagamento": "Credito",
    "numero_parcelas": 10
  }'
```

**Resposta de sucesso (201):**
```json
{
  "success": true,
  "message": "Pagamento criado com sucesso",
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "cliente_id": "123",
    "codigo_pagamento": "PAG001",
    "valor_total": 1000.0,
    "tipo_pagamento": "Credito",
    "numero_parcelas": 10,
    "valor_parcela": 100.0,
    "data_pagamento": "2026-03-25T12:00:00",
    "criado_em": "2026-03-25T12:00:00"
  }
}
```

### 3. DELETE /pagamento/{id}

Deleta um pagamento pelo ID.

**Parâmetros:**
- `id`: ID do pagamento (path parameter)

**Exemplo:**

```bash
curl -X DELETE http://localhost:5000/pagamento/507f1f77bcf86cd799439011
```

**Resposta de sucesso (200):**
```json
{
  "success": true,
  "message": "Pagamento deletado com sucesso"
}
```

**Resposta de erro (404):**
```json
{
  "success": false,
  "error": "Pagamento não encontrado"
}
```

## Estrutura do Banco de Dados

**Database:** `pagamentos_db`

**Collection:** `pagamentos`

**Campos:**
- `_id`: ObjectId (MongoDB)
- `cliente_id`: String
- `codigo_pagamento`: String
- `valor_total`: Float
- `tipo_pagamento`: String ("PIX" ou "Credito")
- `numero_parcelas`: Integer
- `valor_parcela`: Float (calculado)
- `data_pagamento`: String (ISO 8601)
- `criado_em`: String (ISO 8601)

## Notas

- Certifique-se de que o MongoDB está rodando antes de iniciar a API
- O valor da parcela é calculado automaticamente: `valor_total / numero_parcelas`
- Todos os endpoints retornam JSON
- Erros são retornados com status HTTP apropriado e mensagem de erro
