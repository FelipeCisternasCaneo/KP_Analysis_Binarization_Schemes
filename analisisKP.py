import os
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import glob

from statsmodels.stats.diagnostic import lilliefors
from scipy.stats import mannwhitneyu, wilcoxon, shapiro, friedmanchisquare, rankdata

from Util.util import cargar_configuracion_exp, writeTofile
from BD.sqlite import BD
from Util.log import escribir_resumenes

# === Parámetros generales ===
GENERAR_DATA = False
GENERAR_GRAFICOS_DISTRIBUCION = False
GENERAR_RPD = False
GENERAR_ANALITICA_BEST_FAMILIA = False
GRAFICOS_BEST_FAMILIA = False
TEST_ESTADISTICO = True
COLORS = ['r', 'g']

# === Inicialización ===
bd = BD()

def generar_matrices_victorias(carpeta_datos, carpeta_resultados, mh, tipo_problema='max'):
    """
    Genera tablas comparativas (Conteos y Porcentajes) indicando cuántas veces 
    un algoritmo fue ESTADÍSTICAMENTE MEJOR que otro en todas las instancias.
    """
    print(f"Buscando archivos en: {carpeta_datos}...")
    archivos_csv = glob.glob(os.path.join(carpeta_datos, "*.csv"))
    num_instancias = len(archivos_csv)
    
    if num_instancias == 0:
        print("⚠️ No se encontraron archivos CSV.")
        return
        
    print(f"Se encontraron {num_instancias} instancias. Procesando combates estadísticos...\n")
    
    # 1. Identificar todos los algoritmos únicos
    algoritmos = set()
    for archivo in archivos_csv:
        df = pd.read_csv(archivo)
        if 'Family' in df.columns:
            algoritmos.update(df['Family'].unique())
    
    algoritmos = sorted(list(algoritmos))
    
    # 2. Inicializar matriz de victorias con ceros
    matriz_victorias = {alg_A: {alg_B: 0 for alg_B in algoritmos} for alg_A in algoritmos}
    
    # 3. Evaluar instancia por instancia
    for archivo in archivos_csv:
        df = pd.read_csv(archivo)
        
        if 'Family' not in df.columns or 'Data' not in df.columns:
            continue
            
        grupos = df.groupby('Family')
        
        # Comparar todos contra todos en esta instancia
        for alg_A in algoritmos:
            for alg_B in algoritmos:
                if alg_A == alg_B:
                    continue
                
                # Verificar que ambos algoritmos tengan datos en esta instancia
                if alg_A in grupos.groups and alg_B in grupos.groups:
                    datos_A = grupos.get_group(alg_A)['Data'].dropna()
                    datos_B = grupos.get_group(alg_B)['Data'].dropna()
                    
                    # Evitar errores si los datos son idénticos o insuficientes
                    if len(datos_A) < 3 or len(datos_B) < 3 or (datos_A.values == datos_B.values).all():
                        continue
                    
                    # Prueba estadística de Mann-Whitney (Wilcoxon Rank-Sum)
                    estadistico, p_value = mannwhitneyu(datos_A, datos_B, alternative='two-sided')
                    
                    # Condición de victoria: Diferencia significativa Y mejor mediana
                    if p_value < 0.05:
                        mediana_A = datos_A.median()
                        mediana_B = datos_B.median()
                        
                        if tipo_problema == 'max' and mediana_A > mediana_B:
                            matriz_victorias[alg_A][alg_B] += 1
                        elif tipo_problema == 'min' and mediana_A < mediana_B:
                            matriz_victorias[alg_A][alg_B] += 1

    # 4. Construir DataFrames con el formato exacto requerido
    df_conteos = pd.DataFrame(index=algoritmos, columns=algoritmos)
    df_porcentajes = pd.DataFrame(index=algoritmos, columns=algoritmos)
    
    for alg_A in algoritmos:
        for alg_B in algoritmos:
            if alg_A == alg_B:
                df_conteos.at[alg_A, alg_B] = 'X'
                df_porcentajes.at[alg_A, alg_B] = 'X'
            else:
                victorias = matriz_victorias[alg_A][alg_B]
                # Formato: 3/15
                df_conteos.at[alg_A, alg_B] = f"{victorias}/{num_instancias}"
                # Formato: 20.00%
                porcentaje = (victorias / num_instancias) * 100
                df_porcentajes.at[alg_A, alg_B] = f"{porcentaje:.2f}%"

    # Nombrar el índice como en tu ejemplo
    df_conteos.index.name = 'vs'
    df_porcentajes.index.name = 'vs'
    
    # 5. Guardar los resultados en CSV
    os.makedirs(carpeta_resultados, exist_ok=True)
    ruta_conteos = os.path.join(carpeta_resultados, f"{mh}_Tabla_Victorias_Conteos.csv")
    ruta_porcentajes = os.path.join(carpeta_resultados, f"{mh}_Tabla_Victorias_Porcentajes.csv")
    
    df_conteos.to_csv(ruta_conteos)
    df_porcentajes.to_csv(ruta_porcentajes)
    
    # Mostrar resultados en consola
    print("=" * 65)
    print("TABLA 1: CUENTA DIRECTA (Victorias / Total Instancias)")
    print("=" * 65)
    print(df_conteos.to_string())
    
    print("\n" + "=" * 65)
    print("TABLA 2: PORCENTAJES DE VICTORIAS ESTADÍSTICAS")
    print("=" * 65)
    print(df_porcentajes.to_string())
    
    print(f"\n✅ Archivos exportados con éxito en la carpeta: {carpeta_resultados}")

