import flet as ft
import os
import time
import httpx

def main(page: ft.Page):
    page.title = "Remove Background App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file.value = e.files[0].name
            selected_file.update()
            remove_bg_button.disabled = False
            remove_bg_button.update()

    async def remove_background(e):
        if selected_file.value:
            file_path = pick_files_dialog.result.files[0].path
            
            async with httpx.AsyncClient() as client:
                with open(file_path, "rb") as file:
                    files = {"file": (os.path.basename(file_path), file, "image/png")}
                    response = await client.post(
                        "https://apitoflet.newposts.duckdns.org/remove-background/",
                        files=files
                    )
            
            if response.status_code == 200:
                export_filename = response.headers.get('Export-Filename', 'image_sans_fond.png')
                
                timestamp = int(time.time() * 1000)
                temp_file_path = f"temp_image_{timestamp}.png"
                
                with open(temp_file_path, "wb") as f:
                    f.write(response.content)
                
                image.src = temp_file_path
                image.visible = True
                save_button.disabled = False
                
                remove_background.export_filename = export_filename
                remove_background.temp_file_path = temp_file_path
                
                if hasattr(remove_background, 'previous_temp_file'):
                    try:
                        os.remove(remove_background.previous_temp_file)
                    except:
                        pass
                remove_background.previous_temp_file = temp_file_path
                
                page.update()  # Changé de update_async() à update()
            else:
                print(f"Erreur lors de la suppression de l'arrière-plan: {response.status_code}")

    def save_image(e):
        if hasattr(remove_background, 'export_filename') and hasattr(remove_background, 'temp_file_path'):
            save_file_dialog.save_file(file_name=remove_background.export_filename)

    def save_file_result(e: ft.FilePickerResultEvent):
        if e.path and hasattr(remove_background, 'temp_file_path'):
            os.rename(remove_background.temp_file_path, e.path)
            print(f"Image sauvegardée : {e.path}")
            remove_background.temp_file_path = None

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    save_file_dialog = ft.FilePicker(on_result=save_file_result)
    selected_file = ft.Text()

    page.overlay.extend([pick_files_dialog, save_file_dialog])

    image = ft.Image(visible=False, width=300, height=300, fit=ft.ImageFit.CONTAIN)

    remove_bg_button = ft.ElevatedButton("Supprimer l'arrière-plan", on_click=remove_background, disabled=True)
    save_button = ft.ElevatedButton("Sauvegarder l'image", on_click=save_image, disabled=True)

    page.add(
        ft.ElevatedButton(
            "Choisir une image",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=False),
        ),
        selected_file,
        remove_bg_button,
        image,
        save_button
    )

ft.app(target=main)
