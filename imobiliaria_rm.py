"""
=============================================================
  IMOBILIÁRIA R.M — Sistema de Geração de Orçamento
=============================================================
"""

import csv
import os
from datetime import datetime


# ─── CONSTANTES ───────────────────────────────────────────

TIPOS_IMOVEL = {
    "1": {"nome": "Apartamento", "preco_base": 700.00},
    "2": {"nome": "Casa",        "preco_base": 900.00},
    "3": {"nome": "Estúdio",     "preco_base": 1200.00},
}

CONTRATO_TOTAL    = 2000.00
CONTRATO_MAX_PARC = 5

ADICIONAL_APTO_2Q  = 200.00   # 2º quarto em apartamento
ADICIONAL_CASA_2Q  = 250.00   # 2º quarto em casa
GARAGEM_APT_CASA   = 300.00   # vaga para apt / casa
ESTUDIO_2_VAGAS    = 250.00   # 2 vagas no estúdio
ESTUDIO_VAGA_EXTRA = 60.00    # vagas além das 2 no estúdio
DESCONTO_SEM_KIDS  = 0.05     # 5 % para apt sem crianças


# ─── HELPERS ──────────────────────────────────────────────

def linha(char="─", n=55):
    print(char * n)

def cabecalho(titulo: str):
    linha("═")
    print(f"  {titulo}")
    linha("═")

def opcao(prompt: str, validas: list[str]) -> str:
    while True:
        resp = input(prompt).strip()
        if resp in validas:
            return resp
        print(f"  ⚠  Opção inválida. Escolha entre: {', '.join(validas)}")

def sim_nao(prompt: str) -> bool:
    return opcao(f"{prompt} [s/n]: ", ["s", "S", "n", "N"]).lower() == "s"

def inteiro(prompt: str, minimo: int = 1, maximo: int = 99) -> int:
    while True:
        try:
            v = int(input(prompt).strip())
            if minimo <= v <= maximo:
                return v
            print(f"  ⚠  Digite um número entre {minimo} e {maximo}.")
        except ValueError:
            print("  ⚠  Valor inválido. Digite um número inteiro.")

def brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ─── LÓGICA DO ORÇAMENTO ──────────────────────────────────

def calcular_orcamento() -> dict:
    cabecalho("IMOBILIÁRIA R.M — Geração de Orçamento")

    # 1. Tipo de imóvel
    print("\n  Tipos de imóvel disponíveis:")
    for k, v in TIPOS_IMOVEL.items():
        print(f"    [{k}] {v['nome']:12s}  — a partir de {brl(v['preco_base'])}/mês")

    tipo_key  = opcao("\n  Selecione o tipo [1/2/3]: ", list(TIPOS_IMOVEL.keys()))
    tipo      = TIPOS_IMOVEL[tipo_key]
    nome_tipo = tipo["nome"]
    aluguel   = tipo["preco_base"]
    detalhes  = []

    # 2. Quartos (Apto / Casa)
    quartos = 1
    if nome_tipo in ("Apartamento", "Casa"):
        quartos = inteiro(f"\n  Quantos quartos deseja? [1 ou 2]: ", 1, 2)

        if quartos == 2:
            adicional = ADICIONAL_APTO_2Q if nome_tipo == "Apartamento" else ADICIONAL_CASA_2Q
            aluguel  += adicional
            detalhes.append(f"2º quarto (+{brl(adicional)})")

    # 3. Garagem / Vagas
    vagas_estudio = 0

    if nome_tipo in ("Apartamento", "Casa"):
        if sim_nao("\n  Deseja incluir vaga de garagem?"):
            aluguel += GARAGEM_APT_CASA
            detalhes.append(f"Vaga de garagem (+{brl(GARAGEM_APT_CASA)})")

    elif nome_tipo == "Estúdio":
        if sim_nao("\n  Deseja incluir vagas de estacionamento?"):
            aluguel      += ESTUDIO_2_VAGAS
            vagas_estudio = 2
            detalhes.append(f"2 vagas de estacionamento (+{brl(ESTUDIO_2_VAGAS)})")

            extras = inteiro("  Quantas vagas adicionais (além das 2)? [0–10]: ", 0, 10)
            if extras > 0:
                custo_extras  = extras * ESTUDIO_VAGA_EXTRA
                aluguel      += custo_extras
                vagas_estudio += extras
                detalhes.append(f"{extras} vaga(s) extra(s) (+{brl(custo_extras)})")

    # 4. Desconto (Apartamento sem crianças)
    desconto_aplicado = 0.0
    if nome_tipo == "Apartamento":
        if sim_nao("\n  Há crianças no contrato?"):
            pass  # sem desconto
        else:
            desconto_aplicado = aluguel * DESCONTO_SEM_KIDS
            aluguel          -= desconto_aplicado
            detalhes.append(f"Desconto sem crianças (-{brl(desconto_aplicado)})")

    # 5. Parcelas do contrato
    print(f"\n  O contrato imobiliário é de {brl(CONTRATO_TOTAL)}")
    parcelas_contrato = inteiro(
        f"  Em quantas vezes deseja parcelar? [1–{CONTRATO_MAX_PARC}]: ", 1, CONTRATO_MAX_PARC
    )
    valor_parcela_contrato = CONTRATO_TOTAL / parcelas_contrato

    # 6. Nome do cliente (para o CSV)
    print()
    linha()
    cliente = input("  Nome do cliente: ").strip() or "Cliente"

    return {
        "cliente":               cliente,
        "tipo":                  nome_tipo,
        "quartos":               quartos if nome_tipo != "Estúdio" else None,
        "vagas_estudio":         vagas_estudio if nome_tipo == "Estúdio" else None,
        "desconto":              desconto_aplicado,
        "detalhes":              detalhes,
        "aluguel_mensal":        aluguel,
        "contrato_total":        CONTRATO_TOTAL,
        "parcelas_contrato":     parcelas_contrato,
        "valor_parcela_contrato": valor_parcela_contrato,
        "total_mensal_1a_parcela": aluguel + valor_parcela_contrato,
        "tipo_key":              tipo_key,
    }