def test_friedman_rankings(carpeta_datos, carpeta_resultados, mh, tipo_problema='max'):
    """
    Lee los CSV de instancias, calcula la mediana, aplica Friedman 
    y genera una tabla con los RANKINGS por instancia para cada variante.
    """
    print(f"\n[INFO] Iniciando análisis de Friedman y Rankings para {mh}...")
    print(f"Buscando archivos en: {carpeta_datos}...")
    ruta_busqueda = os.path.join(carpeta_datos, "*.csv")
    archivos_csv = glob.glob(ruta_busqueda)
    
    if not archivos_csv:
        print("⚠️ Advertencia: No se encontraron archivos CSV en el directorio.")
        return None, None
        
    diccionario_medianas = {}
    
    for archivo in archivos_csv:
        nombre_instancia = os.path.basename(archivo).replace('.csv', '')
        df = pd.read_csv(archivo)
        
        # Agrupar por variante y calcular la mediana
        if 'Family' in df.columns and 'Data' in df.columns:
            medianas_instancia = df.groupby('Family')['Data'].median()
            diccionario_medianas[nombre_instancia] = medianas_instancia
            
    # Matriz de medianas original
    df_medianas = pd.DataFrame(diccionario_medianas).T
    df_medianas = df_medianas.dropna(axis=1)
    
    # 1. Ejecutar Test de Friedman sobre las medianas
    estadistico, p_value = friedmanchisquare(*[df_medianas[col] for col in df_medianas.columns])
    
    # 2. Transformar la matriz de medianas en MATRIZ DE RANKINGS
    if tipo_problema == 'max':
        # En maximización, el mayor valor recibe el ranking 1
        matriz_rangos = [rankdata(-fila) for fila in df_medianas.values]
    else:
        # En minimización, el menor valor recibe el ranking 1
        matriz_rangos = [rankdata(fila) for fila in df_medianas.values]
        
    df_rankings = pd.DataFrame(matriz_rangos, index=df_medianas.index, columns=df_medianas.columns)
    
    # 3. Calcular los Rankings Promedio Globales
    rankings_promedio = df_rankings.mean().sort_values()
    
    # 4. Agregar la fila de promedios al final de la tabla de rankings
    df_rankings.loc['Ranking_Promedio'] = rankings_promedio
    
    # Formatear la tabla final para que los rankings tengan 2 decimales (útil para empates)
    df_rankings_formateada = df_rankings.apply(lambda col: col.map(lambda x: f"{x:.2f}"))
    
    # Guardar el archivo CSV
    os.makedirs(carpeta_resultados, exist_ok=True)
    ruta_salida = os.path.join(carpeta_resultados, f"{mh}_Tabla_Rankings_Friedman.csv")
    df_rankings_formateada.to_csv(ruta_salida)
    
    # ==========================================
    # REPORTE DE RESULTADOS
    # ==========================================
    # Guardar TXT con el P-Value
    ruta_txt = os.path.join(carpeta_resultados, f"{mh}_P_Value_Friedman.csv")
    with open(ruta_txt, 'w', encoding='utf-8') as archivo_texto:
        archivo_texto.write("Resultados del Test de Friedman\n")
        archivo_texto.write("===============================\n")
        archivo_texto.write(f"Estadistico Chi-cuadrado : {estadistico:.4f}\n")
        archivo_texto.write(f"P-Value global           : {p_value:.4e}\n")
        archivo_texto.write("\nConclusion:\n")
        if p_value < 0.05:
            archivo_texto.write("Existen diferencias estadisticamente significativas (p < 0.05).\n")
        else:
            archivo_texto.write("NO existen diferencias significativas (p >= 0.05).\n")

    # return df_rankings_formateada, rankings_promedio

