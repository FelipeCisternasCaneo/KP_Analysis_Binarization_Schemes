import os
import numpy as np
import matplotlib.pyplot as plt

from Discretization.discretization import (
    S1, S2, S3, S4,
    V1, V2, V3, V4,
    X1, X2, X3, X4,
    Z1, Z2, Z3, Z4,
)


def graficar_familia(nombre_familia, funciones, x, carpeta_salida):
    fig, ax = plt.subplots(figsize=(7, 5))

    for etiqueta, funcion in funciones:
        ax.plot(x, funcion(x), label=etiqueta, linewidth=2)

    ax.axhline(0.5, color='black', linewidth=1, linestyle='--', alpha=0.5)
    ax.set_xlabel(r'$d_{j}^{i}$')
    ax.set_ylabel(r'$T(d_{j}^{i})$')
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    ruta = os.path.join(carpeta_salida, f'{nombre_familia.lower()}_shaped.png')
    fig.savefig(ruta, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return ruta


def main():
    x = np.linspace(-10, 10, 400)
    carpeta_salida = os.path.join('Resultados', 'graficos')
    os.makedirs(carpeta_salida, exist_ok=True)

    familias = [
        ('S', [('S1', S1), ('S2', S2), ('S3', S3), ('S4', S4)]),
        ('V', [('V1', V1), ('V2', V2), ('V3', V3), ('V4', V4)]),
        ('X', [('X1', X1), ('X2', X2), ('X3', X3), ('X4', X4)]),
        ('Z', [('Z1', Z1), ('Z2', Z2), ('Z3', Z3), ('Z4', Z4)]),
    ]

    rutas = []
    for nombre, funciones in familias:
        rutas.append(graficar_familia(nombre, funciones, x, carpeta_salida))

    print('Gráficos generados:')
    for ruta in rutas:
        print(ruta)


if __name__ == '__main__':
    main()
