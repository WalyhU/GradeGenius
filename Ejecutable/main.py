try:
    import os
    import openai
    import openpyxl
    import docx2txt
    import PyPDF2
    import re
    import split_tokens
    import pymongo
    import sys
except Exception as e:
    print("Algunos paquetes no han sido encontrados {}".format(e))

# Configuración de OpenAI (necesitas una API key)
openai.api_key = os.getenv("OpenAI")

# Función para procesar cada archivo


def procesar_archivo(ruta_archivo, tema, categoria):
    # Leer el contenido del archivo
    if ruta_archivo.endswith(".txt"):
        with open(ruta_archivo, "r") as archivo:
            contenido = archivo.read()
    elif ruta_archivo.endswith(".docx"):
        contenido = docx2txt.process(ruta_archivo)
    elif ruta_archivo.endswith(".xlsx"):
        libro = openpyxl.load_workbook(ruta_archivo)
        hoja = libro.active
        contenido = "\n".join([str(celda.value) for celda in hoja[1]])
    elif ruta_archivo.endswith(".pdf"):
        with open(ruta_archivo, "rb") as archivo:
            lector = PyPDF2.PdfReader(archivo)
            contenido = "\n".join([pagina.extract_text()
                                  for pagina in lector.pages])
    contenido = f"Acá está el contenido a evaluar: {contenido}"
    fragments = split_tokens.break_up_file_to_chunks(contenido)
    respuesta = ''
    for i, fragment in enumerate(fragments):
        # Juntar todos los tokens de un chunk en un string
        fragment = " ".join(fragment)
        # Remover los saltos de línea
        fragment = re.sub(r"\n", " ", fragment)
        # Remover los espacios dobles
        fragment = re.sub(r"  ", " ", fragment)
        # Remover los espacios al inicio y al final
        fragment = fragment.strip()
        messages = [
            {"role": "system",
                "content": f"Eres un sistema que califica tareas para estudiantes. Necesito que evalúes el tema: {tema} de la categoría {categoria}. Realiza una nota tentativa, retorna la respuesta en el siguiente formato.: Nombre del alumno: |Nombre del Alumno| Carnet: |Carnet del alumno (xxxx-xx-xxxx) los ultimos numeros pueden ser de 4 a 6 digitos más o menos| Resumen: |Un muy pequeño resumen de lo que se trata el contenido| Nota: |Una nota tentativa ej. Nota: 89%|."},
            {"role": "system", "content": "No necesito nada más, únicamente ese formato, voy a usarlo para extraer los datos en un lenguaje de programación. Si no se proporcionan los suficientes datos, no respondas absolutamente nada, a lo mucho pon un punto."}, {
                "role": "user", "content": fragment}
        ]
        # Resumir el contenido y calificar la tarea usando OpenAI
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1
        )
        r = str(res['choices'][0]['message']['content'])
        respuesta += r

    # Recorrer la respuesta y mostrar el indice
    if len(respuesta.split("| ")) >= 4:
        respuesta = respuesta.split("| ")
    elif len(respuesta.split("\n ")) >= 4:
        respuesta = respuesta.split("\n ")
    elif len(respuesta.split(" | ")) >= 4:
        respuesta = respuesta.split("\n ")
    else:
        print(respuesta)
        return ("na", "na", "na", "na")
    resumen = respuesta[2]
    calificacion = respuesta[3]

    # Extraer el nombre y el carnet del contenido
    nombre = respuesta[0]
    carnet = respuesta[1]

    # Devolver los resultados como una tupla
    return (nombre, carnet, resumen, calificacion)

# Función principal del programa


def main(carpeta, tema, categoria):
    # Conectarse a la base de datos de mongodb
    cliente = pymongo.MongoClient(os.getenv("MONGO_URI"))
    base_de_datos = cliente["ProyectoFinal"]

    # Obtener la lista de archivos en la carpeta
    archivos = [os.path.join(carpeta, nombre) for nombre in os.listdir(
        carpeta) if nombre.endswith((".txt", ".docx", ".xlsx", ".pdf"))]

    # Procesar cada archivo y agregar los datos a la base de datos
    for archivo in archivos:
        nombre, carnet, resumen, calificacion = procesar_archivo(
            archivo, tema, categoria)

        # Insertar los datos en la base de datos
        if nombre == "na" and carnet == "na" and resumen == "na" and calificacion == "na":
            print("na")
            return
        else:
            base_de_datos["Tareas"].insert_one({
                "nombre": nombre,
                "carnet": carnet,
                "resumen": resumen,
                "calificacion": calificacion,
                "tema": tema,
                "categoria": categoria
            })
            print("True")


# Este programa sera corrido desde un programa en C# que manda los argumentos mediante procesos
# Ejecuta la funcion principal con los argumentos recibidos
main(sys.argv[1], sys.argv[2], sys.argv[3])