# ─── EXIBIÇÃO DO RESUMO ───────────────────────────────────

def exibir_resumo(orc: dict):
    cabecalho(f"RESUMO DO ORÇAMENTO — {orc['cliente'].upper()}")

    print(f"\n  Tipo de imóvel : {orc['tipo']}")
    if orc["quartos"]:
        print(f"  Quartos        : {orc['quartos']}")
    if orc["vagas_estudio"]:
        print(f"  Vagas totais   : {orc['vagas_estudio']}")

    if orc["detalhes"]:
        print("\n  Adicionais / Descontos:")
        for d in orc["detalhes"]:
            print(f"    • {d}")

    linha()
    print(f"  Aluguel mensal           : {brl(orc['aluguel_mensal'])}")
    print(f"  Contrato (total)         : {brl(orc['contrato_total'])}")
    print(f"  Contrato (parcela x{orc['parcelas_contrato']:02d})  : {brl(orc['valor_parcela_contrato'])}")
    linha()
    print(f"  Total 1ª mensalidade     : {brl(orc['total_mensal_1a_parcela'])} (aluguel + 1ª parcela contrato)")
    linha("═")


# ─── GERAÇÃO DO CSV ───────────────────────────────────────

def gerar_csv(orc: dict):
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arq = f"orcamento_{orc['cliente'].replace(' ', '_')}_{ts}.csv"

    with open(nome_arq, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")

        # Cabeçalho informativo
        writer.writerow(["IMOBILIÁRIA R.M — ORÇAMENTO DE LOCAÇÃO"])
        writer.writerow([f"Cliente: {orc['cliente']}"])
        writer.writerow([f"Imóvel: {orc['tipo']}"])
        writer.writerow([f"Aluguel mensal: {brl(orc['aluguel_mensal'])}"])
        writer.writerow([f"Contrato total: {brl(orc['contrato_total'])} em {orc['parcelas_contrato']}x de {brl(orc['valor_parcela_contrato'])}"])
        writer.writerow([])

        # Tabela de 12 meses
        writer.writerow(["Mês", "Aluguel", "Parcela Contrato", "Total do Mês", "Observação"])

        for mes in range(1, 13):
            parcela = orc["valor_parcela_contrato"] if mes <= orc["parcelas_contrato"] else 0.00
            total   = orc["aluguel_mensal"] + parcela
            obs     = f"Parcela {mes}/{orc['parcelas_contrato']} do contrato" if parcela > 0 else "Somente aluguel"
            writer.writerow([
                f"Mês {mes:02d}",
                brl(orc["aluguel_mensal"]),
                brl(parcela),
                brl(total),
                obs,
            ])

    print(f"\n  ✅  Arquivo gerado: {os.path.abspath(nome_arq)}")
    return nome_arq


# ─── PONTO DE ENTRADA ─────────────────────────────────────

def main():
    try:
        orc = calcular_orcamento()
        exibir_resumo(orc)

        if sim_nao("\n  Deseja gerar o arquivo CSV com as 12 parcelas do orçamento?"):
            gerar_csv(orc)

        linha("═")
        print("  Obrigado por usar o sistema da Imobiliária R.M!")
        linha("═")

    except KeyboardInterrupt:
        print("\n\n  Operação cancelada. Até logo!")


if __name__ == "__main__":
    main()
