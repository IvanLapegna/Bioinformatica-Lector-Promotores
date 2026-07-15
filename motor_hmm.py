import numpy as np
from hmmlearn.hmm import CategoricalHMM

ESTADOS = ["P", "B"]
SIMBOLOS = ["A", "C", "G", "T"]
IDX = {b: i for i, b in enumerate(SIMBOLOS)}

# Parametros de transicion e inicial.
# OJO: probamos los del profesor (ejemplo17R.py, hmm2: B->P=0.05) y el modelo
# quedaba practicamente inutil -- no detectaba ni un tramo GC-rico de 10 bases
# bien limpio. Por eso usamos estos valores (mas permisivos para entrar a P),
# que si detectan correctamente sin dar falsos positivos. Pendiente: confirmar
# con el conteo real sobre el operon lac (Mundo 1) si se ajustan o se quedan asi.
INICIAL = np.array([0.1, 0.9])
TRANSICION = np.array([
    [0.90, 0.10],   # desde P: 0.9 sigue en P, 0.1 pasa a B
    [0.10, 0.90],   # desde B: 0.1 pasa a P, 0.9 sigue en B
])
EMISION = np.array([
    [0.10, 0.40, 0.40, 0.10],  # P: A=0.1 C=0.4 G=0.4 T=0.1
    [0.25, 0.25, 0.25, 0.25],  # B: parejo
])


def _construir_modelo():
    modelo = CategoricalHMM(n_components=2, n_features=4, init_params="", params="")
    modelo.startprob_ = INICIAL
    modelo.transmat_ = TRANSICION
    modelo.emissionprob_ = EMISION
    return modelo


def _gc_por_ventana(seq: str) -> list:
    """
    Calcula el %GC (como fraccion 0-1) en una ventana centrada en cada posicion.
    El tamano de ventana se adapta al largo de la secuencia: chico para
    secuencias cortas (mas detalle), grande para secuencias largas (menos ruido).
    """
    ventana = max(5, len(seq) // 15)
    mitad = ventana // 2
    valores = []
    for i in range(len(seq)):
        inicio = max(0, i - mitad)
        fin = min(len(seq), i + mitad + 1)
        trozo = seq[inicio:fin]
        gc = (trozo.count("C") + trozo.count("G")) / len(trozo)
        valores.append(gc)
    return valores


def analizar_secuencia(seq: str) -> dict:
    """
    Recibe CUALQUIER secuencia de ADN (string de A/C/G/T, de cualquier largo)
    y devuelve:
      - camino_viterbi: que tramos son Promotor (P) y cuales Background (B)
      - score_forward: que tan probable es la secuencia bajo el modelo

    Esta es la funcion que va a usar la app real (Flask) sin importar
    de donde venga la secuencia (NCBI o pegada a mano).
    """
    seq = seq.upper().strip()
    for base in seq:
        if base not in IDX:
            raise ValueError(f"Base invalida: '{base}'. Solo se permiten A, C, G, T.")

    modelo = _construir_modelo()
    observaciones = np.array([[IDX[b]] for b in seq])

    log_prob_viterbi, camino_indices = modelo.decode(observaciones, algorithm="viterbi")
    camino = "".join(ESTADOS[i] for i in camino_indices)
    score_forward = modelo.score(observaciones)

    # Probabilidad posterior: para cada posicion, que fraccion de las explicaciones
    # posibles la marcan como Promotor (columna 0 = P). Da una curva, no una decision binaria.
    probabilidades = modelo.predict_proba(observaciones)[:, 0].tolist()

    # Confianza promedio: para cada posicion, cuanto "cree" el modelo en la decision
    # que efectivamente tomo Viterbi ahi (no siempre P, a veces B). Un numero solo,
    # que resume que tan convencidas fueron las predicciones en general.
    confianza_por_posicion = [
        p if estado == "P" else (1 - p)
        for estado, p in zip(camino, probabilidades)
    ]
    confianza_promedio = float(np.mean(confianza_por_posicion))

    return {
        "secuencia": seq,
        "camino_viterbi": camino,
        "log_prob_viterbi": log_prob_viterbi,
        "score_forward": score_forward,
        "probabilidad_promotor": probabilidades,
        "gc_ventana": _gc_por_ventana(seq),
        "confianza_promedio": confianza_promedio,
    }


if __name__ == "__main__":
    # Probamos con 3 secuencias DISTINTAS para demostrar que la funcion
    # sirve para cualquier secuencia, no para una fija
    pruebas = {
        "Prueba 1 (con tramo GC-rico en el medio)":
            "ATATATATAT" + "GCGCGCGCGC" + "TATATATATA",
        "Prueba 2 (sin patron claro, mezclada)":
            "AGCTAGCTACGATCGATCGATGCATCGATCG",
        "Prueba 3 (mayormente background, sin promotor)":
            "ATATATATATATATATATATATATATATATATAT",
    }

    for nombre, seq in pruebas.items():
        resultado = analizar_secuencia(seq)
        print(f"--- {nombre} ---")
        print("Secuencia:", resultado["secuencia"])
        print("Viterbi:  ", resultado["camino_viterbi"])
        print(f"Score Forward (log-prob): {resultado['score_forward']:.3f}")
        print()