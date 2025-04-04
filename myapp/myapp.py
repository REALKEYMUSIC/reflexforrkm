import reflex as rx
import pandas as pd
import io

class State(rx.State):
    resumen: str = ""
    error: str = ""

   def analizar_csv(self, files: list[rx.UploadFile]):
    if rx.utils.exporting.is_exporting():
        # No procesar durante el build/export
        return

    try:
        file = files[0]
        content = file.file.read()
        df = pd.read_csv(io.BytesIO(content))

        if "assetTitle" not in df.columns or "partnerRevenue" not in df.columns:
            self.error = "El CSV debe contener las columnas 'assetTitle' y 'partnerRevenue'"
            return

        resumen = df.groupby("assetTitle")["partnerRevenue"].sum().reset_index()
        resumen = resumen.sort_values(by="partnerRevenue", ascending=False)

        self.resumen = resumen.to_string(index=False)
        self.error = ""
    except Exception as e:
        self.error = str(e)

def index():
    return rx.container(
        rx.vstack(
            rx.heading("Análisis de CSV MLC 📊", size="lg"),
            rx.text("Sube un archivo CSV con columnas 'assetTitle' y 'partnerRevenue'"),
            rx.upload(
                rx.button("Seleccionar CSV", color="blue"),
                id="csv-uploader",
                max_files=1,
                on_upload=State.analizar_csv,
            ),
            rx.cond(State.error != "", rx.text(State.error, color="red")),
            rx.cond(State.resumen != "", rx.code_block(State.resumen, language="text")),
            spacing="4",
        ),
        padding="6",
    )

app = rx.App()
app.add_page(index)
