# Ranking de Friedman — PSO y GWO

Posición de cada esquema de binarización dentro de su familia de
instancias, con el `Rank-Avg` que la sustenta (promedio de los
rankings en las 7 instancias de la familia, sobre 31 corridas cada una).

| Familia de instancias | Prefijo | Instancias |
|---|---|---|
| Uncorrelated | `knapPI_1_*` | 7 |
| Weakly correlated | `knapPI_2_*` | 7 |
| Strongly correlated | `knapPI_3_*` | 7 |

## Tabla

|  | **PSO** |  | **PSO** |  | **PSO** |  | **GWO** |  | **GWO** |  | **GWO** |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Position | Uncorrelated | Rank-Avg | Weakly correlated | Rank-Avg | Strongly correlated | Rank-Avg | Uncorrelated | Rank-Avg | Weakly correlated | Rank-Avg | Strongly correlated | Rank-Avg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TOP 1 | S1-STD | 1.86 | S1-STD | 2.07 | S1-STD | 1.79 | S1-STD | 1.64 | S1-STD | 1.64 | S1-STD | 1.21 |
| TOP 2 | S2-STD | 2.71 | S2-STD | 2.43 | S2-STD | 2.50 | S2-STD | 2.36 | S2-STD | 2.36 | S2-STD | 1.93 |
| TOP 3 | S1-COM | 3.64 | S3-STD | 3.43 | S1-COM | 3.43 | S3-STD | 3.29 | S3-STD | 3.07 | S3-STD | 3.14 |
| TOP 4 | S3-STD | 3.86 | S1-COM | 4.79 | S3-STD | 3.79 | S4-STD | 4.14 | S4-STD | 4.07 | S4-STD | 3.71 |
| TOP 5 | S4-STD | 5.14 | S4-STD | 5.21 | S4-STD | 4.36 | X4-STD | 5.14 | X4-STD | 5.07 | X4-STD | 5.00 |
| TOP 6 | S2-COM | 6.21 | S2-COM | 7.14 | S2-COM | 6.57 | X3-STD | 8.29 | X3-STD | 5.79 | X3-STD | 10.00 |
| TOP 7 | V1-STD | 8.43 | X4-STD | 8.79 | V1-STD | 11.00 | X2-STD | 15.43 | X2-STD | 10.93 | V1-STD | 14.57 |
| TOP 8 | V2-STD | 10.43 | V2-STD | 11.57 | X4-STD | 12.43 | S2-COM | 16.57 | V1-STD | 14.36 | X2-STD | 17.29 |
| TOP 9 | X4-STD | 11.43 | V1-STD | 11.79 | V2-STD | 14.29 | S4-COM | 16.71 | X1-STD | 15.21 | Z1-STD | 19.00 |
| TOP 10 | S3-COM | 14.21 | X3-STD | 11.93 | X3-STD | 15.43 | S3-COM | 16.86 | S1-COM | 16.29 | S1-COM | 19.00 |
| TOP 11 | X3-STD | 17.00 | S3-COM | 13.64 | V3-STD | 17.71 | V1-STD | 17.29 | S2-COM | 16.29 | X3-COM | 19.43 |
| TOP 12 | X2-STD | 17.86 | S4-COM | 14.64 | V1-COM | 17.71 | X1-STD | 19.71 | S4-COM | 20.29 | S2-ELIT | 20.57 |
| TOP 13 | V3-STD | 18.00 | X2-STD | 16.36 | S4-COM | 18.43 | X3-COM | 20.14 | X1-COM | 20.71 | V2-STD | 20.71 |
| TOP 14 | S4-COM | 18.21 | V3-STD | 17.93 | V4-STD | 20.29 | X2-COM | 21.14 | V2-STD | 20.71 | S3-COM | 21.29 |
| TOP 15 | V4-STD | 20.71 | V2-COM | 18.43 | S3-COM | 21.00 | V2-STD | 22.71 | S3-COM | 21.29 | X4-COM | 21.86 |
| TOP 16 | X4-COM | 22.71 | X3-COM | 18.71 | V3-COM | 22.00 | V3-ELIT | 23.86 | V4-COM | 22.29 | Z1-COM | 23.14 |
| TOP 17 | Z1-COM | 23.86 | V4-STD | 20.29 | V2-COM | 23.71 | Z1-COM | 24.14 | X2-COM | 22.50 | Z2-ELIT | 23.14 |
| TOP 18 | V1-COM | 24.14 | V1-COM | 20.57 | V2-ELIT | 24.00 | X1-COM | 24.71 | X3-COM | 23.07 | X1-COM | 23.57 |
| TOP 19 | V3-COM | 25.57 | X4-COM | 24.29 | X4-COM | 24.14 | Z4-STD | 24.79 | V3-STD | 24.00 | Z1-ELIT | 23.71 |
| TOP 20 | Z4-ELIT | 25.57 | Z3-COM | 26.29 | X2-STD | 24.57 | Z4-ELIT | 25.29 | X4-COM | 24.29 | X1-STD | 24.14 |
| TOP 21 | X3-COM | 25.86 | V3-COM | 26.43 | Z1-ELIT | 24.71 | V1-ELIT | 26.14 | X4-ELIT | 25.86 | S2-COM | 25.14 |
| TOP 22 | S4-ELIT | 26.29 | Z2-STD | 26.86 | X3-COM | 27.57 | S3-ELIT | 26.43 | Z3-ELIT | 26.07 | X2-COM | 25.57 |
| TOP 23 | X1-STD | 26.43 | Z2-COM | 27.43 | V4-COM | 28.00 | X4-COM | 26.86 | S3-ELIT | 26.57 | V2-COM | 26.64 |
| TOP 24 | V4-ELIT | 26.57 | X2-COM | 27.71 | Z4-COM | 28.29 | S1-COM | 27.14 | Z2-ELIT | 26.79 | Z4-ELIT | 27.86 |
| TOP 25 | X4-ELIT | 27.29 | X1-STD | 28.00 | V1-ELIT | 28.71 | V2-ELIT | 28.14 | Z1-COM | 27.29 | V3-STD | 28.00 |
| TOP 26 | V4-COM | 28.14 | S2-ELIT | 29.29 | X1-ELIT | 28.86 | V4-STD | 28.43 | Z1-ELIT | 27.71 | S4-COM | 28.00 |
| TOP 27 | V2-ELIT | 28.43 | Z4-COM | 29.50 | S2-ELIT | 29.14 | X4-ELIT | 28.43 | Z3-STD | 27.93 | V4-COM | 28.43 |
| TOP 28 | V1-ELIT | 28.43 | X1-COM | 29.86 | Z4-STD | 29.57 | X1-ELIT | 28.57 | X2-ELIT | 28.29 | V4-STD | 28.71 |
| TOP 29 | V2-COM | 28.57 | X1-ELIT | 30.14 | Z2-STD | 29.71 | V2-COM | 28.93 | Z1-STD | 28.43 | Z2-STD | 28.86 |
| TOP 30 | Z4-COM | 28.57 | Z1-ELIT | 30.14 | X1-STD | 30.14 | V3-COM | 29.14 | S2-ELIT | 28.57 | Z2-COM | 29.14 |
| TOP 31 | S3-ELIT | 29.29 | V1-ELIT | 30.29 | Z3-COM | 30.57 | X2-ELIT | 29.57 | Z2-STD | 28.86 | Z3-ELIT | 29.57 |
| TOP 32 | X1-ELIT | 31.00 | V4-COM | 30.43 | Z1-STD | 30.64 | Z2-COM | 30.43 | Z4-ELIT | 29.14 | S4-ELIT | 30.00 |
| TOP 33 | Z3-COM | 31.14 | Z4-STD | 30.93 | Z2-COM | 30.71 | Z3-ELIT | 30.43 | V2-COM | 30.43 | V1-ELIT | 30.43 |
| TOP 34 | Z1-ELIT | 31.29 | Z3-STD | 32.14 | X2-COM | 31.29 | Z1-STD | 30.71 | V4-STD | 31.14 | X3-ELIT | 30.43 |
| TOP 35 | X2-COM | 31.86 | Z1-STD | 34.00 | Z1-COM | 31.57 | S1-ELIT | 31.00 | X3-ELIT | 31.57 | Z3-COM | 30.79 |
| TOP 36 | Z3-STD | 31.86 | S4-ELIT | 34.14 | Z3-STD | 31.71 | V4-COM | 31.14 | V2-ELIT | 31.79 | V3-ELIT | 31.21 |
| TOP 37 | V3-ELIT | 32.71 | Z2-ELIT | 34.71 | X1-COM | 31.86 | Z3-STD | 31.29 | Z2-COM | 32.43 | V1-COM | 31.29 |
| TOP 38 | X1-COM | 32.86 | X2-ELIT | 34.86 | V3-ELIT | 32.00 | Z4-COM | 31.43 | S4-ELIT | 32.50 | X1-ELIT | 31.29 |
| TOP 39 | Z2-ELIT | 33.00 | Z3-ELIT | 35.57 | X3-ELIT | 33.14 | Z1-ELIT | 31.86 | V1-COM | 32.71 | X4-ELIT | 31.71 |
| TOP 40 | S2-ELIT | 33.00 | V2-ELIT | 35.71 | Z2-ELIT | 33.21 | S4-ELIT | 32.29 | S1-ELIT | 33.14 | X2-ELIT | 32.07 |
| TOP 41 | X3-ELIT | 33.57 | X3-ELIT | 35.86 | X4-ELIT | 33.29 | X3-ELIT | 32.71 | V3-COM | 34.07 | Z3-STD | 32.71 |
| TOP 42 | X2-ELIT | 33.71 | V3-ELIT | 36.71 | S3-ELIT | 34.29 | Z2-STD | 32.71 | V4-ELIT | 34.21 | Z4-STD | 32.79 |
| TOP 43 | S1-ELIT | 35.43 | Z1-COM | 36.79 | V4-ELIT | 34.29 | V3-STD | 34.00 | Z3-COM | 35.57 | V2-ELIT | 33.43 |
| TOP 44 | Z2-STD | 38.29 | S3-ELIT | 36.86 | S4-ELIT | 34.43 | V1-COM | 34.00 | V1-ELIT | 36.93 | S1-ELIT | 34.29 |
| TOP 45 | Z2-COM | 39.14 | S1-ELIT | 37.07 | Z4-ELIT | 35.00 | V4-ELIT | 34.00 | V3-ELIT | 37.29 | V4-ELIT | 34.36 |
| TOP 46 | Z4-STD | 39.57 | V4-ELIT | 37.43 | Z3-ELIT | 35.29 | S2-ELIT | 34.14 | Z4-STD | 38.57 | S3-ELIT | 35.00 |
| TOP 47 | Z3-ELIT | 40.86 | X4-ELIT | 37.57 | S1-ELIT | 39.43 | Z2-ELIT | 35.43 | Z4-COM | 38.93 | Z4-COM | 35.14 |
| TOP 48 | Z1-STD | 41.29 | Z4-ELIT | 39.29 | X2-ELIT | 39.43 | Z3-COM | 36.43 | X1-ELIT | 39.00 | V3-COM | 36.71 |