def analisis_normalidad_masivo(carpeta_datos, carpeta_resultados, mh):
    """
    Lee todos los CSV de una carpeta, aplica Shapiro-Wilk a las 31 ejecuciones 
    de cada variante y genera un reporte global.
    """
    print(f"Buscando archivos CSV en: {carpeta_datos}...")
    
    # Busca todos los archivos .csv en el directorio indicado
    ruta_busqueda = os.path.join(carpeta_datos, "*.csv")
    archivos_csv = glob.glob(ruta_busqueda)
    
    if not archivos_csv:
        print("⚠️ No se encontraron archivos CSV en la carpeta indicada.")
        return
    
    lista_resultados = []
    
    for archivo in archivos_csv:
        # Extrae el nombre del archivo sin la extensión (ej: knapPI_1_10000_1000_1)
        nombre_instancia = os.path.basename(archivo).replace('.csv', '')
        df = pd.read_csv(archivo)
        
        # Validamos que el archivo tenga las columnas esperadas
        if 'Family' in df.columns and 'Data' in df.columns:
            
            # Agrupamos los datos por cada variante de algoritmo
            grupos = df.groupby('Family')
            
            for algoritmo, datos_grupo in grupos:
                # Extraemos la lista de los 31 valores de fitness
                valores = datos_grupo['Data'].dropna()
                
                # Regla 1: Shapiro-Wilk requiere al menos 3 datos
                if len(valores) < 3:
                    p_value = np.nan
                
                # Regla 2: Si el algoritmo convergió siempre al mismo número exacto (std = 0)
                # la matemática de Shapiro colapsa. Le asignamos p-value = 0.0 (No normal)
                elif valores.std() == 0:
                    p_value = 0.0
                
                # Regla 3: Si hay varianza, aplicamos el test
                else:
                    estadistico, p_value = shapiro(valores)
                
                # Criterio de decisión estadística (Alfa = 0.05)
                es_normal = "Sí" if p_value >= 0.05 else "No"
                
                # Guardamos el registro
                lista_resultados.append({
                    'Instancia': nombre_instancia,
                    'Algoritmo': algoritmo,
                    'P-Value': p_value,
                    'Normal (p>=0.05)': es_normal
                })
        else:
            print(f"⚠️ El archivo {nombre_instancia} no tiene las columnas 'Family' o 'Data'. Se omitió.")

    # Consolidamos todo en un único DataFrame
    df_reporte = pd.DataFrame(lista_resultados)
    
    # Formatear el p-value a notación científica para mejor lectura
    df_reporte['P-Value'] = df_reporte['P-Value'].map(lambda x: f"{x:.2e}" if pd.notnull(x) else "N/A")
    
    # Guardamos el reporte final
    os.makedirs(carpeta_resultados, exist_ok=True)
    ruta_salida = os.path.join(carpeta_resultados, f"{mh}_Reporte_Normalidad_Global.csv")
    df_reporte.to_csv(ruta_salida, index=False)
    
    print(f"\n✅ Análisis completado. Se evaluaron {len(archivos_csv)} instancias.")
    print(f"📊 Reporte guardado en: {ruta_salida}")

def obtenerExperimentosCSV():
    ruta_fitness = './Resultados/Test/KP/data/'
    df = pd.read_csv(os.path.join(ruta_fitness, 'knapPI_1_100_1000_1.csv'))
    return df['MH'].unique().tolist()

def test_estadistico():
    familia = True
    s_shaped = True    
    if familia:
        ruta_base = './Resultados/data/KP/fitness/'
        mhs = bd.obtenerMHBD()
        instancias = bd.obtenerInstanciasEjecutadas("KP")
        for instancia in instancias:
            df = pd.read_csv(f'{ruta_base}{instancia[1]}.csv')
            df['Family'] = df['Family'] + '-' + df['DR']
            columnas_finales = ['MH', 'Family', 'Data']
            df_nuevo = df[columnas_finales]
            df_pso = df_nuevo[df_nuevo['MH'] == 'PSO']
            df_gwo = df_nuevo[df_nuevo['MH'] == 'GWO']
            df_pso.to_csv(f'./Resultados/Test/KP/data/family/PSO/{instancia[1]}.csv', index=False)
            df_gwo.to_csv(f'./Resultados/Test/KP/data/family/GWO/{instancia[1]}.csv', index=False)
            print(f"✅ Archivo unificado para la instancia Familia Esquemas para {instancia[1]} generado exitosamente.")
        for mh in mhs:
            analisis_normalidad_masivo(f'./Resultados/Test/KP/data/family/{mh[0]}/', f'./Resultados/Test/KP/family/normalidad', f'{mh[0]}')
            test_friedman_rankings(f'./Resultados/Test/KP/data/family/{mh[0]}/', f'./Resultados/Test/KP/family/friedman', f'{mh[0]}', tipo_problema='max')
            generar_matrices_victorias(f'./Resultados/Test/KP/data/family/{mh[0]}/', f'./Resultados/Test/KP/family/wilcoxon', f'{mh[0]}', tipo_problema='max')


    if s_shaped:
        ruta_base = './Resultados/data/KP/fitness/'
        mhs = bd.obtenerMHBD()
        instancias = bd.obtenerInstanciasEjecutadas("KP")
        for instancia in instancias:
            df = pd.read_csv(f'{ruta_base}{instancia[1]}.csv')
            df['Family'] = df['TF'] + '-' + df['DR']
            columnas_finales = ['MH', 'Family', 'Data']
            df_nuevo = df[columnas_finales]
            df_pso = df_nuevo.query(f"MH == 'PSO' and (Family == 'S1-STD' or Family == 'S2-STD' or Family == 'S3-STD' or Family == 'S4-STD')")
            df_gwo = df_nuevo.query(f"MH == 'GWO' and (Family == 'S1-STD' or Family == 'S2-STD' or Family == 'S3-STD' or Family == 'S4-STD')")
            df_pso.to_csv(f'./Resultados/Test/KP/data/s-shaped/PSO/{instancia[1]}.csv', index=False)
            df_gwo.to_csv(f'./Resultados/Test/KP/data/s-shaped/GWO/{instancia[1]}.csv', index=False)
            print(f"✅ Archivo unificado para la instancia Familia Esquemas para {instancia[1]} generado exitosamente.")
        for mh in mhs:
            analisis_normalidad_masivo(f'./Resultados/Test/KP/data/s-shaped/{mh[0]}/', f'./Resultados/Test/KP/s-shaped/normalidad', f'{mh[0]}')
            test_friedman_rankings(f'./Resultados/Test/KP/data/s-shaped/{mh[0]}/', f'./Resultados/Test/KP/s-shaped/friedman', f'{mh[0]}', tipo_problema='max')
            generar_matrices_victorias(f'./Resultados/Test/KP/data/s-shaped/{mh[0]}/', f'./Resultados/Test/KP/s-shaped/wilcoxon', f'{mh[0]}', tipo_problema='max')

