import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup


def obtener_html(provincia, fecha, pagina):
    url = f"https://runedia.mundodeportivo.com/calendario-carreras/espana/{provincia}/provincia/tipo/distancia/{fecha}/0/0/{pagina}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error en la página {pagina} de {provincia}, status: {response.status_code}")
        return None


def parsear_caja_carrera(div, provincia):
    try:
        dia = div.find("span", class_="dia").text.strip()
        mes = div.find("span", class_="mes").text.strip()
    except:
        dia, mes = None, None

    try:
        enlace_tag = div.find("a", class_="nom-cursa")
        titulo = enlace_tag.text.strip()
        enlace = enlace_tag["href"]
    except:
        titulo, enlace = None, None

    try:
        localidad = div.find("span", class_="lloc").text.strip()
    except:
        localidad = None

    try:
        spans = div.find_all("span")
        tipo = spans[-2].text.strip() if len(spans) >= 2 else None
        distancia = spans[-1].text.strip() if len(spans) >= 1 else None
    except:
        tipo, distancia = None, None

    return {
        "dia": dia,
        "mes": mes,
        "titulo": titulo,
        "enlace": f"https://runedia.mundodeportivo.com{enlace}" if enlace and enlace.startswith("/") else enlace,
        "localidad": localidad,
        "tipo": tipo,
        "distancia": distancia,
        "provincia": provincia
    }


def obtener_carreras(provincia, fecha):
    todas = []
    pagina = 1
    while True:
        print(f"Scrapeando página {pagina} de {provincia} ({fecha})")
        html = obtener_html(provincia, fecha, pagina)
        if html is None:
            break

        soup = BeautifulSoup(html, "html.parser")
        cajas = soup.find_all("div", class_="item-cursa")
        if len(cajas) == 0:
            print("Fin de resultados (no hay más carreras en esta página).")
            break

        carreras_pagina = [parsear_caja_carrera(div, provincia) for div in cajas]
        todas.extend(carreras_pagina)

        pagina += 1
        time.sleep(1)

    return pd.DataFrame(todas)


def guardar_csv(df, provincia):
    ruta = f"data/raw/carreras-{provincia}.csv"
    df.to_csv(ruta, index=False)
    print(f"Archivo guardado: {ruta}")

