from .company import load_company_config


def company(request):
    data = load_company_config()
    return {"demo_company": data["organization"]}
