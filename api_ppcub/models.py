from pydantic import BaseModel
from typing import List, Optional

# Usamos Optional se um campo pode ser nulo (null)

class AtividadePermitida(BaseModel):
    cod_atividade: Optional[str] = None
    descricao_atividade: Optional[str] = None # Supondo que você tenha uma descrição
    #resultado: str
    uso_purp: str
    restricao_uso: Optional[str] = None
    notas_gerais: List[str] = []
    notas_especificas: List[str] = []
    observacao: Optional[str] = None

class Endereco(BaseModel):
    endereco_completo: str
    cipu: int
    ciu: str
    cep: str
    pn_uso: str
    atividades_permitidas: List[AtividadePermitida] = []

class ViabilidadeResponse(BaseModel):
    enderecos: List[Endereco]