def graficar_exploracion_explotacion(iteraciones, xpl, xpt, titulo, mh, binarizacion):
    """
    Genera y guarda un gráfico de líneas de XPL y XPT sin título.
    Acepta DataFrames como entrada para las series.
    """
    # 1. Convertir DataFrames a arreglos 1D para evitar errores de Matplotlib y de cálculo de medias
    val_iter = iteraciones.values.flatten() if isinstance(iteraciones, pd.DataFrame) else iteraciones
    val_xpl = xpl.values.flatten() if isinstance(xpl, pd.DataFrame) else xpl
    val_xpt = xpt.values.flatten() if isinstance(xpt, pd.DataFrame) else xpt
    
    # 2. Construir la ruta de salida estricta
    output_dir = './Resultados/graficos/KP/'
    os.makedirs(output_dir, exist_ok=True) # Crea las carpetas si no existen
    
    nombre_archivo = f'percentage_{titulo}_{mh}_{binarizacion}.png'
    path_porcentaje = os.path.join(output_dir, nombre_archivo)
    
    # 3. Inicializar el lienzo
    fig, axPER = plt.subplots(figsize=(8, 5))
    
    # 4. Graficar las series (Usando los valores aplanados)
    axPER.plot(val_iter, val_xpl, color="r", label=rf"$\overline{{XPL}}$: {np.round(np.mean(val_xpl), 2)}%")
    axPER.plot(val_iter, val_xpt, color="b", label=rf"$\overline{{XPT}}$: {np.round(np.mean(val_xpt), 2)}%")
    
    # 5. Personalización (Se elimina el título según la instrucción)
    axPER.set_ylabel("Percentage")
    axPER.set_xlabel("Iteration")
    
    # 6. Configurar leyenda y márgenes
    axPER.legend(loc='center right')
    plt.tight_layout()
    
    # 7. Guardar y cerrar
    plt.savefig(path_porcentaje, dpi=300)
    plt.close()
    
    print(f"✅ Gráfico guardado exitosamente en: {path_porcentaje}")

def graficar_dos_series(eje_x, serie_1, serie_2, 
                        nombre_serie1="Algoritmo 1", 
                        nombre_serie2="Algoritmo 2", 
                        etiqueta_x="Iteraciones", 
                        etiqueta_y="Fitness",
                        ruta_guardado=None):
    """
    Genera un gráfico de líneas comparando dos series de datos.
    Los parámetros de entrada (eje_x, serie_1, serie_2) pueden ser columnas de un DataFrame (Series) o listas.
    """
    
    # 1. Configurar el tamaño del lienzo
    plt.figure(figsize=(8, 6))

    # 2. Graficar las series
    plt.plot(eje_x, serie_1, label=nombre_serie1, color='blue', linestyle='-')
    plt.plot(eje_x, serie_2, label=nombre_serie2, color='red', linestyle='--')

    # 3. Personalización de textos
    plt.xlabel(etiqueta_x, fontsize=12)
    plt.ylabel(etiqueta_y, fontsize=12)

    # 4. Activar leyenda y cuadrícula ('best' busca automáticamente el mejor rincón vacío)
    plt.legend(loc='lower right', fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.7)

    # 5. Ajustar márgenes
    plt.tight_layout()

    # 6. Guardar si se proporciona una ruta
    if ruta_guardado:
        plt.savefig(ruta_guardado, dpi=300)
        print(f"✅ Gráfico guardado exitosamente en: {ruta_guardado}")

    # 7. Mostrar el gráfico y limpiar la memoria
    plt.close()

