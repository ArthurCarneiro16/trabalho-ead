import csv
from datetime import datetime

PRECO_BASE = {
    "1": ("Apartamento", 700.00),
    "2": ("Casa", 900.00),
    "3": ("Estudio", 1200.00),
}

def perg_sim_nao(msg):
    while True:
        r = input(msg + " [s/n]: ").strip().lower()
        if r in ("s", "n"):
            return r == "s"

def perg_int(msg, minimo, maximo):
    while True:
        try:
            v = int(input(msg).strip())
            if minimo <= v <= maximo:
                return v
            print(f"Digite um número entre {minimo} e {maximo}.")
        except ValueError:
            print("Valor inválido.")

def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def main():
    print("\n=== Imobiliária R.M — Orçamento ===\n")

    print("Tipo de imóvel:")
    print("  [1] Apartamento — a partir de R$ 700,00")
    print("  [2] Casa        — a partir de R$ 900,00")
    print("  [3] Estúdio     — R$ 1.200,00")

    while True:
        tipo_key = input("\nEscolha [1/2/3]: ").strip()
        if tipo_key in PRECO_BASE:
            break
        print("Opção inválida.")

    nome_tipo, aluguel = PRECO_BASE[tipo_key]
    extras = []

    if nome_tipo in ("Apartamento", "Casa"):
        quartos = perg_int("Quantos quartos? [1 ou 2]: ", 1, 2)
        if quartos == 2:
            add = 200.00 if nome_tipo == "Apartamento" else 250.00
            aluguel += add
            extras.append(f"2º quarto: +{brl(add)}")

        if perg_sim_nao("Incluir vaga de garagem?"):
            aluguel += 300.00
            extras.append("Garagem: +R$ 300,00")

    else:
        if perg_sim_nao("Incluir vagas de estacionamento?"):
            aluguel += 250.00
            extras.append("2 vagas: +R$ 250,00")
            vagas_extra = perg_int("Vagas adicionais além das 2? [0-10]: ", 0, 10)
            if vagas_extra > 0:
                custo = vagas_extra * 60.00
                aluguel += custo
                extras.append(f"{vagas_extra} vaga(s) extra(s): +{brl(custo)}")

    if nome_tipo == "Apartamento":
        if not perg_sim_nao("Há crianças no contrato?"):
            desconto = aluguel * 0.05
            aluguel -= desconto
            extras.append(f"Desconto sem criancas: -{brl(desconto)}")

    print(f"\nContrato: R$ 2.000,00 (pode parcelar em até 5x)")
    parcelas = perg_int("Em quantas parcelas? [1-5]: ", 1, 5)
    valor_parcela = 2000.00 / parcelas

    cliente = input("\nNome do cliente: ").strip() or "Cliente"

    print("\n--- Resumo ---")
    print(f"Cliente: {cliente}")
    print(f"Imóvel: {nome_tipo}")
    if extras:
        for e in extras:
            print(f"  {e}")
    print(f"Aluguel: {brl(aluguel)}/mês")
    print(f"Contrato: {brl(2000.00)} em {parcelas}x de {brl(valor_parcela)}")
    print(f"1ª mensalidade: {brl(aluguel + valor_parcela)}")
    print("--------------")

    if perg_sim_nao("\nGerar CSV com 12 meses?"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arq = f"orcamento_{cliente.replace(' ', '_')}_{ts}.csv"

        with open(nome_arq, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Imobiliária R.M — Orçamento"])
            w.writerow([f"Cliente: {cliente}", f"Imóvel: {nome_tipo}"])
            w.writerow([])
            w.writerow(["Mês", "Aluguel", "Parcela Contrato", "Total", "Obs"])
            for mes in range(1, 13):
                parc = valor_parcela if mes <= parcelas else 0.0
                obs = f"Parcela {mes}/{parcelas}" if parc > 0 else "-"
                w.writerow([f"Mês {mes:02d}", brl(aluguel), brl(parc), brl(aluguel + parc), obs])

        print(f"Arquivo gerado: {nome_arq}")

if __name__ == "__main__":
    main()
