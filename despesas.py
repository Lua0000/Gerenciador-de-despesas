import sys
import json
import csv
import os
import argparse
from datetime import datetime

DATA_FILE = "despesas_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"expenses": [], "budgets": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"expenses": [], "budgets": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def check_budget_warning(data, date_str):
    month_str = date_str[:7] # YYYY-MM
    budget = data["budgets"].get(month_str)
    if budget is not None:
        total = sum(e["amount"] for e in data["expenses"] if e["date"].startswith(month_str))
        if total > budget:
            print(f"\n[AVISO] Você ultrapassou o orçamento de R${budget:.2f} para o mês {month_str}! Total atual: R${total:.2f}")

def add_expense(description, amount, category="Geral"):
    data = load_data()
    date_str = datetime.now().strftime("%Y-%m-%d")
    expense_id = 1 if not data["expenses"] else max(e["id"] for e in data["expenses"]) + 1
    
    expense = {
        "id": expense_id,
        "date": date_str,
        "description": description,
        "amount": amount,
        "category": category
    }
    
    data["expenses"].append(expense)
    save_data(data)
    print(f"Despesa adicionada com sucesso! (ID: {expense_id})")
    check_budget_warning(data, date_str)

def update_expense(expense_id, description=None, amount=None, category=None):
    data = load_data()
    for e in data["expenses"]:
        if e["id"] == expense_id:
            if description is not None: e["description"] = description
            if amount is not None: e["amount"] = amount
            if category is not None: e["category"] = category
            save_data(data)
            print(f"Despesa {expense_id} atualizada com sucesso!")
            check_budget_warning(data, e["date"])
            return
    print(f"Despesa com ID {expense_id} não encontrada.")

def delete_expense(expense_id):
    data = load_data()
    initial_len = len(data["expenses"])
    data["expenses"] = [e for e in data["expenses"] if e["id"] != expense_id]
    
    if len(data["expenses"]) < initial_len:
        save_data(data)
        print("Despesa excluída com sucesso!")
    else:
        print("Despesa não encontrada.")

def list_expenses(category=None):
    data = load_data()
    expenses = data["expenses"]
    if category:
        expenses = [e for e in expenses if e["category"].lower() == category.lower()]
        
    if not expenses:
        print("Nenhuma despesa encontrada.")
        return
        
    print(f"\n{'ID':<5} | {'Data':<10} | {'Categoria':<15} | {'Valor':<10} | {'Descrição'}")
    print("-" * 65)
    for e in expenses:
        print(f"{e['id']:<5} | {e['date']:<10} | {e['category']:<15} | R${e['amount']:<8.2f} | {e['description']}")
    print("-" * 65)

def summary_expenses(month=None):
    data = load_data()
    year = datetime.now().year
    
    expenses = data["expenses"]
    if month:
        month_str = f"{year}-{int(month):02d}"
        expenses = [e for e in expenses if e["date"].startswith(month_str)]
        title = f"Resumo de {int(month):02d}/{year}"
    else:
        title = "Resumo de todas as despesas"
        
    total = sum(e["amount"] for e in expenses)
    print(f"\n=== {title} ===")
    print(f"Total: R${total:.2f}")

def set_budget(month, amount):
    data = load_data()
    year = datetime.now().year
    month_str = f"{year}-{int(month):02d}"
    data["budgets"][month_str] = amount
    save_data(data)
    print(f"Orçamento para {int(month):02d}/{year} definido como R${amount:.2f}")
    check_budget_warning(data, f"{month_str}-01")

def export_csv():
    data = load_data()
    filename = "despesas_export.csv"
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Data", "Descrição", "Valor", "Categoria"])
        for e in data["expenses"]:
            writer.writerow([e["id"], e["date"], e["description"], e["amount"], e["category"]])
    print(f"Despesas exportadas para {filename} com sucesso!")

def export_txt():
    data = load_data()
    filename = "despesas_export.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== RELATÓRIO DE DESPESAS ===\n\n")
        total = 0
        for e in data["expenses"]:
            f.write(f"ID: {e['id']}\n")
            f.write(f"Data: {e['date']}\n")
            f.write(f"Categoria: {e['category']}\n")
            f.write(f"Valor: R${e['amount']:.2f}\n")
            f.write(f"Descrição: {e['description']}\n")
            f.write("-" * 30 + "\n")
            total += e["amount"]
        f.write(f"\nTOTAL GERAL: R${total:.2f}\n")
    print(f"Despesas salvas em {filename} com sucesso!")