def graficos_best():
    binarizacion_en_analisis = ['STD', 'STD_CIRCLE']
    instancias = bd.obtenerInstanciasEjecutadas("KP")
    mhs = bd.obtenerMHBD()    
    
    for instancia in instancias:
        titulo = instancia[1].split('_')[1] + "_" + instancia[1].split('_')[2]
        if '1000' in titulo or '2000' in titulo:
            for mh in mhs:
                experimento_base = f'{mh[0]} S2-{binarizacion_en_analisis[0]}'
                experimento_caotico = f'{mh[0]} S2-{binarizacion_en_analisis[1]}'
                best_caotico = bd.obtenerBestArchivoKP(instancia[1], mh[0], experimento_caotico)
                buffer_memoria_caotico = io.BytesIO(best_caotico[0][1])
                df_caotico = pd.read_csv(buffer_memoria_caotico, encoding='utf-8')
                
                
                best_base = bd.obtenerBestArchivoKP(instancia[1], mh[0], experimento_base)
                buffer_memoria_base = io.BytesIO(best_base[0][1])
                df_base = pd.read_csv(buffer_memoria_base, encoding='utf-8')
                print(f"\n[INFO] Generando gráfico de convergencia para la instancia {titulo} y MH {mh[0]}...")
                # Llamada avanzada (personalizando todo y guardando la imagen):
                graficar_dos_series(
                    eje_x=df_base['iter'], 
                    serie_1=df_base['fitness'], 
                    serie_2=df_caotico['fitness'],
                    nombre_serie1=binarizacion_en_analisis[0],
                    nombre_serie2=binarizacion_en_analisis[1],
                    etiqueta_x="Iterations",
                    etiqueta_y="Fitness",
                    ruta_guardado=f"./Resultados/best/KP/convergencia_{titulo}_{mh[0]}.png"
                )
                
                print(f"[INFO] Generando gráfico de exploración y explotación para la instancia {titulo}, MH {mh[0]}, binarización {binarizacion_en_analisis[0]}...")
                # Supongamos que df_datos es tu DataFrame con las iteraciones y porcentajes
                graficar_exploracion_explotacion(
                    iteraciones=df_base['iter'],   # Pasando un DataFrame
                    xpl=df_base['XPL'],                # Pasando un DataFrame
                    xpt=df_base['XPT'],                # Pasando un DataFrame
                    titulo=titulo,
                    mh=mh[0],  # mh es una lista/tupla, mh[0] será "SCA"
                    binarizacion=binarizacion_en_analisis[0]
                )
                
                print(f"[INFO] Generando gráfico de exploración y explotación para la instancia {titulo}, MH {mh[0]}, binarización {binarizacion_en_analisis[1]}...")
                # Supongamos que df_datos es tu DataFrame con las iteraciones y porcentajes
                graficar_exploracion_explotacion(
                    iteraciones=df_caotico['iter'],   # Pasando un DataFrame
                    xpl=df_caotico['XPL'],                # Pasando un DataFrame
                    xpt=df_caotico['XPT'],                # Pasando un DataFrame
                    titulo=titulo,
                    mh=mh[0],  # mh es una lista/tupla, mh[0] será "SCA"
                    binarizacion=binarizacion_en_analisis[1]
                )
            
