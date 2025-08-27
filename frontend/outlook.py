import flet as ft
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from .collector import move_file_to_collector
from frontend.applist import apps

df = pd.DataFrame(columns=["pitanje", "odgovor", "kontekst", "aplikacija"])
sharing_message: bool = False
def create_outlook_export_content(page: ft.Page):
    message_section = ft.Column([])
    page.on_tab_change = lambda e: ucitaj_df()
    scrollable_container = None

    uploaded_files = []
    upload_complete = False

    upload_dir = "./unos/emails"
    os.makedirs(upload_dir, exist_ok=True)
    page.upload_dir = os.path.abspath(upload_dir)


    def show_message(message, color=ft.Colors.GREEN):
        print(f"Setting message: {message}")
        message_section.controls.clear()
        message_section.controls.append(ft.Text(message, color=color))
        page.update()

    def on_upload_result(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0 and not e.error:
            upload_complete = True
            page.update()
            show_message("Datoteka učitana. Kliknite 'Procesiraj'.", ft.Colors.GREEN)

    def on_file_picker_result(e: ft.FilePickerResultEvent):
        print(f"File picker result: {e}")
        nonlocal uploaded_files, upload_complete
        if e.files:
            uploaded_files = e.files
            upload_complete = False
            page.update()
            print(f"Selected files: {[f.name for f in uploaded_files]}")
            
            try:
                upload_list = []
                for file_obj in uploaded_files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            file_obj.name,
                            upload_url=page.get_upload_url(file_obj.name, 600),
                        )
                    )

                file_picker.upload(upload_list)
                show_message(f"Učitavanje {len(uploaded_files)} datoteka...", ft.Colors.BLUE)
            except Exception as upload_error:
                print(f"Upload error: {upload_error}")
                show_message(f"Greška pri učitavanju: {upload_error}", ft.Colors.RED)
                uploaded_files = []
                upload_complete = False
                page.update()
        else:
            uploaded_files = []
            upload_complete = False
            page.update()
            show_message("Nijedna datoteka nije odabrana.", ft.Colors.RED)

    def process_documents():
        global df

        print(f"Process documents called. Uploaded files: {uploaded_files}")
        print(f"Upload complete: {upload_complete}")

        if not uploaded_files:
            show_message("Nema podatka za izvoz.", ft.Colors.RED)
            return



        if not app_dropdown.value:
            show_message("Molimo odaberite aplikaciju.", ft.Colors.RED)
            return

        try:
            message_section.controls.append(
                ft.Text("Obrađivanje emailova u tijeku...", color=ft.Colors.BLUE)
            )

            upload_dir = "./unos/emails"
            print(f"Processing emails from: {os.path.abspath(upload_dir)}")
            
            from tools.email_parse import get_email_data_with_app
            results = get_email_data_with_app(upload_dir, True, app_dropdown.value)
   
            for file_obj in uploaded_files:
                src_path = os.path.join(upload_dir, file_obj.name)
                try:
                    move_file_to_collector(src_path)
                    print(f"Moved {file_obj.name} to collector.")
                except Exception as move_err:
                    print(f"Error moving {file_obj.name}: {move_err}")

            if results:
                for result in results:
                    result['aplikacija'] = app_dropdown.value

                df = pd.DataFrame(results)
                show_message(f"Uspješno obrađeno {len(results)} pitanja/odgovora!", ft.Colors.GREEN)
                load_df_table()
            else:
                show_message("Nema pronađenih pitanja/odgovora u dokumentima.", ft.Colors.ORANGE)

        except Exception as e:
            show_message(f"Greška pri obrađivanju dokumenata: {e}", ft.Colors.RED)
            print(f"Exception details: {type(e).__name__}: {e}")

    def load_df_table():
        nonlocal scrollable_container
        try:
            columns = [ft.DataColumn(ft.Text(col)) for col in df.columns]

            rows = []
            for index, row in df.iterrows():
                cells = [ft.DataCell(ft.Text(str(row[col])[:100] + "..." if len(str(row[col])) > 100 else str(row[col]))) for col in df.columns]
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

            if scrollable_container:
                outlook_content.controls.remove(scrollable_container)

            scrollable_container = ft.Container(
                content=data_table,
                expand=True,
                padding=10
            )
            outlook_content.controls.append(scrollable_container)
            page.update()

        except Exception as e:
            show_message(f"Greška pri učitavanju podataka: {e}", ft.Colors.RED)

    def clear_data():
        global df
        df = pd.DataFrame(columns=["pitanje", "odgovor", "kontekst", "aplikacija"])
        nonlocal scrollable_container
        if scrollable_container:
            docs_content.controls.remove(scrollable_container)
            scrollable_container = None
        page.update()
        show_message("Podaci su obrisani.", ft.Colors.ORANGE)

    def export_to_main():
        try:
            import frontend.data
            if not df.empty:
                frontend.data.df = pd.concat([frontend.data.df, df], ignore_index=True)
                show_message(f"Izvezeno {len(df)} zapisa u glavnu listu!", ft.Colors.GREEN)
            else:
                show_message("Nema podataka za izvoz.", ft.Colors.ORANGE)
        except Exception as e:
            show_message(f"Greška pri izvozu: {e}", ft.Colors.RED)

    file_picker = ft.FilePicker(
        on_result=on_file_picker_result,
        on_upload=on_upload_result
    )
    page.overlay.append(file_picker)

    app_dropdown = ft.Dropdown(
        label="Aplikacija",
        hint_text="Odaberite aplikaciju",
        options=[ft.dropdown.Option(app["name"], app["name"]) for app in apps],
        width=300,
        enable_filter=True
    )

    upload_btn = ft.ElevatedButton(
        "Učitaj Dokumente", 
        on_click=lambda e: (
            file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=["msg"]
            )
        ),
        icon=ft.Icons.UPLOAD_FILE
    )

    process_btn = ft.ElevatedButton(
        "Procesiraj",
        on_click=lambda e: process_documents(),
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        icon=ft.Icons.PLAY_ARROW
    )

    clear_btn = ft.ElevatedButton(
        "Očisti podatke",
        on_click=lambda e: clear_data(),
        bgcolor=ft.Colors.ORANGE,
        color=ft.Colors.WHITE,
        icon=ft.Icons.CLEAR
    )

    export_btn = ft.ElevatedButton(
        "Izvezi u glavnu listu",
        on_click=lambda e: export_to_main(),
        bgcolor=ft.Colors.GREEN,
        color=ft.Colors.WHITE,
        icon=ft.Icons.IMPORT_EXPORT
    )

    outlook_content = ft.Column([
        message_section,
        ft.Text("Učitavanje i obrada .msg outlook exporta", size=24, weight="bold"),
        ft.Divider(),
        ft.Row([upload_btn, app_dropdown, process_btn], spacing=10, alignment=ft.MainAxisAlignment.START),
        ft.Row([clear_btn, export_btn], spacing=10, alignment=ft.MainAxisAlignment.START),
        ft.Divider(),
        ft.Text("Obrađeni podaci:", size=18, weight="bold"),
    ], expand=True, scroll=ft.ScrollMode.AUTO)

    return outlook_content

actual_uploads_dir = "./unos/emails"
upload_dirs_to_create = ["./unos/emails", "./unos/emails"]
for upload_dir in upload_dirs_to_create:
    os.makedirs(upload_dir, exist_ok=True)
