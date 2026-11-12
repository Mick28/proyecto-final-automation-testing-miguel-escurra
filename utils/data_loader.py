"""Lectura de datos de prueba desde archivos externos (CSV y JSON).

Separar los datos del código permite agregar casos nuevos editando
solo los archivos de la carpeta datos/, sin tocar los tests.
"""
import csv
import json

from utils.config import DATA_DIR


def read_csv(file_name: str) -> list[dict]:
    """Lee un CSV de datos/ y devuelve una lista de diccionarios (uno por fila)."""
    with open(DATA_DIR / file_name, encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def read_json(file_name: str):
    """Lee un JSON de datos/ y devuelve su contenido (lista o diccionario)."""
    with open(DATA_DIR / file_name, encoding="utf-8") as json_file:
        return json.load(json_file)