def generar_analitica_familiar():
    
    ruta_fitness = './Resultados/data/KP/fitness/'
    
    archivos = glob.glob(os.path.join(ruta_fitness, "*.csv"))
    DR = ['STD']
    TF = ['S1', 'S2', 'S3', 'S4']
    MHS = ['GWO', 'PSO']
    bd = BD()
    for mh in MHS:
        filas = []
        for archivo in archivos:
            nueva_fila = {}
            instancia = archivo.split("_")[1] + "_" + archivo.split("_")[2]
            nueva_fila['Instance'] = instancia
            df = pd.read_csv(archivo)
            optimo = bd.obtenerOptimoInstancia(archivo.split("\\")[1].split(".")[0])
            print(optimo[0][0])
            nueva_fila['Opt.'] = optimo[0][0]
            
            for tf in TF:
                for dr in DR:
                    df_filtrado = df.query(f"MH == '{mh}' and TF == '{tf}' and DR == '{dr}'")
                    if not df_filtrado.empty:
                        
                        nueva_fila[f'{tf}_{dr}_max'] = df_filtrado['Data'].max()
                        nueva_fila[f'{tf}_{dr}_median'] = df_filtrado['Data'].median()
                        nueva_fila[f'{tf}_{dr}_std'] = np.round(df_filtrado['Data'].std(), 2)
                        
                    #     print(archivo, mh, tf, dr, df_filtrado['Data'].max(), df_filtrado['Data'].median(), df_filtrado['Data'].std())
                    # else:
                    #     print(archivo, mh, tf, dr, "No hay datos")
            filas.append(nueva_fila)
        df_final = pd.DataFrame(filas)
        df_final.to_csv(f'./Resultados/resumen/KP/fitness/analitica_familia_{mh}.csv', index=False)
        # df_filtrado = df.query(f"MH == '{MHS[0]}' and TF == '{TF[0]}' and DR == '{DR[0]}'")
        # print(archivo, df_filtrado['Data'].max(), df_filtrado['Data'].median(), df_filtrado['Data'].std())
        
        
    
    # configuraciones = ['STD', 'STD_LOG', 'STD_PIECE', 'STD_SINE', 'STD_SINGER', 'STD_SINU', 'STD_TENT', 'STD_CIRCLE']
    # # columnas =  ['Instance','STD', '', '', 'STD_LOG', '', '', 'STD_PIECE', '', '', 'STD_SINE', '', '', 'STD_SINGER', '', '', 'STD_SINU', '', '', 'STD_TENT', '', '', 'STD_CIRCLE', '', '']
    # # encabezado =  ['','best', 'avg', 'std', 'best', 'avg', 'std','best', 'avg', 'std','best', 'avg', 'std','best', 'avg', 'std','best', 'avg', 'std','best', 'avg', 'std','best', 'avg', 'std']
    # columnas =  ['Instance','Opt', 'STD', '', 'STD_LOG', '', 'STD_PIECE', '', 'STD_SINE', '', 'STD_SINGER', '', 'STD_SINU', '', 'STD_TENT', '', 'STD_CIRCLE', '']
    # encabezado =  ['', '','best', 'avg', 'best', 'avg', 'best', 'avg', 'best', 'avg', 'best', 'avg', 'best', 'avg', 'best', 'avg','best', 'avg']
    # mhs = bd.obtenerMHBD()
    # for mh in mhs:
    #     # 1. Creas tu buffer
    #     filas_acumuladas = [encabezado]
    #     archivos = os.listdir(f'./Resultados/data/KP/fitness/{mh[0]}/')
    #     for archivo in archivos:
    #         fila_dinamica = [archivo.split(".")[0].split('_')[1] + "_" + archivo.split(".")[0].split('_')[2]]
    #         df = pd.read_csv(f'./Resultados/data/KP/fitness/{mh[0]}/{archivo}')
    #         optimo = bd.obtenerOptimoInstancia(archivo.split(".")[0])
    #         fila_dinamica.append(optimo[0][0])
    #         for configuracion in configuraciones:
    #             df_filtrado = df[df['MH'] == configuracion]
    #             if not df_filtrado.empty:
    #                 best = df_filtrado['Data'].max()
    #                 promedio = df_filtrado['Data'].mean()
    #                 # std = df_filtrado['Data'].std()
    #                 fila_dinamica.append(best)
    #                 fila_dinamica.append(np.round(promedio, 2))
    #                 # fila_dinamica.append(np.round(std, 2))
    #         filas_acumuladas.append(fila_dinamica)
    #     df_final = pd.DataFrame(filas_acumuladas, columns=columnas)
    #     df_final.to_csv(f'./Resultados/resumen/KP/fitness/{mh[0]}.csv', index=False)
    #     print(f"✅ Archivo fitness_KP_{mh[0]}.csv generado exitosamente.")
    #         # buffer_columnas[nombre_algoritmo] = resultados
                    
def generarRPD():
    # instancias_desordenadas = bd.obtenerInstanciasEjecutadas("KP")
    mhs = bd.obtenerMHBD()    
    # instancias = sorted(instancias_desordenadas, key=lambda x: (
    #     int(x[1].split('_')[1]),  # Primero ordena por el grupo (1, 2, 3)
    #     int(x[1].split('_')[2])   # Luego ordena por la capacidad (100, 200, ..., 10000)
    # ))
    # # Nombres de las columnas que usarás al final
    # nombres_columnas = ['BS']
    # for instancia in instancias:
    #     titulo = instancia[1].split('_')[1] + "_" + instancia[1].split('_')[2]
    #     nombres_columnas.append(titulo)
    # print(nombres_columnas)
    # nombres_columnas.append('avg')
    for mh in mhs:
        # experimentos = bd.obtenerBinarizacionesbyMH(mh[0])
        # # 1. Creas tu buffer
        # filas_acumuladas = []
        # for experimento in experimentos:
        #     # 1. Creas tu buffer
        #     fila_dinamica = [experimento[0]]  # La primera columna es el nombre del MH
        #     promedio = []
        #     print(f"[INFO] Procesando RPD experimento {experimento[0]}...") 
        #     for instancia in instancias:
        #         rpd = bd.obtenerRPD(instancia[1], mh[0], experimento[0])
        #         fila_dinamica.append(rpd[0][0])
        #         promedio.append(rpd[0][0])
        #     fila_dinamica.append(np.round(np.mean(promedio), 2))
        #     filas_acumuladas.append(fila_dinamica)
        # # 2. Conviertes a DataFrame pasándole el nombre de las columnas
        # df_final = pd.DataFrame(filas_acumuladas, columns=nombres_columnas)
        # df_final.to_csv(f'./Resultados/resumen/KP/RPD/{mh[0]}.csv', index=False)
        # print(f"✅ Archivo RPD_KP_{mh[0]}.csv generado exitosamente.")
        
        # GENERACION TABLA RESUMEN FAMILIA 
        df = pd.read_csv(f'./Resultados/resumen/KP/RPD/{mh[0]}.csv')
        # Extract Family and DR
        df[['TF', 'DR']] = df['BS'].str.split('-', expand=True)
        df['Family'] = df['TF'].str[0]
        # Melt data to keep instances individual
        data_cols = [c for c in df.columns if '_' in c]
        df_long = df.melt(id_vars=['Family', 'DR', 'BS'], 
                            value_vars=data_cols, 
                            var_name='Instance', value_name='RPD')
        # Pivot table: rows=(Family, DR), cols=Instance
        pivot_table = df_long.pivot_table(index=['Family', 'DR'], columns='Instance', values='RPD', aggfunc='mean')
        # Transponer la tabla: Ahora las instancias serán las filas
        pivot_table_transposed = pivot_table.T
        # Mostrar las primeras filas para verificar el formato
        print(pivot_table_transposed)
        pivot_table_transposed = pivot_table_transposed.round(2)
        pivot_table_transposed.to_csv(f'./Resultados/resumen/KP/RPD/{mh[0]}_familia.csv')
        
        # grafico heatmap completo
        df = pd.read_csv(f'./Resultados/resumen/KP/RPD/{mh[0]}.csv')
        df.set_index('BS', inplace=True)
        plt.figure(figsize=(18, 28))
        sns.heatmap(df, annot=True, fmt=".2f", cmap="RdYlGn_r", linewidths=.2, annot_kws={"size": 17},
                 cbar_kws={"orientation": "horizontal", 
                           "pad": 0.04,
                           "shrink": 0.8,    # Reduce el largo horizontal de la barra
                           "aspect": 30})
        plt.xlabel('Instances', fontsize=14, labelpad=10)
        plt.ylabel('Binarization Schemes', fontsize=14, labelpad=10)
        plt.xticks(rotation=15, ha='right', fontsize=15)
        plt.yticks(fontsize=15)
        plt.tight_layout()

        with open(f'./Resultados/resumen/KP/RPD/heatmap_{mh[0]}.pdf', 'wb') as f:
            plt.savefig(f, format='pdf', dpi=300, 
            bbox_inches='tight',  # <-- ¡Esta es la magia que recorta el espacio blanco!
            pad_inches=0.1)
        print("Hecho")

