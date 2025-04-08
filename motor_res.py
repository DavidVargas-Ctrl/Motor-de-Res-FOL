from typing import List, Set, Tuple, Dict, Optional
import ast
import re

# Definiciones básicas para resolución
Literal = str
Clausula = Set[Literal]
Sustitucion = Dict[str, str]


def es_variable(x: str) -> bool:
    # Se asume que las variables comienzan con minúscula.
    return x[0].islower()


def parse_literal(literal: str) -> Tuple[str, List[str]]:
    # Extrae el predicado y la lista de argumentos de la literal
    pred, args = re.match(r'(~?\w+)\((.*)\)', literal).groups()
    return pred, [arg.strip() for arg in args.split(',')]


def aplicar_sustitucion(literal: str, sustitucion: Sustitucion) -> str:
    pred, args = parse_literal(literal)
    nuevos_args = [sustitucion.get(arg, arg) for arg in args]
    return f"{pred}({', '.join(nuevos_args)})"


def unificar(lit1: str, lit2: str) -> Optional[Sustitucion]:
    # Unificación simple entre dos literales.
    pred1, args1 = parse_literal(lit1)
    pred2, args2 = parse_literal(lit2)
    if pred1.lstrip('~') != pred2.lstrip('~') or len(args1) != len(args2):
        return None
    sust = {}
    for a1, a2 in zip(args1, args2):
        if a1 == a2:
            continue
        elif es_variable(a1) and not es_variable(a2):
            sust[a1] = a2
        elif es_variable(a2) and not es_variable(a1):
            sust[a2] = a1
        elif es_variable(a1) and es_variable(a2):
            sust[a1] = a2
        else:
            return None
    return sust


def resolver_fol(ci: Clausula, cj: Clausula) -> Set[Clausula]:
    # Aplica la resolución entre dos cláusulas.
    resolventes = set()
    for li in ci:
        for lj in cj:
            # Se consideran literales complementarias si una está negada y la otra no.
            if li.startswith('~') != lj.startswith('~'):
                sustitucion = unificar(li.lstrip('~'), lj.lstrip('~'))
                if sustitucion is not None:
                    nueva_ci = {aplicar_sustitucion(l, sustitucion) for l in ci if l != li}
                    nueva_cj = {aplicar_sustitucion(l, sustitucion) for l in cj if l != lj}
                    nueva = nueva_ci.union(nueva_cj)
                    resolventes.add(frozenset(nueva))
    return resolventes


def resolucion_fol(bc: List[Clausula], objetivo: Clausula) -> bool:
    """
    Paso 8 y 9: Se trabaja con la base de conocimiento en CNF (bc) y se añade el objetivo
    (usualmente la negación de la consulta). Se aplican las resoluciones en pares de cláusulas.
    Si se deriva la cláusula vacía, se demuestra el objetivo.
    """
    bc = bc.copy()
    bc.append(objetivo)
    nuevas = set()
    paso = 1

    while True:
        pares = [(bc[i], bc[j]) for i in range(len(bc)) for j in range(i + 1, len(bc))]
        for (ci, cj) in pares:
            resultados = resolver_fol(ci, cj)
            for nuevo in resultados:
                print(f"\nPaso {paso}:")
                print(f"Resolviendo {ci} y {cj}")
                print(f"Resultado: {nuevo if nuevo else 'CLAUSULA VACIA (Se demuestra)'}")
                paso += 1
                if not nuevo:  # La cláusula vacía se representa con el conjunto vacío.
                    return True
                nuevas.add(nuevo)

        if nuevas.issubset(set(map(frozenset, bc))):
            return False
        for c in nuevas:
            if c not in bc:
                bc.append(set(c))


# -------------------------
# Funciones para los 7 pasos de transformación a CNF
# (Se incluyen por completitud, en caso de que se desee transformar una fórmula en cadena)
# -------------------------

def eliminar_implicaciones(formula: str) -> str:
    """
    Paso 1: Elimina implicaciones.
    Reemplaza A -> B por ~A v B. Implementación simplificada.
    """
    while "->" in formula:
        formula = re.sub(r'([^()]+)->([^()]+)', r"(~(\1) v (\2))", formula)
    return formula


def mover_negaciones(formula: str) -> str:
    """
    Paso 2: Mueve las negaciones hacia adentro utilizando las leyes de De Morgan.
    """
    formula = re.sub(r'~\(([^()]+) v ([^()]+)\)', r"(~\1 ^ ~\2)", formula)
    formula = re.sub(r'~\(([^()]+) \^ ([^()]+)\)', r"(~\1 v ~\2)", formula)
    return formula