def interactive_menu():
    while True:
        print("\n" + "="*45)
        print("        GERENCIADOR DE DESPESAS")
        print("="*45)
        print("1. Adicionar despesa")
        print("2. Atualizar despesa")
        print("3. Excluir despesa")
        print("4. Visualizar todas as despesas")
        print("5. Resumo de todas as despesas")
        print("6. Resumo das despesas de um mês")
        print("7. Filtrar despesas por categoria")
        print("8. Definir orçamento mensal")
        print("9. Exportar para CSV")
        print("10. Salvar todas as despesas em TXT")
        print("0. Sair")
        print("="*45)
        
        choice = input("Escolha uma opção: ")
        
        if choice == '1':
            desc = input("Descrição: ")
            try:
                amt = float(input("Valor (utilize ponto para os centavos): "))
            except ValueError:
                print("Valor inválido!")
                continue
            cat = input("Categoria (padrão: Geral): ") or "Geral"
            add_expense(desc, amt, cat)
        elif choice == '2':
            try:
                e_id = int(input("ID da despesa: "))
            except ValueError:
                print("ID inválido!")
                continue
            desc = input("Nova descrição (enter para manter o registro antigo): ") or None
            amt_str = input("Novo valor (enter para manter o registro antigo): ")
            amt = None
            if amt_str:
                try: amt = float(amt_str)
                except ValueError: print("Valor inválido ignorado.")
            cat = input("Nova categoria (enter para manter o registro antigo): ") or None
            update_expense(e_id, desc, amt, cat)
        elif choice == '3':
            try:
                e_id = int(input("ID da despesa a ser excluída: "))
            except ValueError:
                print("ID inválido!")
                continue
            delete_expense(e_id)
        elif choice == '4':
            list_expenses()
        elif choice == '5':
            summary_expenses()
        elif choice == '6':
            try:
                m = int(input("Mês numérico (ex: 3 para Março): "))
            except ValueError:
                print("Mês inválido!")
                continue
            summary_expenses(m)
        elif choice == '7':
            cat = input("Digite a categoria que deseja analisar: ")
            list_expenses(cat)
        elif choice == '8':
            try:
                m = int(input("Mês (1-12): "))
                amt = float(input("Orçamento mensal em reais: "))
            except ValueError:
                print("Valores inválidos!")
                continue
            set_budget(m, amt)
        elif choice == '9':
            export_csv()
        elif choice == '10':
            export_txt()
        elif choice == '0':
            print("Saindo do gerenciador. Até logo!")
            break
        else:
            print("Opção inválida.")

def parse_args():
    parser = argparse.ArgumentParser(description="Gerenciador de Despesas CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Add
    parser_add = subparsers.add_parser("add", help="Adicionar uma despesa")
    parser_add.add_argument("--description", required=True, help="Descrição da despesa")
    parser_add.add_argument("--amount", required=True, type=float, help="Valor da despesa")
    parser_add.add_argument("--category", default="Geral", help="Categoria da despesa (opcional)")

    # Update
    parser_update = subparsers.add_parser("update", help="Atualizar uma despesa")
    parser_update.add_argument("--id", required=True, type=int, help="ID da despesa")
    parser_update.add_argument("--description", help="Nova descrição")
    parser_update.add_argument("--amount", type=float, help="Novo valor")
    parser_update.add_argument("--category", help="Nova categoria")

    # Delete
    parser_delete = subparsers.add_parser("delete", help="Excluir uma despesa")
    parser_delete.add_argument("--id", required=True, type=int, help="ID da despesa")

    # List
    parser_list = subparsers.add_parser("list", help="Listar despesas")
    parser_list.add_argument("--category", help="Filtrar por categoria")

    # Summary
    parser_summary = subparsers.add_parser("summary", help="Resumo das despesas")
    parser_summary.add_argument("--month", type=int, help="Mês específico (1-12)")

    # Budget
    parser_budget = subparsers.add_parser("budget", help="Definir orçamento mensal")
    parser_budget.add_argument("--month", required=True, type=int, help="Mês (1-12)")
    parser_budget.add_argument("--amount", required=True, type=float, help="Valor do orçamento")

    # Export CSV
    parser_export_csv = subparsers.add_parser("export-csv", help="Exportar despesas para CSV")

    # Export TXT
    parser_export_txt = subparsers.add_parser("export-txt", help="Exportar despesas para TXT")

    args = parser.parse_args()

    if args.command == "add":
        add_expense(args.description, args.amount, args.category)
    elif args.command == "update":
        update_expense(args.id, args.description, args.amount, args.category)
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "list":
        list_expenses(args.category)
    elif args.command == "summary":
        summary_expenses(args.month)
    elif args.command == "budget":
        set_budget(args.month, args.amount)
    elif args.command == "export-csv":
        export_csv()
    elif args.command == "export-txt":
        export_txt()
    else:
        parser.print_help()

def main():
    # Se não houver argumentos, abre o Menu Interativo (ótimo para uso como um .exe)
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        parse_args()

if __name__ == "__main__":
    main()