def generar_graficos_separados(ruta_csv, ruta_salida_box, nombre_instancia):
    # 1. Leer los datos
    print(f"[INFO] Leyendo datos de: {ruta_csv}")
    df = pd.read_csv(ruta_csv)
    
    # 2. Configurar el estilo visual
    sns.set_theme(style="whitegrid")
    
    # ---------------------------------------------------------
    # GRÁFICO 1: CAJA Y BIGOTES (BOXPLOT) INDEPENDIENTE
    # ---------------------------------------------------------
    # Creamos un lienzo nuevo solo para este gráfico
    plt.figure(figsize=(14, 8)) 
    
    sns.boxplot(x='MH', y='Data', data=df, palette='Set2')
    titulo = nombre_instancia.split('_')[1] + "_" + nombre_instancia.split('_')[2]
    plt.title(f'Boxplot - Instance {titulo}', fontsize=16, fontweight='bold')
    plt.xlabel('Binarization', fontsize=12)
    plt.ylabel('Fitness', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Guardamos y cerramos
    ruta_boxplot = os.path.join(ruta_salida_box, f'boxplot_{nombre_instancia}.png')
    plt.savefig(ruta_boxplot, dpi=300)
    plt.close() # MUY IMPORTANTE: Cierra el lienzo para no mezclar con el siguiente
    print(f"✅ Boxplot guardado en: {ruta_boxplot}")

    # # ---------------------------------------------------------
    # # GRÁFICO 2: VIOLÍN (VIOLINPLOT) INDEPENDIENTE
    # # ---------------------------------------------------------
    # # Creamos OTRO lienzo nuevo
    # plt.figure(figsize=(14, 8))
    
    # sns.violinplot(x='MH', y='Data', data=df, palette='Set3', inner='quartile')
    
    # plt.title(f'Violinplot - Instance {nombre_instancia}', fontsize=16, fontweight='bold')
    # plt.xlabel('MH', fontsize=12)
    # plt.ylabel('Fitness', fontsize=12)
    # plt.xticks(rotation=45, ha='right')
    # plt.tight_layout()
    
    # # Guardamos y cerramos
    # ruta_violin = os.path.join(ruta_salida_violin, f'violinplot_{nombre_instancia}.png')
    # plt.savefig(ruta_violin, dpi=300)
    # plt.close()
    # print(f"✅ Violinplot guardado en: {ruta_violin}")

def gestionar_archivo_csv(ruta_archivo):
    # Convertimos la ruta de texto a un objeto Path
    archivo = Path(ruta_archivo)
    
    # 1. Verificamos si existe
    if archivo.exists():
        print(f"✅ ESTADO: El archivo '{archivo.name}' YA EXISTE.")
        return {'mode': 'a', 'header': False}
        
    else:
    # 2 y 3. Si no existe, lo creamos e indicamos el modo
        print(f"⚠️ ESTADO: El archivo '{archivo.name}' NO EXISTE.")
        # .touch() crea un archivo en blanco en esa ruta
        df = pd.DataFrame(columns=['MH', 'Data'])
        df.to_csv(archivo, index=False)
        print("✨ ACCIÓN: Archivo creado exitosamente.")
        return {'mode': 'w', 'header': True}

def generar_data():
    instancias = bd.obtenerInstanciasEjecutadas("KP")
    print(f"[INFO] Analizando {len(instancias)} instancias de KP...")
    
    for instancia in instancias:
        print(f"\n [INFO] Procesando instancia: {instancia[1]}")
        mhs = bd.obtenerMHEjecutadas(instancia[1])
        print(f"[INFO] Analizando {len(mhs)} MHS para la instancia {instancia[1]}...")
        
        ruta_fitness = f'./Resultados/data/KP/fitness/{instancia[1]}.csv'
        ruta_tiempos = f'./Resultados/data/KP/tiempos/{instancia[1]}.csv'
        
        for mh in mhs:
            print(f"[INFO] Procesando MHS: {mh[0]} para la instancia {instancia[1]}...")
            
            experimentos = bd.obtenerExperimentosEjecutadosBinarizacion(instancia[1], mh[0])
            print(f"[INFO] Analizando {len(experimentos)} experimentos para la instancia {instancia[1]} y MHS {mh[0]}...")
            
            for experimento in experimentos:
                print(f"[INFO] Procesando experimento: {experimento[0]} para la instancia {instancia[1]} y MHS {mh[0]}...")
                resultados = bd.obtenerResultadosTiemposBinarizacion(instancia[1], experimento[0], mh[0])
                print(f"\n [INFO] Analizando {len(resultados)} resultados para la instancia {instancia[1]}, MHS {mh[0]} y experimento {experimento[0]}...")
                
                # verificacion archivo de fitness
                conf_fitness = gestionar_archivo_csv(ruta_fitness)
                # verificacion archivo de tiempos
                conf_tiempos = gestionar_archivo_csv(ruta_tiempos)
                
                datos_fitness = []
                datos_tiempos = []
                datos_exp = []
                datos_mh = []
                datos_tf = []
                datos_dr = []
                datos_family = []
                
                nomre_experimento = mh[0] + "_" + experimento[0]
                TF = experimento[0].split("-")[0]
                DR = experimento[0].split("-")[1]
                Family = TF[0]
                
                for resultado in resultados:
                    datos_fitness.append(resultado[0])  # fitness
                    datos_tiempos.append(resultado[1])  # tiempo
                    datos_exp.append(nomre_experimento)
                    datos_mh.append(mh[0])
                    datos_tf.append(TF)
                    datos_dr.append(DR)
                    datos_family.append(Family)
                
                nuevos_datos_fitness = pd.DataFrame({
                    'Exp': datos_exp,
                    'MH' : datos_mh,
                    'TF' : datos_tf,
                    'DR' : datos_dr,
                    'Family' : datos_family,
                    'Data': datos_fitness
                    
                })
                
                nuevos_datos_tiempos = pd.DataFrame({
                    'MH': datos_mh,
                    'Data': datos_tiempos
                })
            
                # Guardamos el DataFrame
                nuevos_datos_fitness.to_csv(
                    ruta_fitness, 
                    mode=conf_fitness['mode'], 
                    header=conf_fitness['header'], 
                    index=False  # ¡MUY IMPORTANTE! (Explicación abajo)
                )

                nuevos_datos_tiempos.to_csv(
                    ruta_tiempos, 
                    mode=conf_tiempos['mode'], 
                    header=conf_tiempos['header'], 
                    index=False  # ¡MUY IMPORTANTE! (Explicación abajo)
                )
                             
def analizar_instancias():
    """
    Función principal para analizar instancias del KP.
    Procesa cada instancia, genera gráficos y resúmenes estadísticos.
    """
    if GENERAR_DATA:
        generar_data()
        
    if GENERAR_GRAFICOS_DISTRIBUCION:
        instancias = bd.obtenerInstanciasEjecutadas("KP")
        for instancia in instancias:
            mhs = bd.obtenerMHEjecutadas(instancia[1])
            for mh in mhs:
                ruta_entrada = f'./Resultados/data/KP/fitness/{mh[0]}/{instancia[1]}.csv'
                ruta_salida_box = f'./Resultados/boxplot/KP/{mh[0]}/'
                
                generar_graficos_separados(ruta_entrada, ruta_salida_box, instancia[1])
    if GENERAR_RPD:
        generarRPD()
        
    if GENERAR_ANALITICA_BEST_FAMILIA:
        generar_analitica_familiar()
        
    if GRAFICOS_BEST_FAMILIA:
        graficos_best()
        
    if TEST_ESTADISTICO:
        test_estadistico()

    # print(os.listdir('./Resultados/graficos/KP/'))  # Verifica que los archivos se hayan guardado correctamente

    print("[INFO] Análisis KP completado con éxito.")
    print("-" * 50)
