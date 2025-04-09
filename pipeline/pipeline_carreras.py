import src.extract as ext

def run():
    provincias = [
        "andalucia", "navarra", "asturias","aragon","canarias", "cantabria", "castilla-la-mancha",
        "castilla-y-leon", "catalunya", "ceuta" , "euskadi", "extremadura", "galicia" , "illes-balears",
        "la-rioja", "madrid", "melilla" , "murcia", "valencia"  
    ]

    fecha_inicio = "2024-04"

    for provincia in provincias:
        print(f"\n⏳ Iniciando extracción para: {provincia}")
        df = ext.obtener_carreras(provincia, fecha_inicio)

        if not df.empty:
            ext.guardar_csv(df, provincia)
        else:
            print(f"⚠️ No se encontraron carreras para {provincia}")

