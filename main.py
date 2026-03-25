import os
from datetime import datetime

import requests
from bson.objectid import ObjectId
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

app = Flask(__name__)

MONGO_HOST = os.getenv("MONGO_HOST", "mongo-connections")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
app.config["MONGO_URI"] = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/pagamentos_db"
mongo = PyMongo(app)


# Helper para converter ObjectId em string
def serialize_pagamento(pagamento):
    pagamento["_id"] = str(pagamento["_id"])
    return pagamento


def validar_cliente(cliente_id):
    """Valida se o cliente existe na API externa"""
    try:
        url = f"http://18.228.48.67/users/{cliente_id}"
        response = requests.get(url, timeout=5)

        if response.status_code == 404:
            return False, "Cliente não encontrado"
        elif response.status_code == 200:
            return True, None
        else:
            return False, f"Erro ao validar cliente: status {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout ao validar cliente"
    except requests.exceptions.ConnectionError:
        return False, "Erro de conexão ao validar cliente"


@app.route("/pagamento", methods=["GET"])
def listar_pagamentos():
    """Lista todos os pagamentos ou filtra por cliente_id"""
    cliente_id = request.args.get("cliente_id")

    try:
        if cliente_id:
            # Filtra por cliente_id
            pagamentos = list(mongo.db.pagamentos.find({"cliente_id": cliente_id}))
        else:
            # Lista todos os pagamentos
            pagamentos = list(mongo.db.pagamentos.find())

        # Serializa os pagamentos
        pagamentos_serializados = [serialize_pagamento(p) for p in pagamentos]

        return jsonify(
            {
                "success": True,
                "data": pagamentos_serializados,
                "total": len(pagamentos_serializados),
            }
        ), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/pagamento/<string:pagamento_id>", methods=["DELETE"])
def deletar_pagamento(pagamento_id):
    """Deleta um pagamento pelo ID"""
    try:
        # Verifica se o ID é válido
        if not ObjectId.is_valid(pagamento_id):
            return jsonify({"success": False, "error": "ID inválido"}), 400

        # Tenta deletar o pagamento
        resultado = mongo.db.pagamentos.delete_one({"_id": ObjectId(pagamento_id)})

        if resultado.deleted_count == 0:
            return jsonify({"success": False, "error": "Pagamento não encontrado"}), 404

        return jsonify(
            {"success": True, "message": "Pagamento deletado com sucesso"}
        ), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/pagamento", methods=["POST"])
def criar_pagamento():
    """Cria um novo pagamento"""
    try:
        dados = request.get_json()

        # Validação dos campos obrigatórios
        campos_obrigatorios = [
            "cliente_id",
            "email_cliente",
            "valor_totaltipo_pagamento",
        ]
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify(
                    {"success": False, "error": f"Campo obrigatório ausente: {campo}"}
                ), 400

        # Cria o objeto de pagamento
        pagamento = {
            "cliente_id": dados["cliente_id"],
            "valor_total": dados["valor_total"],
            "email_cliente": dados["email_cliente"],
            "data_pagamento": dados.get("data_pagamento", datetime.now().isoformat()),
            "criado_em": datetime.now().isoformat(),
        }

        # Insere no banco de dados
        resultado = mongo.db.pagamentos.insert_one(pagamento)
        pagamento["_id"] = str(resultado.inserted_id)

        return jsonify(
            {
                "success": True,
                "message": "Pagamento criado com sucesso",
                "data": pagamento,
            }
        ), 201

    except ValueError as e:
        return jsonify(
            {
                "success": False,
                "error": "Valores inválidos para valor_total ou numero_parcelas",
            }
        ), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
