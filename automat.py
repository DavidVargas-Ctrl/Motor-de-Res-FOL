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
time.sleep(40)

# Encuentra la caja de entrada correcta de Gemini
input_box = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']"))
)

# Lee el contenido del archivo
with open("conocimiento.txt", "r", encoding="utf-8") as file:
    texto = file.read()

mi_prompt = f"""
A partir del siguiente conjunto de enunciados en lenguaje natural, realiza los siguientes pasos de forma estricta:

1. Convierte cada enunciado a su representación en Lógica de Primer Orden (FOL).
2. Transforma todas las fórmulas a su Forma Normal Conjuntiva (CNF), asegurándote de aplicar completamente los pasos necesarios: eliminación de implicaciones, movimiento de negaciones, estandarización de variables, skolemización, eliminación de cuantificadores y distribución adecuada de disyunciones sobre conjunciones.
3. Expresa el resultado final **únicamente** como una lista de **cláusulas en CNF**, donde:
   - Cada cláusula debe ser un conjunto de literales en formato de Python, como: {{"~Ama(x, y)", "Animal(y)", "EsAmadoPorAlguien(x)"}}.
   - Si la cláusula contiene un solo literal, escríbela igualmente como un conjunto con un solo elemento: {{"Gobernante(Cesar)"}}.
   - No debe aparecer ningún cuantificador como ∀ o ∃ en las cláusulas finales.
   - No debe haber fórmulas con implicaciones (->) ni conectivos fuera de los conjuntos.
   - Cada literal debe estar escrito como Predicado(argumentos), usando estilo PascalCase para los predicados.

4. Es fundamental que la CNF esté completamente desarrollada. Por ejemplo:
   - Si el enunciado dice "La gente sólo intenta asesinar a los gobernantes a los que no es leal", entonces la cláusula resultante debe ser: {{"~Hombre(x)", "~Gobernante(y)", "~IntentaAsesinar(x, y)", "~Leal(x, y)"}}.

5. Al final, agrega como **última cláusula** la **negación exacta** de la pregunta que se quiere demostrar.

Texto:
{texto}

Devuélvelo exclusivamente como una lista de conjuntos de literales en formato de Python, sin encabezados, sin lenguaje natural y sin explicaciones adicionales. Asegúrate de que sea directamente interpretable por código Python usando ast.literal_eval.
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

# Ajusta el formato (elimina la primera línea si es "Python")
with open("respuesta_gemini.txt", "r", encoding="utf-8") as f:
    gemini_output = f.read()

lines = gemini_output.splitlines()
if lines and lines[0].strip() == "Python":
    gemini_output = "\n".join(lines[1:])

with open("respuesta_gemini_ajustada.txt", "w", encoding="utf-8") as f:
    f.write(gemini_output)

print("La respuesta ajustada se ha guardado en 'respuesta_gemini_ajustada.txt'.")

driver.quit()

