import sys, os
os.environ["FLET_SECRET_KEY"] = "your-simple-key-123"
import flet as ft
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.input_parse import PoboljsajUnos, TestirajUnos
from tools import oracle_local
from frontend.document import create_docs_content
from frontend.outlook import create_outlook_export_content
import time
import asyncio
from frontend.applist import apps
from frontend.set_message import settimeoutmessage, setloading


def main(page: ft.Page):
    page.client_storage.set("upload_dir", "../unos/dokumentacija")

    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.INDIGO,
    )
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#303030"
    

    # Poruke sekcija
    message_section = ft.Column([], height=35, scroll="auto",) 
    def show_message(message:str, color=ft.Colors.GREEN):
        settimeoutmessage(page, message_section, message, color, timeout=3)

    def show_error(message:str, color=ft.Colors.RED):
        settimeoutmessage(page, message_section, message, color, timeout=5)

    def show_loading(message:str, color=ft.Colors.BLUE):
        setloading(page, message_section, message, color=color)

    def end_loading(message:str, color=ft.Colors.GREEN):
        settimeoutmessage(page, message_section, message, color=color, timeout=2)


    # Lista kontrole
    def ucitaj_df():
        nonlocal scrollable_container
        try:
            import frontend.data
            columns = [ft.DataColumn(ft.Text(col)) for col in frontend.data.df.columns]
            columns.append(ft.DataColumn(ft.Text("Akcije")))
            
            rows = []
            for index, row in frontend.data.df.iterrows():
                cells = [
                    ft.DataCell(
                        ft.Text(
                            str(row[col])[:100] + "..." if len(str(row[col])) > 100 else str(row[col]),
                            overflow="ellipsis",
                            max_lines=2
                        )
                    )
                    for col in frontend.data.df.columns
                ]
                
                delete_button = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED,
                    tooltip="Obriši red",
                    on_click=lambda e, idx=index: delete_row(idx)
                )
                edit_button = ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=ft.Colors.BLUE,
                    tooltip="Uredi red",
                    on_click=lambda e, idx=index: izmjeni_redak(idx)
                )
                cells.append(ft.DataCell(ft.Row([edit_button, delete_button], spacing=5)))
                
                rows.append(ft.DataRow(cells=cells))
            
            data_table = ft.DataTable(
                columns=columns,
                rows=rows,
                border=ft.border.all(1, ft.Colors.BLACK),
                show_bottom_border=True,
                show_checkbox_column=False,
                divider_thickness=1,
                data_row_min_height=40,
                heading_row_height=40,
            )
            scroll = ft.ListView(
                controls=[data_table],
                expand=True,
                spacing=10,
                padding=10,
                auto_scroll=True
            )
            if scrollable_container:
                manual_tab_content.controls.remove(scrollable_container)
            scrollable_container = scroll
            manual_tab_content.controls.append(scrollable_container)
            page.update()
        except Exception as e:
            show_error(f"Greška pri učitavanju tabele: {e}", ft.Colors.RED)

    def izbrisi_sve():
        import frontend.data
        frontend.data.df = frontend.data.df.iloc[0:0]
        ucitaj_df()
        page.close(izbrisati_dlg)

        show_message("Svi unosi su izbrisani.", ft.Colors.RED)
    def izmjeni_redak(index):
        import frontend.data
        current_values = frontend.data.df.iloc[index]
        pitanjeUnos.value = current_values["pitanje"]
        odgovorUnos.value = current_values["odgovor"]
        KontekstUnos.value = current_values["kontekst"]
        aplikacijaUnos.value = current_values["aplikacija"]
        show_message("Uređivanje redka. Promijenite vrijednosti i kliknite 'Dodaj u listu' za spremanje.", ft.Colors.BLUE)
        delete_row(index)
    def dodajulistu(pitanje, odgovor, kontekst, aplikacija):
        if not pitanje or not odgovor or not kontekst or not aplikacija:
            show_error("Molimo unesite sve podatke uključujući aplikaciju.", ft.Colors.RED)
            return
        print(f"Dodaj u listu: {pitanje}, {odgovor}, {kontekst}, {aplikacija}")
        import frontend.data
        frontend.data.df.loc[len(frontend.data.df)] = [pitanje, odgovor, kontekst, aplikacija]
        
        pitanjeUnos.value = ""
        odgovorUnos.value = ""
        KontekstUnos.value = ""
        
        show_message("Uspješno dodano u listu!", ft.Colors.GREEN)
        ucitaj_df()

    def Testiraj(pitanje, odgovor, kontekst):
        if not pitanje or not odgovor or not kontekst:
            show_error("Molimo unesite pitanje, odgovor i kontekst za testiranje.", ft.Colors.RED)
            return
        show_loading("Testiranje unosa, molimo pričekajte...")
        try:
            kritika = TestirajUnos(pitanje, odgovor, kontekst)
            print(f"AI Testiranje: {kritika}")
        except Exception as e:
            show_error(f"Greška pri testiranju unosa: {e}", ft.Colors.RED)
            kritika = "Prazna kritika."
        end_loading("Testiranje završeno!", ft.Colors.GREEN)
        show_message(kritika, ft.Colors.BLUE)
        return kritika

    def Poboljsaj(pitanje, odgovor, kontekst, kritika=""):
        if not pitanje or not odgovor or not kontekst:
            show_error("Molimo unesite pitanje, odgovor i kontekst za poboljšanje.", ft.Colors.RED)
            return
        show_loading("Poboljšavanje unosa, molimo pričekajte...")
        try:
            rezultat = PoboljsajUnos(pitanje, odgovor, kontekst)
        except Exception as e:
            show_error(f"Greška pri poboljšavanju unosa: {e}", ft.Colors.RED)
        print(f"AI Poboljšanje: {rezultat}")
        pitanjeUnos.value = rezultat['pitanje']
        odgovorUnos.value = rezultat['odgovor']
        end_loading("AI poboljšanje uspješno!", ft.Colors.GREEN)
        ucitaj_df()


    def testirajsadlg(pitanje, odgovor, kontekst):
        kritika = Testiraj(pitanje, odgovor, kontekst)
        def close_dlg_kritika(e):
            page.close(kritika_dlg)
        kritika_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("AI KRITIKA UNOSA"),
            content=ft.Text(kritika),
            actions=[
                ft.TextButton("Ok", on_click=close_dlg_kritika)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(kritika_dlg)

    def delete_row(index):
        import frontend.data
        frontend.data.df = frontend.data.df.drop(index).reset_index(drop=True)
        ucitaj_df()


        
    def confirm_upload(e):
        close_dlg_confirm(e)
        try:
            import frontend.data
            if not frontend.data.df.empty:
                show_loading("Slanje podataka u bazu, molimo pričekajte...")
                oracle_local.send_to_database(frontend.data.df)
                end_loading("Uspješno poslano u bazu!", ft.Colors.GREEN)
            else:
                show_error("Nema podataka za slanje u bazu.", ft.Colors.RED)
        except Exception as ex:
            show_error(f"Greška pri slanju u bazu: {ex}", ft.Colors.RED)

    scrollable_container = None

 



    page.title = "Baza znanja interface"
    Title = ft.Row(
        [
            ft.Icon(ft.Icons.EDIT_DOCUMENT, size=50, color=ft.Colors.WHITE),
            ft.Text(
                "Upis u bazu znanja chatbota",
                theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                color=ft.Colors.WHITE,
            ),
        ],
        alignment="start",  # Flet uses "start" instead of "left"
        vertical_alignment="end"
    )

    pitanjeUnos = ft.TextField(label="pitanje", autofocus=True, min_lines=1, max_lines=1)
    odgovorUnos = ft.TextField(label="odgovor", multiline=True, min_lines=3, max_lines=5)
    KontekstUnos = ft.TextField(label="Razjasni", multiline=True, min_lines=4, max_lines=5)
    
    aplikacijaUnos = ft.Dropdown(
        label="Aplikacija",
        hint_text="Odaberite aplikaciju",
        options=[ft.dropdown.Option(str(app["id"]), app["name"]) for app in apps],
        width=300,
        enable_filter=True
    )

    def close_dlg_izbrisati(e):
        page.close(izbrisati_dlg)
        page.update()

    def close_dlg_confirm(e):
        page.close(confirm_dlg)
        page.update()


    confirm_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Upload u bazu"),
        content=ft.Text("Uploadat listu u bazu?"),
        actions=[
            ft.TextButton("Da", on_click=lambda e: confirm_upload(e)),
            ft.TextButton("Ne", on_click=lambda e: close_dlg_confirm(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    izbrisati_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Izbrisati sve unose?"),
        content=ft.Text("Jeste li sigurni da želite izbrisati sve unose?"),
        actions=[
            ft.TextButton("Da", on_click=lambda e: izbrisi_sve()),
            ft.TextButton("Ne", on_click=lambda e: close_dlg_izbrisati(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def show_confirm_dlg(e):
        page.dialog = confirm_dlg
        page.open(confirm_dlg)
        page.update()

    def show_izbrisati_dlg(e):
        page.dialog = izbrisati_dlg
        page.open(izbrisati_dlg)
        page.update()



    Buttons = ft.Row([
        ft.ElevatedButton("Dodaj u listu", on_click=lambda e: dodajulistu(pitanjeUnos.value, odgovorUnos.value, KontekstUnos.value, int(aplikacijaUnos.value))),
        ft.ElevatedButton("AI Poboljsaj Unos", on_click=lambda e: Poboljsaj(pitanjeUnos.value, odgovorUnos.value, KontekstUnos.value, Testiraj(pitanjeUnos.value, odgovorUnos.value, KontekstUnos.value)), bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE),
        ft.ElevatedButton("Izbriši sve", on_click=lambda e: show_izbrisati_dlg(e), bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
        ft.ElevatedButton("Upload u bazu", on_click=lambda e: show_confirm_dlg(e) , bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
        ft.ElevatedButton("Testiraj Unos", on_click=lambda e: testirajsadlg(pitanjeUnos.value, odgovorUnos.value, KontekstUnos.value), bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
    ], alignment="start", spacing=10)

    
    manual_tab_content = ft.Column([
        message_section,
        pitanjeUnos,
        odgovorUnos,
        KontekstUnos,
        aplikacijaUnos,
        Buttons,
    ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Manualni Unos",
                content=ft.Container(
                    content=manual_tab_content,
                    padding=10
                ),
            ),
            ft.Tab(
                text="Dokumenti",
                content=ft.Container(
                    content=create_docs_content(page),
                    padding=10
                ),
            ),
            ft.Tab(
                text="Outlook export",
                content=ft.Container(
                    content=create_outlook_export_content(page),
                    padding=10
                ),
            ),
        ],
        expand=1,
        on_change=lambda e: ucitaj_df()
    )

    page.add(Title, t)
    page.dialog = confirm_dlg
    ucitaj_df()
    page.update()

if __name__ == "__main__":
    os.makedirs("../unos/dokumentacija", exist_ok=True)
    ft.app(target=main, host="0.0.0.0", port=80, upload_dir="../unos/dokumentacija",assets_dir="assets")
