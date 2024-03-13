class APIEndpoints:
    endpoints_dict = {
        'int': 'https://saphetydoc-int.saphety.com/TradeHttp/MessageServiceRest',
        'qa': 'https://www-qa.netdocs.com.pt/TradeHttp/MessageServiceRest',
        'prd': 'https://www.netdocs.com.pt/TradeHttp/MessageServiceRest',
        'sin-int': 'https://doc-server-int.saphety.com/Doc.WebApi.Services',
        'sin-qa': 'https://doc-server-qa.saphety.com/Doc.WebApi.Services',
        'sin-prd': 'https://doc-server.saphety.com/Doc.WebApi.Services',
        'cn-dev': 'https://api-internal.sovos.com',
        'cn-uat': 'https://api-internal.sovos.com',
        'delta-qa': 'https://api-internal.sovos.com',
        'delta-uat': 'https://api-test.sovos.com'
    }

    @classmethod
    def get_endpoint_by_alias(cls, alias: str) -> str:
        return cls.endpoints_dict.get(alias, None)
