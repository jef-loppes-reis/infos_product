from ecomm import Postgres

with open('./data/sql/query.sql', 'r', encoding='utf-8') as fp:

    query: str = fp.read()
    query = query%('codpro', '046168')
    query = query.replace("WHERE produto.'codpro'", 'produto.codpro')
    query = query.replace("WHERE produto.'num_fab'", 'produto.num_fab')

    # with Postgres() as db:
    #     print(db.query(fp.read()%'codpro'%'046168'))
