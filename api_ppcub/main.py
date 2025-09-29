from fastapi import FastAPI, HTTPException, Query
import models, queries
from typing import Optional

app = FastAPI(
    title="API de Análise de Viabilidade",
    description="Consulta a viabilidade de atividades econômicas em lotes da cidade.",
    version="1.0.0"
)

@app.get(
    "/api/viabilidade",
    response_model=models.ViabilidadeResponse,
    tags=["Análise de Viabilidade"]
)
def consultar_viabilidade(
    cep: str = Query(..., min_length=8, max_length=9, regex=r"^\d{5}-?\d{3}$", description="CEP do lote no formato XXXXX-XXX ou XXXXXXXX")
):
    """
    Retorna uma lista de endereços para um CEP específico, com todas as 
    atividades permitidas e suas respectivas restrições e notas.
    """
    try:
        dados = queries.get_viabilidade_por_cep(cep.replace("-", ""))
        if not dados["enderecos"]:
            raise HTTPException(status_code=404, detail="Nenhum endereço encontrado para o CEP informado.")
        return dados
    except Exception as e:
        # Em um cenário real, você faria um log do erro `e`
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor.")