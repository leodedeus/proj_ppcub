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
                SELECT
                    endereco_cartorial,
                    cipu,
                    ciu,
                    cep,
                    uso,
                    codigo_subclasse,
                    subclasse,
                    restricao_uso_purp,
                    nota_geral,
                    nota_especifica
                FROM
                    ppcub.ppcub_busca_atividade
                WHERE
                    cep = %s
                ORDER BY endereco_cartorial, codigo_subclasse, nota_geral, nota_especifica;
            """
            cur.execute(sql_query, (cep,))
            rows = cur.fetchall()

            for row in rows:
                (
                    end_completo, cipu, ciu, cep, pn_uso, cod_ativ, atividade, restricao, nota_g, nota_e
                ) = row

                # Se for a primeira vez que vemos este endereço, cria a estrutura base
                if end_completo not in enderecos_map:
                    enderecos_map[end_completo] = {
                        "endereco_completo": end_completo,
                        "cipu": cipu,
                        "ciu": ciu,
                        "cep": cep,
                        "pn_uso": pn_uso,
                        "atividades_permitidas": {} # Usamos um dict para facilitar a busca por atividade
                    }

                # Atalho para o dicionário de atividades do endereço atual
                atividades_do_endereco = enderecos_map[end_completo]["atividades_permitidas"]

                # Se for a primeira vez que vemos esta atividade neste endereço
                if cod_ativ not in atividades_do_endereco:
                    atividades_do_endereco[cod_ativ] = {
                        "cod_atividade": cod_ativ,
                        "descricao_atividade": atividade,
                        "resultado": "Aprovado com Observações" if any([restricao, nota_g, nota_e]) else "Aprovado",
                        "restricao_uso": restricao,
                        "notas_gerais": [],
                        "notas_especificas": []
                    }
                
                # Adiciona as notas, evitando duplicatas
                if nota_g and nota_g not in atividades_do_endereco[cod_ativ]["notas_gerais"]:
                    atividades_do_endereco[cod_ativ]["notas_gerais"].append(nota_g)
                
                if nota_e and nota_e not in atividades_do_endereco[cod_ativ]["notas_especificas"]:
                    atividades_do_endereco[cod_ativ]["notas_especificas"].append(nota_e)

    finally:
        conn.close()

    # Agora, formatamos o resultado final para corresponder ao nosso modelo Pydantic
    resultado_final = {"enderecos": []}
    for end_data in enderecos_map.values():
        # Converte o dicionário de atividades em uma lista
        end_data["atividades_permitidas"] = list(end_data["atividades_permitidas"].values())
        resultado_final["enderecos"].append(end_data)

    return resultado_final