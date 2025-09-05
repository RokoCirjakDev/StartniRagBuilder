import flet as ft
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.doc_parse import get_doc_data_with_app_id
import asyncio
from .collector import move_file_to_collector
from frontend.applist import apps
from frontend.set_message import settimeoutmessage, setloading

df = pd.DataFrame(columns=["pitanje", "odgovor", "kontekst", "aplikacija"])
sharing_message: bool = False
def create_docs_content(page: ft.Page):
    message_section = ft.Column([])
    page.on_tab_change = lambda e: ucitaj_df()
    scrollable_container = None

    uploaded_files = []
    upload_complete = False

    upload_dir = "../unos/dokumentacija"
    os.makedirs(upload_dir, exist_ok=True)
    page.upload_dir = os.path.abspath(upload_dir)

    
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

    def on_upload_result(e: ft.FilePickerUploadEvent):
        nonlocal upload_complete
        print(f"Upload result: {e}")
        print(f"File name: {e.file_name}")
        print(f"Progress: {e.progress}")
        print(f"Error: {e.error}")

        if e.error:
            show_error(f"Greška pri učitavanju datoteke {e.file_name}: {e.error}", ft.Colors.RED)
            upload_complete = False
        elif e.progress == 1.0:
            import time
            max_attempts = 5
            attempt = 0

            uploaded_file_names = [f.name for f in uploaded_files]
            show_loading(f"Provjera učitavanja datoteke {e.file_name}...")
            while attempt < max_attempts:
                time.sleep(0.5)

                abs_upload_dir = os.path.abspath(upload_dir)
                print(f"Checking absolute path: {abs_upload_dir}")

                if os.path.exists(abs_upload_dir):
                    actual_files = os.listdir(abs_upload_dir)
                    print(f"Attempt {attempt + 1} - Checking {abs_upload_dir}:")
                    print(f"  Files found: {actual_files}")


                    all_uploaded = all(fname in actual_files for fname in uploaded_file_names)
                    if all_uploaded:
                        upload_complete = True
                        page.update()
                       
                        return
                else:
                    print(f"Directory {abs_upload_dir} does not exist")

                attempt += 1

            default_uploads = ["./unos/dokumentacija"]
            for default_dir in default_uploads:
                if os.path.exists(default_dir):
                    files_in_default = os.listdir(default_dir)
                    print(f"Files found in {default_dir}: {files_in_default}")

                    for file_name in uploaded_file_names:
                        if file_name in files_in_default:
                            src_path = os.path.join(default_dir, file_name)
                            dst_path = os.path.join(upload_dir, file_name)
                            try:
                                import shutil
                                shutil.move(src_path, dst_path)
                                upload_complete = True
                                page.update()
                                end_loading(f"Svi dokumenti su uspješno učitani ({len(uploaded_file_names)} datoteka). Odaberite aplikaciju i kliknite 'Procesiraj'.")
                                return
                            except Exception as move_error:
                                print(f"Error moving file: {move_error}")

            show_error(f"Datoteka {e.file_name} nije pronađena nakon učitavanja. Molimo pokušajte ponovno.", ft.Colors.RED)
            upload_complete = False
            page.update()

    def on_file_picker_result(e: ft.FilePickerResultEvent):
        print(f"File picker result: {e}")
        nonlocal uploaded_files, upload_complete
        if e.files:
            uploaded_files = e.files
            upload_complete = False
            page.update()
            print(f"Selected files: {[f.name for f in uploaded_files]}")

            try:
                show_loading(f"Učitavanje {len(uploaded_files)} datoteka...", ft.Colors.BLUE)
                upload_list = []
                for file_obj in uploaded_files:
                    upload_list.append(
                        ft.FilePickerUploadFile(
                            file_obj.name,
                            upload_url=page.get_upload_url(file_obj.name, 600),
                        )
                    )

                file_picker.upload(upload_list)
                end_loading(f"Učitavanje {len(uploaded_files)} datoteka zavrseno...", ft.Colors.BLUE)
            except Exception as upload_error:
                print(f"Upload error: {upload_error}")
                show_error(f"Greška pri učitavanju: {upload_error}", ft.Colors.RED)
                uploaded_files = []
                upload_complete = False
                page.update()
        else:
            uploaded_files = []
            upload_complete = False
            page.update()
            show_error("Nijedna datoteka nije odabrana.", ft.Colors.RED)

    def process_documents():
        global df
        upload_dir = "../unos/dokumentacija"

        print(f"Process documents called. Uploaded files: {uploaded_files}")
        print(f"Upload complete: {upload_complete}")

        if not uploaded_files:
            show_error("Nema podataka za izvoz.", ft.Colors.RED)
            return

        if not upload_complete:
            while not upload_complete:
                print("Waiting for upload to complete...")
                show_message("Čekanje na završetak učitavanja...", ft.Colors.ORANGE)


        if not app_dropdown.value:
            show_error("Molimo odaberite aplikaciju.", ft.Colors.RED)
            return

        try:
            show_loading("Obrada dokumenata...", ft.Colors.BLUE)

            
            print(f"Processing documents from: {os.path.abspath(upload_dir)}")

            from tools.doc_parse import get_doc_data_with_app_id
            
            results = get_doc_data_with_app_id(upload_dir, True, int(app_dropdown.value))

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
                end_loading("Emailovi obrađeni. Učitavanje podataka u tablicu...", ft.Colors.GREEN)
                load_df_table()
            else:
                show_error("Nema pronađenih pitanja/odgovora u dokumentima.", ft.Colors.ORANGE)

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
                docs_content.controls.remove(scrollable_container)

            scrollable_container = ft.Container(
                content=data_table,
                expand=True,
                padding=10
            )
            docs_content.controls.append(scrollable_container)
            page.update()

        except Exception as e:
            show_error(f"Greška pri učitavanju podataka: {e}", ft.Colors.RED)

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
                show_message("Nema podatka za izvoz.", ft.Colors.RED)
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
        options=[ft.dropdown.Option(str(app["id"]), app["name"]) for app in apps],
        width=300,
        enable_filter=True
    )

    upload_btn = ft.ElevatedButton(
        "Učitaj Dokumente", 
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["docx"]
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

    docs_content = ft.Column([
        message_section,
        ft.Text("Učitavanje i obrada dokumenata", size=24, weight="bold"),
        ft.Divider(),
        ft.Row([upload_btn, app_dropdown, process_btn], spacing=10, alignment=ft.MainAxisAlignment.START),
        ft.Row([clear_btn, export_btn], spacing=10, alignment=ft.MainAxisAlignment.START),
        ft.Divider(),
        ft.Text("Obrađeni podaci:", size=18, weight="bold"),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
    load_df_table()
    page.update()
    return docs_content

actual_uploads_dir = "../unos/dokumentacija"
upload_dirs_to_create = ["../unos/dokumentacija"]
for upload_dir in upload_dirs_to_create:
    os.makedirs(upload_dir, exist_ok=True)
