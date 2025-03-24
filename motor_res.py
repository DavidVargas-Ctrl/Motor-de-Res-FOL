from typing import List, Set, Tuple, Dict, Optional
import re

Literal = str
Clausula = Set[Literal]
Sustitucion = Dict[str, str]

def es_variable(x: str) -> bool:
    return x[0].islower()

def parse_literal(literal: str) -> Tuple[str, List[str]]:
    pred, args = re.match(r'(~?\w+)\((.*)\)', literal).groups()
    return pred, [arg.strip() for arg in args.split(',')]

def aplicar_sustitucion(literal: str, sustitucion: Sustitucion) -> str:
    pred, args = parse_literal(literal)
    nuevos_args = [sustitucion.get(arg, arg) for arg in args]
    return f"{pred}({', '.join(nuevos_args)})"

def unificar(lit1: str, lit2: str) -> Optional[Sustitucion]:
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
    resolventes = set()
    for li in ci:
        for lj in cj:
            if li.startswith('~') != lj.startswith('~'):
                sustitucion = unificar(li.lstrip('~'), lj.lstrip('~'))
                if sustitucion is not None:
                    nueva_ci = {aplicar_sustitucion(l, sustitucion) for l in ci if l != li}
                    nueva_cj = {aplicar_sustitucion(l, sustitucion) for l in cj if l != lj}
                    nueva = nueva_ci.union(nueva_cj)
                    resolventes.add(frozenset(nueva))
    return resolventes

def resolucion_fol(bc: List[Clausula], objetivo: Clausula) -> bool:
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
                if not nuevo:
                    return True
                nuevas.add(nuevo)

        if nuevas.issubset(set(map(frozenset, bc))):
            return False
        for c in nuevas:
            if c not in bc:
                bc.append(set(c))
