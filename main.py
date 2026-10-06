import asyncio
from typing import Any, Callable

import flet as ft


PIZZAS: list[tuple[str, str, str, str]] = [
    ("Margherita", "Molho de tomate, mussarela e manjericão", "R$ 32,90", "#E85D4A"),
    ("Calabresa", "Calabresa, cebola roxa e orégano", "R$ 36,90", "#F2A93B"),
    ("Quatro queijos", "Mussarela, provolone, parmesão e gorgonzola", "R$ 42,90", "#6E9E78"),
]
PIZZA_SIZE_MULTIPLIERS = {"P": 0.8, "M": 1.0, "G": 1.25}
DELIVERY_TAX = 6.0


def parse_price(value: str) -> float:
    cleaned = value.replace("R$", "").replace(".", "").replace(",", ".")
    return float(cleaned.strip())


def format_price(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def price_for_size(price: str, size: str) -> float:
    return parse_price(price) * PIZZA_SIZE_MULTIPLIERS[size]


def pizza_selection_handler(index: int, choose: Callable[[int], None]) -> Callable[..., Any]:
    def on_select(*_args: Any):
        choose(index)

    return on_select


def pizza_card(
    name: str,
    description: str,
    price: str,
    accent: str,
    selected: bool,
    on_select: Callable[..., Any],
):
    return ft.Container(
        width=260,
        height=320,
        padding=ft.Padding.all(18),
        border_radius=26,
        bgcolor="#FFFDFB" if not selected else "#FFF4EC",
        border=ft.Border.all(2 if selected else 1, accent if selected else "#F0E1D8"),
        shadow=ft.BoxShadow(
            blur_radius=28 if selected else 10,
            color="#AC6A4D33" if selected else "#2F242010",
            offset=ft.Offset(0, 10),
        ),
        on_click=on_select,
        content=ft.Column(
            [
                ft.Container(
                    height=140,
                    border_radius=20,
                    bgcolor=accent,
                    content=ft.Stack(
                        [
                            ft.Container(
                                alignment=ft.Alignment(1.0, 0.0),
                                padding=ft.Padding.only(top=12, right=12),
                                content=ft.Container(
                                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                                    border_radius=14,
                                    bgcolor="#FFFFFF33",
                                    content=ft.Text(
                                        "TOP" if selected else "NOVO",
                                        size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color="#FFFFFF",
                                    ),
                                ),
                            ),
                            ft.Container(
                                alignment=ft.Alignment(0.5, 0.5),
                                content=ft.Text("🍕", size=76),
                            ),
                        ]
                    ),
                ),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(name, size=20, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                ft.Text(description, size=12.5, color="#706460", max_lines=2),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_ROUNDED if selected else ft.Icons.RADIO_BUTTON_UNCHECKED_ROUNDED,
                            color=accent,
                            size=24,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Row(
                    [
                        ft.Text(price, size=18, weight=ft.FontWeight.BOLD, color=accent),
                        ft.Container(expand=True),
                        ft.Text("Escolher", size=12, color=accent, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
        ),
    )


def main(page: ft.Page):
    page.title = "PizzaDev | Gestão de Comandas"
    page.bgcolor = "#F3EEE8"
    page.padding = 0
    page.window.width = 1300
    page.window.height = 880
    page.window.resizable = True
    page.theme = ft.Theme(font_family="Segoe UI")

    selected_pizza_index: int = 0
    selected_size = "M"
    selected_command_index: int = 0
    delivery_ready_flags: dict[int, bool] = {}
    delivery_countdown: dict[int, int] = {}

    commands: list[dict[str, Any]] = [
        {
            "id": 101,
            "cliente": "Marina Costa",
            "telefone": "11987654321",
            "mesa": "Mesa 12",
            "status": "Aberta",
            "obs": "Sem cebola",
            "tipo_entrega": "Entrega",
            "forma_pagamento": "Dinheiro",
            "endereco": "Rua das Flores",
            "numero": "120",
            "bairro": "Centro",
            "complemento": "Apartamento 3",
            "itens": [
                {"name": "Margherita", "qty": 1, "price": parse_price("R$ 32,90")},
                {"name": "Calabresa", "qty": 2, "price": parse_price("R$ 36,90")},
                {"name": "Quatro queijos", "qty": 1, "price": parse_price("R$ 42,90")},
            ],
        },
        {
            "id": 102,
            "cliente": "João Pereira",
            "telefone": "11976543210",
            "mesa": "Mesa 05",
            "status": "Na cozinha",
            "obs": "Sem oregano",
            "tipo_entrega": "Retirada",
            "forma_pagamento": "Dinheiro",
            "endereco": "",
            "numero": "",
            "bairro": "",
            "complemento": "",
            "itens": [
                {"name": "Quatro queijos", "qty": 1, "price": parse_price("R$ 42,90")},
            ],
        },
        {
            "id": 103,
            "cliente": "Ana Souza",
            "telefone": "11912345678",
            "mesa": "Take Away",
            "status": "Aberta",
            "obs": "Entregar sem molho extra",
            "tipo_entrega": "Entrega",
            "forma_pagamento": "Pix",
            "endereco": "Avenida Paulista",
            "numero": "500",
            "bairro": "Bela Vista",
            "complemento": "Bloco A",
            "itens": [],
        },
    ]

    command_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    menu_cards = ft.Row(spacing=18, scroll=ft.ScrollMode.AUTO)
    size_selector = ft.Row(spacing=8)
    items_column = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
    kitchen_column = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
    feedback = ft.Text("", size=14, color="#1E7E57", weight=ft.FontWeight.BOLD)
    delivery_status_text = ft.Text("", size=12, color="#D78D1B", weight=ft.FontWeight.BOLD)
    total_text = ft.Text("", size=26, weight=ft.FontWeight.BOLD, color="#D96347")
    error_text = ft.Text("", size=12, color="#C93A32")

    customer_name = ft.TextField(label="Nome do cliente", value=commands[selected_command_index]["cliente"])
    customer_phone = ft.TextField(label="Telefone", value=commands[selected_command_index].get("telefone", ""), keyboard_type=ft.KeyboardType.NUMBER)
    customer_table = ft.TextField(label="Mesa / local", value=commands[selected_command_index]["mesa"])
    customer_obs = ft.TextField(label="Observações", value=commands[selected_command_index]["obs"], multiline=True, min_lines=2, max_lines=4)
    customer_address = ft.TextField(label="Rua", value=commands[selected_command_index].get("endereco", ""))
    customer_number = ft.TextField(label="Número", value=commands[selected_command_index].get("numero", ""), keyboard_type=ft.KeyboardType.NUMBER)
    customer_district = ft.TextField(label="Bairro", value=commands[selected_command_index].get("bairro", ""))
    customer_complement = ft.TextField(label="Complemento", value=commands[selected_command_index].get("complemento", ""))

    def get_total(command: dict[str, Any]) -> float:
        subtotal = sum(item["qty"] * item["price"] for item in command["itens"])
        if command.get("tipo_entrega") == "Entrega":
            return subtotal + DELIVERY_TAX
        return subtotal

    def status_badge(status: str) -> tuple[str, str]:
        colors = {
            "Aberta": ("#E8F7EE", "#2E8B57"),
            "Na cozinha": ("#FFF4DB", "#D78D1B"),
            "Pronta": ("#EAF2FF", "#3B6FD8"),
            "Entregue": ("#F4EDF9", "#7A4EB6"),
        }
        bg, fg = colors.get(status, ("#F3F4F6", "#4B5563"))
        return bg, fg

    def refresh_command_list():
        command_list.controls = []
        for idx, command in enumerate(commands):
            bg, fg = status_badge(command["status"])
            selected = idx == selected_command_index
            command_list.controls.append(
                ft.Container(
                    ink=True,
                    on_click=lambda e, i=idx: select_command(i),
                    padding=ft.Padding.all(12),
                    border_radius=18,
                    bgcolor="#F9F3EE" if not selected else "#FFF0E9",
                    border=ft.Border.all(2 if selected else 1, "#F0D9CB" if not selected else "#E85D4A"),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(f"Comanda #{command['id']}", size=16, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=999,
                                        bgcolor=bg,
                                        content=ft.Text(command["status"], size=10, weight=ft.FontWeight.BOLD, color=fg),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(command["cliente"], size=13, color="#655A57"),
                            ft.Text(f"{command['mesa']} · {len(command['itens'])} itens", size=12, color="#857671"),
                        ],
                        spacing=6,
                    ),
                )
            )

    def refresh_kitchen_queue():
        kitchen_column.controls = []
        for command in commands:
            if command["status"] in {"Aberta", "Na cozinha", "Pronta"}:
                bg, fg = status_badge(command["status"])
                kitchen_column.controls.append(
                    ft.Container(
                        padding=ft.Padding.all(12),
                        border_radius=16,
                        bgcolor="#FFFDFB",
                        border=ft.Border.all(1, "#F2E0D5"),
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(f"#{command['id']}", size=15, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                        ft.Text(command["cliente"], size=12, color="#665C58"),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=999,
                                    bgcolor=bg,
                                    content=ft.Text(command["status"], size=10, weight=ft.FontWeight.BOLD, color=fg),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    )
                )
        if not kitchen_column.controls:
            kitchen_column.controls.append(ft.Text("Sem pedidos na fila.", size=13, color="#7C685F"))

    def remove_item_from_command(item_name: str, item_size: str):
        command = commands[selected_command_index]
        command["itens"] = [
            item
            for item in command["itens"]
            if not (item["name"] == item_name and item.get("size", "M") == item_size)
        ]
        feedback.value = f"{item_name} tamanho {item_size} removido da comanda #{command['id']}"
        refresh_all()

    def adjust_item_quantity(item_name: str, item_size: str, delta: int):
        command = commands[selected_command_index]
        for item in command["itens"]:
            if item["name"] == item_name and item.get("size", "M") == item_size:
                item["qty"] += delta
                if item["qty"] <= 0:
                    command["itens"] = [
                        current_item
                        for current_item in command["itens"]
                        if not (current_item["name"] == item_name and current_item.get("size", "M") == item_size)
                    ]
                    feedback.value = f"{item_name} tamanho {item_size} removido da comanda #{command['id']}"
                else:
                    feedback.value = f"Quantidade de {item_name} ({item_size}) atualizada para {item['qty']}."
                refresh_all()
                return

    def refresh_summary():
        command = commands[selected_command_index]
        items_column.controls = []
        if not command["itens"]:
            items_column.controls.append(ft.Text("Nenhum item adicionado ainda.", size=13, color="#7E6C63"))
        else:
            for item in command["itens"]:
                qty = item["qty"]
                price = item["price"]
                item_size = item.get("size", "M")
                items_column.controls.append(
                    ft.Container(
                        padding=ft.Padding.all(12),
                        border_radius=16,
                        bgcolor="#FFFFFF",
                        border=ft.Border.all(1, "#F2E0D5"),
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(f"{item['name']} ({item_size})", size=15, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                        ft.Text(f"Qtd: {qty}", size=11, color="#7B6D66"),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Text(format_price(price * qty), size=15, weight=ft.FontWeight.BOLD, color="#D96347"),
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.REMOVE,
                                            tooltip="Diminuir quantidade",
                                            on_click=lambda _event, item_name=item["name"], size=item_size: adjust_item_quantity(item_name, size, -1),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.ADD,
                                            tooltip="Aumentar quantidade",
                                            on_click=lambda _event, item_name=item["name"], size=item_size: adjust_item_quantity(item_name, size, 1),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            tooltip="Excluir item",
                                            icon_color="#C94F3D",
                                            on_click=lambda _event, item_name=item["name"], size=item_size: remove_item_from_command(item_name, size),
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    )
                )
        total_text.value = f"Total: {format_price(get_total(command))}"

    def refresh_cards():
        menu_cards.controls = [
            pizza_card(
                name,
                description,
                format_price(price_for_size(price, selected_size)),
                accent,
                index == selected_pizza_index,
                pizza_selection_handler(index, choose_pizza),
            )
            for index, (name, description, price, accent) in enumerate(PIZZAS)
        ]

    def refresh_size_selector():
        size_selector.controls = [
            (
                ft.FilledButton(
                    size,
                    on_click=lambda _event, selected=size: choose_size(selected),
                    bgcolor="#E85D4A",
                    color="#FFFFFF",
                )
                if size == selected_size
                else ft.OutlinedButton(
                    size,
                    on_click=lambda _event, selected=size: choose_size(selected),
                )
            )
            for size in PIZZA_SIZE_MULTIPLIERS
        ]

    def validate_customer_data(command: dict[str, Any]) -> bool:
        name = customer_name.value.strip()
        phone = customer_phone.value.strip()
        if not name:
            error_text.value = "Informe o nome do cliente."
            return False

        digits = "".join(char for char in phone if char.isdigit())
        if len(digits) not in {10, 11}:
            error_text.value = "Telefone deve conter 10 ou 11 dígitos."
            return False

        if command.get("tipo_entrega") == "Entrega":
            if not customer_address.value.strip():
                error_text.value = "Para entrega, informe a rua."
                return False
            if not customer_number.value.strip():
                error_text.value = "Para entrega, informe o número do endereço."
                return False
            if not customer_district.value.strip():
                error_text.value = "Para entrega, informe o bairro."
                return False

        error_text.value = ""
        return True

    def refresh_all():
        command = commands[selected_command_index]
        customer_name.value = command["cliente"]
        customer_phone.value = command.get("telefone", "")
        customer_table.value = command["mesa"]
        customer_obs.value = command["obs"]
        customer_address.value = command.get("endereco", "")
        customer_number.value = command.get("numero", "")
        customer_district.value = command.get("bairro", "")
        customer_complement.value = command.get("complemento", "")
        delivery_method = command.get("tipo_entrega", "Retirada")
        delivery_choice.value = delivery_method
        payment_choice.value = command.get("forma_pagamento", "Dinheiro")
        address_section.visible = delivery_method == "Entrega"
        error_text.value = ""
        clear_cart_button.disabled = not command["itens"]
        advance_button.disabled = not command["itens"]
        if command["status"] == "Na cozinha":
            if delivery_ready_flags.get(command["id"], False):
                delivery_status_text.value = "Pronto para entrega"
            else:
                remaining = delivery_countdown.get(command["id"], 60)
                delivery_status_text.value = f"Pronto em {remaining}s"
            delivery_status_text.visible = True
        else:
            delivery_status_text.value = ""
            delivery_status_text.visible = False
        delivery_button.visible = command["status"] == "Na cozinha" and delivery_ready_flags.get(command["id"], False)
        refresh_command_list()
        refresh_size_selector()
        refresh_cards()
        refresh_summary()
        refresh_kitchen_queue()
        page.update()

    def choose_delivery_type(selected_type: str):
        command = commands[selected_command_index]
        command["tipo_entrega"] = selected_type
        refresh_all()

    def choose_payment_type(selected_type: str):
        command = commands[selected_command_index]
        command["forma_pagamento"] = selected_type
        refresh_all()

    def select_command(index: int):
        nonlocal selected_command_index
        selected_command_index = index
        refresh_all()

    def choose_pizza(index: int):
        nonlocal selected_pizza_index
        selected_pizza_index = index
        feedback.value = f"Pizza selecionada: {PIZZAS[index][0]}"
        page.update()

    def choose_size(size: str):
        nonlocal selected_size
        selected_size = size
        feedback.value = f"Tamanho selecionado: {size}"
        refresh_all()

    def add_item_to_command(*_args: Any):
        command = commands[selected_command_index]
        pizza_name, _, price, _ = PIZZAS[selected_pizza_index]
        normalized_size = selected_size.upper()
        item_price = price_for_size(price, normalized_size)
        existing = next(
            (
                item
                for item in command["itens"]
                if item["name"] == pizza_name and item.get("size", "M").upper() == normalized_size
            ),
            None,
        )
        if existing:
            existing["qty"] += 1
            existing["price"] = item_price
        else:
            command["itens"].append({"name": pizza_name, "size": normalized_size, "qty": 1, "price": item_price})
        command["status"] = "Aberta"
        feedback.value = f"{pizza_name} tamanho {normalized_size} adicionado à comanda #{command['id']}"
        refresh_all()

    def save_customer_data(*_args: Any):
        command = commands[selected_command_index]
        if not validate_customer_data(command):
            page.update()
            return

        command["cliente"] = customer_name.value.strip() or "Cliente sem nome"
        command["telefone"] = customer_phone.value.strip()
        command["mesa"] = customer_table.value.strip() or "Mesa sem definir"
        command["obs"] = customer_obs.value.strip() or "Sem observações"
        command["tipo_entrega"] = delivery_choice.value
        command["forma_pagamento"] = payment_choice.value
        command["endereco"] = customer_address.value.strip()
        command["numero"] = customer_number.value.strip()
        command["bairro"] = customer_district.value.strip()
        command["complemento"] = customer_complement.value.strip()
        feedback.value = f"Ficha da comanda #{command['id']} salva."
        error_text.value = ""
        refresh_all()

    def clear_cart(*_args: Any):
        command = commands[selected_command_index]
        if not command["itens"]:
            feedback.value = "O carrinho já está vazio."
            page.update()
            return

        command["itens"] = []
        command["status"] = "Aberta"
        feedback.value = f"Carrinho da comanda #{command['id']} limpo."
        refresh_all()

    def new_command(*_args: Any):
        nonlocal selected_command_index
        next_id = max((command["id"] for command in commands), default=100) + 1
        commands.append(
            {
                "id": next_id,
                "cliente": "Novo cliente",
                "telefone": "",
                "mesa": "Nova mesa",
                "status": "Aberta",
                "obs": "",
                "tipo_entrega": "Retirada",
                "forma_pagamento": "Dinheiro",
                "endereco": "",
                "numero": "",
                "bairro": "",
                "complemento": "",
                "itens": [],
            }
        )
        delivery_ready_flags[next_id] = False
        selected_command_index = len(commands) - 1
        feedback.value = f"Nova comanda aberta: #{next_id}"
        refresh_all()

    def send_to_kitchen(*_args: Any):
        command = commands[selected_command_index]
        if not command["itens"]:
            feedback.value = "Adicione ao menos um item antes de enviar para cozinha."
            page.update()
            return
        if not validate_customer_data(command):
            page.update()
            return

        command_id = command["id"]
        command["status"] = "Na cozinha"
        delivery_ready_flags[command_id] = False
        delivery_countdown[command_id] = 60
        delivery_button.visible = False
        delivery_status_text.value = "Pronto em 60s"
        delivery_status_text.visible = True
        feedback.value = f"Pedido da comanda #{command_id} enviado para a cozinha."

        async def wait_for_delivery_ready(command_id: int):
            for remaining in range(60, 0, -1):
                delivery_countdown[command_id] = remaining
                if command_id == commands[selected_command_index]["id"]:
                    delivery_status_text.value = f"Pronto em {remaining}s"
                    page.update()
                await asyncio.sleep(1)

            delivery_ready_flags[command_id] = True
            delivery_countdown.pop(command_id, None)
            feedback.value = f"Comanda #{command_id} pronta para entrega."
            refresh_all()

        page.run_task(wait_for_delivery_ready, command_id)
        refresh_all()

    def finalize_order(*_args: Any):
        command = commands[selected_command_index]
        if not command["itens"]:
            feedback.value = "Não há itens para finalizar."
            page.update()
            return
        if not validate_customer_data(command):
            page.update()
            return
        command["status"] = "Pronta"
        feedback.value = f"Comanda #{command['id']} pronta para entrega."
        refresh_all()

    clear_cart_button = ft.OutlinedButton(
        "Cancelar pedido",
        icon=ft.Icons.DELETE_SWEEP,
        on_click=clear_cart,
        disabled=True,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )
    advance_button = ft.FilledButton(
        "Avançar",
        icon=ft.Icons.ARROW_FORWARD,
        on_click=finalize_order,
        bgcolor="#E85D4A",
        color="#FFFFFF",
        disabled=True,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )
    delivery_button = ft.FilledButton(
        "Enviar para entrega",
        icon=ft.Icons.DELIVERY_DINING,
        on_click=finalize_order,
        bgcolor="#2E8B57",
        color="#FFFFFF",
        visible=False,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )
    delivery_choice = ft.RadioGroup(
        value=commands[selected_command_index].get("tipo_entrega", "Retirada"),
        content=ft.Row(
            [
                ft.Radio(value="Retirada", label="Retirada"),
                ft.Radio(value="Entrega", label="Entrega"),
            ],
            spacing=18,
        ),
        on_change=lambda e: choose_delivery_type(e.control.value),
    )
    payment_choice = ft.RadioGroup(
        value=commands[selected_command_index].get("forma_pagamento", "Dinheiro"),
        content=ft.Row(
            [
                ft.Radio(value="Dinheiro", label="Dinheiro"),
                ft.Radio(value="Cartão", label="Cartão"),
                ft.Radio(value="Pix", label="Pix"),
            ],
            spacing=18,
        ),
        on_change=lambda e: choose_payment_type(e.control.value),
    )
    address_section = ft.Column(
        [
            customer_address,
            ft.Row([customer_number, customer_district], spacing=12),
            customer_complement,
        ],
        spacing=10,
        visible=commands[selected_command_index].get("tipo_entrega", "Retirada") == "Entrega",
    )

    page.add(
        ft.Container(
            expand=True,
            padding=ft.Padding.all(22),
            content=ft.Row(
                [
                    ft.Container(
                        width=310,
                        padding=ft.Padding.all(18),
                        border_radius=28,
                        bgcolor="#1E1B20",
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("PizzaDev", size=22, weight=ft.FontWeight.BOLD, color="#F9EDE7"),
                                        ft.Container(expand=True),
                                        ft.Icon(ft.Icons.LOCAL_PIZZA_ROUNDED, color="#FF8B5A", size=30),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Divider(height=12, color="transparent"),
                                ft.Text("Comandas", size=16, weight=ft.FontWeight.BOLD, color="#F4E1D6"),
                                ft.Divider(height=8, color="transparent"),
                                command_list,
                                ft.Divider(height=10, color="transparent"),
                                ft.Button(
                                    "Nova comanda",
                                    icon=ft.Icons.ADD,
                                    on_click=new_command,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=14),
                                        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
                                    ),
                                ),
                            ],
                            spacing=6,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        padding=ft.Padding.all(14),
                        border_radius=28,
                        bgcolor="#FFFDFB",
                        border=ft.Border.all(1, "#F0E1D8"),
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Column(
                                            [
                                                ft.Text("Seleção de sabores", size=28, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                                ft.Text("Montagem rápida do pedido", size=14, color="#7C685F"),
                                            ],
                                            spacing=2,
                                            expand=True,
                                        ),
                                        ft.Container(
                                            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                                            border_radius=999,
                                            bgcolor="#FDE8DE",
                                            content=ft.Text("Ativo", size=11, weight=ft.FontWeight.BOLD, color="#D95F45"),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Divider(height=12, color="transparent"),
                                ft.Row(
                                    [
                                        ft.Text("Tamanho", size=13, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                        size_selector,
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Divider(height=4, color="transparent"),
                                menu_cards,
                                ft.Divider(height=10, color="transparent"),
                                ft.Row(
                                    [
                                        ft.Column([ft.Text("Comanda ativa", size=12, color="#7B6D66"), ft.Text(f"#{commands[selected_command_index]['id']}", size=24, weight=ft.FontWeight.BOLD, color="#2B1D18")], spacing=2),
                                        ft.Container(expand=True),
                                        ft.Button(
                                            "Adicionar item",
                                            icon=ft.Icons.ADD_SHOPPING_CART,
                                            on_click=add_item_to_command,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=14),
                                                padding=ft.Padding.symmetric(horizontal=18, vertical=14),
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=0,
                        ),
                    ),
                    ft.Container(
                        width=400,
                        padding=ft.Padding.all(18),
                        border_radius=28,
                        bgcolor="#F8F1EC",
                        border=ft.Border.all(1, "#F0D9CB"),
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Ficha do cliente", size=23, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                        ft.Container(expand=True),
                                        ft.IconButton(icon=ft.Icons.SAVE, on_click=save_customer_data),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Divider(height=10, color="transparent"),
                                customer_name,
                                customer_phone,
                                ft.Text("Tipo de recebimento", size=13, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                delivery_choice,
                                ft.Text("Forma de pagamento", size=13, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                payment_choice,
                                address_section,
                                customer_table,
                                customer_obs,
                                error_text,
                                ft.Divider(height=10, color="transparent"),
                                ft.Text("Pedido atual", size=16, weight=ft.FontWeight.BOLD, color="#2B1D18"),
                                items_column,
                                ft.Divider(height=6, color="transparent"),
                                ft.Container(
                                    padding=ft.Padding.all(14),
                                    border_radius=18,
                                    bgcolor="#FFF3ED",
                                    content=ft.Column(
                                        [
                                            ft.Text("Resumo do valor", size=12, color="#816C63"),
                                            total_text,
                                        ],
                                        spacing=2,
                                    ),
                                ),
                                ft.Row(
                                    [
                                        clear_cart_button,
                                        ft.OutlinedButton(
                                            "Enviar para cozinha",
                                            icon=ft.Icons.KITCHEN,
                                            on_click=send_to_kitchen,
                                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                                        ),
                                        delivery_button,
                                        advance_button,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                delivery_status_text,
                                feedback,
                            ],
                            spacing=8,
                        ),
                    ),
                ],
                spacing=20,
            ),
        )
    )

    refresh_all()


if __name__ == "__main__":
    ft.run(main)
