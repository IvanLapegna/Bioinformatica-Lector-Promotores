# Lector de Promotores — HMM

Herramienta que analiza secuencias reales de ADN usando un Modelo Oculto de Markov (HMM) de 2 estados, para identificar qué tramos son probablemente región **Promotora** y cuáles **Background**.

Proyecto final — Bioinformática, UNAJ.

## Qué hace

- Recibe una secuencia de ADN, por accession de NCBI o pegada a mano.
- Decodifica con **Viterbi** qué tramos son Promotor / Background (tira de colores).
- Calcula con **Forward** la probabilidad de la secuencia bajo el modelo.
- Muestra una curva de **probabilidad posterior** (qué tan convencido está el modelo en cada posición) superpuesta con una curva de **%GC** (el dato crudo), con zoom interactivo.
- Calcula una métrica de **confianza promedio** de las predicciones.

## Estructura del proyecto

```
backend/
├── app.py               Backend Flask (endpoints)
├── motor_hmm.py          El modelo HMM (Viterbi, Forward, decodificación posterior)
├── requirements.txt      Dependencias de Python
├── Dockerfile            Para correr en Docker
├── docker-compose.yml    Atajo para build + run en un solo comando
├── templates/
│   └── index.html         Estructura de la página
└── static/
    ├── style.css           Estilos
    └── main.js             Lógica del frontend (fetch, gráfico, zoom)
```

## Cómo correrlo

Elegí cualquiera de las 2 opciones — las 2 levantan lo mismo en `http://127.0.0.1:5000/`.

### Opción 1: Python directo

Requisitos: Python 3.10 o superior.

```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

### Opción 2: Docker Compose 

Requisitos: Docker Desktop instalado y corriendo.

```bash
cd backend
docker compose up
```

## Cómo usarlo

1. Abrí `http://127.0.0.1:5000/` en el navegador.
2. Elegí **"Accession de NCBI"** y escribí un accession real (por ejemplo `J01636`), o elegí **"Pegar secuencia"** y pegá una secuencia de ADN (solo se aceptan las letras A, C, G, T).
3. Apretá **"Analizar"**.
4. El resultado muestra: la secuencia coloreada (ámbar = Promotor, gris azulado = Background), el gráfico con las curvas de probabilidad y %GC (con zoom por rueda del mouse o pellizco, y botón para restablecer), el puntaje Forward, el largo de la secuencia, y la confianza promedio del modelo.

## Modelo

HMM de 2 estados (Promotor / Background), alfabeto {A, C, G, T}.

**Emisión** (dada por el material de la materia, Clase 10):

| Estado | P(A) | P(C) | P(G) | P(T) |
|---|---|---|---|---|
| Promotor | 0,10 | 0,40 | 0,40 | 0,10 |
| Background | 0,25 | 0,25 | 0,25 | 0,25 |

**Transición** (definida y validada por el equipo): 0,9 de quedarse en el mismo estado, 0,1 de cambiar — tanto para Promotor como para Background.

**Inicial**: P = 0,1 / B = 0,9.