def estandarizar_variables(formula: str) -> str:
    """
    Paso 3: Estandariza las variables (se asume que ya son únicas).
    """
    return formula


def skolemizar(formula: str) -> str:
    """
    Paso 4: Skolemiza la fórmula.
    """
    contador = 0

    def reemplazo(match):
        nonlocal contador
        contador += 1
        return f"sk{contador}"

    formula = re.sub(r'∃\w+\.', reemplazo, formula)
    return formula


def eliminar_cuantificadores(formula: str) -> str:
    """
    Paso 5: Elimina los cuantificadores universales.
    """
    formula = re.sub(r'∀\w+\.', '', formula)
    return formula


def distribuir(formula: str) -> str:
    """
    Paso 6: Distribuye las disyunciones sobre las conjunciones.
    """
    return formula


def extraer_clausulas(formula: str) -> List[Clausula]:
    """
    Paso 7: Extrae cláusulas de la fórmula en CNF.
    """
    clauses = []
    for clause in formula.split('^'):
        clause = clause.strip().replace("(", "").replace(")", "")
        literals = clause.split('v')
        clause_set = {lit.strip() for lit in literals if lit.strip()}
        if clause_set:
            clauses.append(clause_set)
    return clauses


def convertir_a_cnf(formula: str) -> List[Clausula]:
    """
    Aplica los 7 pasos para transformar una fórmula de FOL a CNF.
    """
    print("Paso 1: Eliminar implicaciones")
    formula = eliminar_implicaciones(formula)
    print("Resultado:", formula)
    print("Paso 2: Mover negaciones hacia adentro")
    formula = mover_negaciones(formula)
    print("Resultado:", formula)
    print("Paso 3: Estandarizar variables")
    formula = estandarizar_variables(formula)
    print("Resultado:", formula)
    print("Paso 4: Skolemizar")
    formula = skolemizar(formula)
    print("Resultado:", formula)
    print("Paso 5: Eliminar cuantificadores universales")
    formula = eliminar_cuantificadores(formula)
    print("Resultado:", formula)
    print("Paso 6: Distribuir disyunciones sobre conjunciones")
    formula = distribuir(formula)
    print("Resultado:", formula)
    print("Paso 7: Extraer cláusulas")
    clauses = extraer_clausulas(formula)
    print("Resultado:", clauses)
    return clauses


# -------------------------
# Ejemplo de uso leyendo la base generada desde un archivo
# -------------------------

if __name__ == "__main__":
    # Se asume que el archivo "respuesta_gemini_ajustada.txt" contiene la salida de Gemini,
    # por ejemplo:
    # [
    #  {'Hombre(Marco)'},
    #  {'Pompeyano(Marco)'},
    #  {'∀x.(Pompeyano(x) -> Romano(x))'},
    #  {'Gobernante(Cesar)'},
    #  {'∀x.(Romano(x) -> (Leal(x, Cesar) v Odia(x, Cesar)))'},
    #  {'∀x.∀y.(IntentaAsesinar(x, y) -> (Gobernante(y) ^ ~Leal(x, y)))'},
    #  {'IntentaAsesinar(Marco, Cesar)'},
    #  {'~Odia(Marco, Cesar)'}
    # ]

    with open("respuesta_gemini_ajustada.txt", "r", encoding="utf-8") as f:
        contenido = f.read()

    try:
        # Convierte el string al equivalente en Python (lista de conjuntos)
        base_list = ast.literal_eval(contenido)
    except Exception as e:
        print("Error al interpretar la base de conocimientos:", e)
        base_list = []

    # Se asume que la última cláusula es la negación de la consulta
    if base_list:
        objetivo = base_list.pop()  # Extrae la última cláusula
        base = base_list  # El resto es la base de conocimientos
    else:
        print("La base de conocimientos está vacía.")
        exit(1)

    # Muestra la base leída y el objetivo (opcional)
    print("Base de conocimientos (CNF):")
    for clausula in base:
        print(clausula)
    print("\nObjetivo (negación de la consulta):", objetivo)

    # Se procede con la resolución
    print("\n=== Aplicando Resolución ===")
    if resolucion_fol(base, objetivo):
        print("La cláusula vacía se derivó: se demuestra el objetivo.")
    else:
        print("No se pudo demostrar el objetivo mediante resolución.")
