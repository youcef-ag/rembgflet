import os
import tempfile

from PIL import Image
from rembg import new_session, remove
import flet as ft


def main(page: ft.Page):
    page.title = "Suppression d'arrière-plan"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10  # Reduced padding for mobile
    page.scroll = ft.ScrollMode.ADAPTIVE  # Enable scrolling for smaller screens

    # Remove fixed window sizes to allow responsiveness
    # page.window.width = 600
    # page.window.height = 800

    input_path = output_path = None
    session = None

    models = {
        "u2net": "Modèle général",
        "u2netp": "Version légère de u2net",
        "u2net_human_seg": "Segmentation humaine",
        "u2net_cloth_seg": "Segmentation de vêtements",
        "silueta": "Version réduite de u2net",
        "isnet-general-use": "Nouveau modèle général",
        "isnet-anime": "Segmentation pour anime",
        "sam": "Modèle polyvalent (SAM)",
        "birefnet-general": "Modèle général BiRefNet",
        "birefnet-general-lite": "Modèle général BiRefNet léger",
        "birefnet-portrait": "Portraits humains BiRefNet",
        "birefnet-dis": "Segmentation dichotomique BiRefNet",
        "birefnet-hrsod": "Détection d'objets saillants HR BiRefNet",
        "birefnet-cod": "Détection d'objets cachés BiRefNet",
        "birefnet-massive": "BiRefNet avec jeu de données massif"
    }

    def handle_file_result(e: ft.FilePickerResultEvent, is_save: bool):
        nonlocal input_path, output_path
        if is_save and e.path and output_path:
            os.rename(output_path, e.path)
            output_path = e.path
        elif not is_save and e.files:
            input_path = e.files[0].path
            original_image.src = input_path
            original_image.update()
            remove_background_button.disabled = False
            page.update()

    pick_files_dialog = ft.FilePicker(on_result=lambda e: handle_file_result(e, False))
    save_file_dialog = ft.FilePicker(on_result=lambda e: handle_file_result(e, True))
    page.overlay.extend([pick_files_dialog, save_file_dialog])

    def process_image(_):
        nonlocal output_path, session
        if input_path:
            model_name = model_dropdown.value
            session = new_session(model_name)

            with Image.open(input_path) as input_image:
                if model_name == "sam":
                    input_points = [[0, 0], [input_image.width - 1, input_image.height - 1]]
                    input_labels = [1, 1]
                    output_image = remove(
                        input_image,
                        session=session,
                        input_points=input_points,
                        input_labels=input_labels
                    )
                else:
                    output_image = remove(input_image, session=session)

                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    output_path = temp_file.name
                    output_image.save(output_path)

            processed_image.src = output_path
            processed_image.update()
            export_button.disabled = False
            page.update()

    upload_button = ft.ElevatedButton(
        "Charger une image",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: pick_files_dialog.pick_files(
            allow_multiple=False,
            allowed_extensions=['png', 'jpg', 'jpeg']
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(left=10, right=10, top=8, bottom=8)  # Adjusted padding
        )
    )

    remove_background_button = ft.ElevatedButton(
        "Supprimer l'arrière-plan",
        icon=ft.icons.AUTO_FIX_HIGH,
        on_click=process_image,
        disabled=True,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(left=10, right=10, top=8, bottom=8)
        )
    )

    export_button = ft.ElevatedButton(
        "Exporter l'image",
        icon=ft.icons.DOWNLOAD,
        on_click=lambda _: save_file_dialog.save_file(
            file_name="image_sans_fond.png",
            allowed_extensions=['png']
        ),
        disabled=True,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(left=10, right=10, top=8, bottom=8)
        )
    )

    model_dropdown = ft.Dropdown(
        label="Choisir un modèle",
        options=[ft.dropdown.Option(key, value) for key, value in models.items()],
        value="u2net",
        width=250,  # Reduced width for mobile
        expand=True,  # Allow dropdown to take available space
        text_size=12  # Reduced font size for dropdown options
    )

    def create_image_container(title):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Image(
                     # Reduced size for mobile
                    height=200,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=ft.border_radius.all(8)
                ),
            ]),
            padding=5,
            margin=5,
            border_radius=8,
            border=ft.border.all(1, ft.colors.OUTLINE),
             # Consistent width
        )

    original_image_container = create_image_container("Image originale")
    processed_image_container = create_image_container("Image traitée")
    original_image = original_image_container.content.controls[1]
    processed_image = processed_image_container.content.controls[1]

    # Use SingleColumn layout for mobile
    page.add(
        ft.AppBar(
            title=ft.Text("Suppression d'arrière-plan", color=ft.colors.WHITE, size=16),
            bgcolor=ft.colors.BLUE,
            center_title=True,
        ),
        ft.Column([
            upload_button,
            model_dropdown,
            original_image_container,
            remove_background_button,
            processed_image_container,
            export_button
        ], alignment=ft.MainAxisAlignment.START, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )


ft.app(target=main)  # Use web browser view for better mobile compatibility
