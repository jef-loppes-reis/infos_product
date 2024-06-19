SELECT produto.produto as titulo,
    produto.codpro as codigo_interno,
    produto.codpro as sku,
	produto.fantasia as marca,
    tb_multiplo.multiplo,
    ROUND(tb_prd_tipo.p_venda * 1.35504, 2) as vl_uni,
    ROUND(
        tb_prd_tipo.p_venda * 1.35504 * tb_multiplo.multiplo::int,
        2
    ) as vl_total,
    ROUND(
        tb_estoque.estoque::int / tb_multiplo.multiplo::int
    )::int as estoque,
    prd_gtin.cd_barras as codigo_barras,
    original.num_orig as oem
FROM "D-1".produto
    INNER JOIN (
        SELECT codpro,
            CASE
                WHEN produto.embala = 0 THEN 1
                ELSE produto.embala
            END as multiplo
        FROM "D-1".produto
    ) as tb_multiplo ON produto.codpro = tb_multiplo.codpro
    LEFT JOIN (
        SELECT prd_tipo.codpro,
            prd_tipo.p_venda
        FROM "D-1".prd_tipo
        WHERE cd_tploja = '01'
    ) as tb_prd_tipo ON produto.codpro = tb_prd_tipo.codpro
    LEFT JOIN (
        SELECT codpro,
            SUM(estoque) as estoque
        FROM "H-1".prd_loja
        GROUP BY codpro
    ) as tb_estoque ON produto.codpro = tb_estoque.codpro
    LEFT JOIN "D-1".prd_gtin ON produto.codpro = prd_gtin.cd_produto
    LEFT JOIN "D-1".original ON produto.num_orig = original.nu_origina
WHERE produto.codpro = '%s'
ORDER BY dt_cadast DESC;