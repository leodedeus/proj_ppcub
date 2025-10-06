from database import get_db_connection
from typing import Dict, Any

def get_viabilidade_por_cep(cep: str) -> Dict[str, Any]:
    """
    Consulta a view no banco e estrutura os dados por endereço e atividade.
    """
    conn = get_db_connection()
    if not conn:
        return {"enderecos": []}

    # Dicionário para ajudar a montar a estrutura aninhada
    enderecos_map = {}

    try:
        with conn.cursor() as cur:
            # Substitua vw_viabilidade_atividade pelo nome real da sua view
            # e os nomes das colunas pelos nomes corretos na sua view
            sql_query = """
                select * from ppcub.busca_atividades_por_cep(%s)
            """
            cur.execute(sql_query, (cep,))
            rows = cur.fetchall()

            for row in rows:
                (
                    id,
                    cipu,
                    ciu,
                    cep,
                    endereco_cartorial,
                    endereco_usual,
                    codigo_parametro,
                    uso,
                    codigo_subclasse,
                    subclasse,
                    endereco_purp,
                    uso_atividade,
                    restricao_uso_atividade,
                    cod_nota_geral,
                    nota_geral,
                    cod_nota_especifica,
                    nota_especifica,
                    observacao
                ) = row

                # Se for a primeira vez que vemos este endereço, cria a estrutura base
                if endereco_cartorial not in enderecos_map:
                    enderecos_map[endereco_cartorial] = {
                        "endereco_completo": endereco_cartorial,
                        "cipu": cipu,
                        "ciu": ciu,
                        "cep": cep,
                        "pn_uso": uso,
                        "atividades_permitidas": {} # Usamos um dict para facilitar a busca por atividade
                    }

                # Atalho para o dicionário de atividades do endereço atual
                atividades_do_endereco = enderecos_map[endereco_cartorial]["atividades_permitidas"]

                # Se for a primeira vez que vemos esta atividade neste endereço
                if codigo_subclasse not in atividades_do_endereco:
                    atividades_do_endereco[codigo_subclasse] = {
                        "cod_atividade": codigo_subclasse,
                        "descricao_atividade": subclasse,
                        "uso_purp": uso_atividade,
                        "restricao_uso": restricao_uso_atividade,
                        "notas_gerais": [nota_geral] if nota_geral else [],
                        "notas_especificas": [nota_especifica] if nota_especifica else [],
                        "observacao": observacao
                    }
                
                # Adiciona as notas, evitando duplicatas
                if nota_geral and nota_geral not in atividades_do_endereco[codigo_subclasse]["notas_gerais"]:
                    atividades_do_endereco[codigo_subclasse]["notas_gerais"].append(nota_geral)
                
                if nota_especifica and nota_especifica not in atividades_do_endereco[codigo_subclasse]["notas_especificas"]:
                    atividades_do_endereco[codigo_subclasse]["notas_especificas"].append(nota_especifica)

    finally:
        conn.close()

    # Agora, formatamos o resultado final para corresponder ao nosso modelo Pydantic
    resultado_final = {"enderecos": []}
    for end_data in enderecos_map.values():
        # Converte o dicionário de atividades em uma lista
        end_data["atividades_permitidas"] = list(end_data["atividades_permitidas"].values())
        resultado_final["enderecos"].append(end_data)

    return resultado_final