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
                with busca_atividades as (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY lr.pu_cipu) AS id,
                    cast(lr.pu_cipu as int) as cipu,
                    lr.pu_ciu as ciu,
                    lr.pu_cep as cep,
                    lr.pu_end_cart as endereco_cartorial,
                    lr.pu_end_usual as endereco_usual,
                    lr.pn_cod_par as codigo_parametro,
                    lr.pn_uso as uso,
                    aii.ppcub_cod_subclasse as codigo_subclasse,
                    aii.ppcub_subclasse as subclasse,
                    Null as endereco_purp,
                    aii.ppcub_uso as uso_atividade,
                    CASE 
                        WHEN aii.ppcub_uso LIKE '%(%' THEN
                            TRIM(BOTH ' ' FROM 
                                (REGEXP_MATCH(aii.ppcub_uso, '\((.*)\)'))[1]
                            )
                        ELSE NULL 
                    END AS restricao_uso_atividade,
                    Null as cod_nota_geral,
                    Null as nota_geral,
                    Null as cod_nota_especifica,
                    Null as nota_especifica,
                    'É necessário atender ao número de vagas definido na legislação' as observacao
                from app_fdw_user.view_mat_lote_registrado as lr
                    inner join app_fdw_user.view_mat_tb_ppcub_dec_46414_24_anexo_ii_uos_tp11 as aii on aii.ppcub_uos = lr.pn_uso
                    where lr.pu_cep = %s
                union all
                select
                    ROW_NUMBER() OVER (ORDER BY lr.pu_cipu) AS id,
                    cast(lr.pu_cipu as int) as cipu,
                    lr.pu_ciu as ciu,
                    lr.pu_cep as cep,
                    lr.pu_end_cart as endereco_cartorial,
                    lr.pu_end_usual as endereco_usual,
                    lr.pn_cod_par as codigo_parametro,
                    lr.pn_uso as uso,
                    du.ppcub_cod_subclasse as codigo_subclasse,
                    du.ppcub_subclasse as subclasse,
                    du.ppcub_end_purp as endereco_purp,
                    du.ppcub_uso_purp as uso_atividade,
                    CASE 
                        WHEN du.ppcub_uso_purp LIKE '%(%' THEN
                            TRIM(BOTH ' ' FROM 
                                (REGEXP_MATCH(du.ppcub_uso_purp, '\((.*)\)'))[1]
                            )
                        ELSE NULL 
                    END AS restricao_uso_atividade,
                    ng.ng_codigo as cod_nota_geral,
                    ng.ng_descricao as nota_geral,
                    ne.ne_codigo as cod_nota_especifica,
                    ne.ne_descricao as nota_especifica,
                    'É necessário atender ao número de vagas definido na legislação' AS observacao
                from app_fdw_user.view_mat_lote_registrado as lr
                    inner join app_fdw_user.view_mat_tb_ppcub_dec_46414_24_anexo_i_usos as du on du.ppcub_cod_itemb = lr.pn_uso
                    left join app_fdw_user.view_mat_tb_ppcub_purp_notas_gerais as ng on ng.ng_tpup = du.ppcub_tpup
                    left join app_fdw_user.view_mat_tb_ppcub_rel_uso_nota_especifica as ue on ue.une_cod_itemb = du.ppcub_cod_itemb
                    left join app_fdw_user.view_mat_tb_ppcub_purp_notas_especificas as ne on ne.ne_codigo = ue.une_cod_nota_especifica
                    where lr.pu_cep = %s
                union all
                SELECT
                    ROW_NUMBER() OVER (ORDER BY lr.pu_cipu) AS id,
                    cast(lr.pu_cipu as int) as cipu,
                    lr.pu_ciu as ciu,
                    lr.pu_cep as cep,
                    lr.pu_end_cart as endereco_cartorial,
                    lr.pu_end_usual as endereco_usual,
                    lr.pn_cod_par as codigo_parametro,
                    lr.pn_uso as uso,
                    la.cod_subclasse as codigo_subclasse,
                    la.subclasse as subclasse,
                    Null as endereco_purp,
                    la.uso_atividade as uso_atividade,
                    CASE 
                        WHEN la.uso_atividade LIKE '%(%' THEN
                            TRIM(BOTH ' ' FROM 
                                (REGEXP_MATCH(la.uso_atividade, '\((.*)\)'))[1]
                            )
                        ELSE NULL 
                    END AS restricao_uso_atividade,
                    Null as cod_nota_geral,
                    Null as nota_geral,
                    la.cod_nota_ln as cod_nota_especifica,
                    la.nota_especifica as nota_especifica,
                    'É necessário atender ao número de vagas definido na legislação' as observacao
                from app_fdw_user.view_mat_lote_registrado as lr
                    inner join app_fdw_user.view_tb_luos_atividades_notas as la on la.uos = lr.pn_uso
                    where lr.pu_cep = %s
                )
                select *
                from busca_atividades
            """
            cur.execute(sql_query, (cep,))
            rows = cur.fetchall()

            for row in rows:
                (
                    end_completo, cipu, ciu, cep, pn_uso, cod_ativ, atividade, uso_purp, restricao, nota_g, nota_e, observacao
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
                        #"resultado": "Aprovado com Observações" if any([restricao, nota_g, nota_e]) else "Aprovado",
                        "uso_purp": uso_purp,
                        "restricao_uso": restricao,
                        "notas_gerais": [],
                        "notas_especificas": [],
                        "observação": observacao
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