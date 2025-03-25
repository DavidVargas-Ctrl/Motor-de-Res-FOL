from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Inicia Chrome sin cargar perfil
driver = webdriver.Edge()

driver.get("https://gemini.google.com/app?hl=es")
print("Tienes 20 segundos para iniciar sesión manual si es necesario...")
time.sleep(60)

# Encuentra la caja de entrada correcta de Gemini
input_box = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']"))
)

mi_prompt = """
Convierte los siguientes enunciados en lenguaje natural a cláusulas de primer orden (FOL) en formato de conjuntos de literales de Python:
Ejemplo: {"~Ama(x, y)", "Animal(y)", "EsAmadoPorAlguien(x)"}

Texto:
Marco es un hombre.
Marco es un Pompeyano.
Todos los Pompeyanos son Romanos.
César es un gobernante.
Todos los Romanos son o leales al César o odian al César.
La gente sólo intenta asesinar a los gobernantes a los que no es leal.
Marco intentó asesinar al César.

Devuélvelo como una lista de conjuntos de literales (list of sets), sin explicaciones.
"""

# Usa JavaScript para insertar todo el texto (más confiable en contenteditable)
driver.execute_script("arguments[0].innerText = arguments[1];", input_box, mi_prompt)

# Simula presionar Enter para enviar
input_box.send_keys(Keys.ENTER)

print("Prompt enviado a Gemini. Esperando respuesta...")
time.sleep(25)  # Ajusta el tiempo según la longitud de la respuesta

# Opcional: Espera la respuesta (ajusta el selector si es necesario)
respuesta = WebDriverWait(driver, 25).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.markdown"))
)

print("\nRespuesta de Gemini:\n", respuesta.text)

# Guarda la respuesta
with open("respuesta_gemini.txt", "w", encoding="utf-8") as f:
    f.write(respuesta.text)

driver.quit()
