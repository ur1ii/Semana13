from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

def nuevo_estado():
    return {"pila": [], "cola": [], "lista": [],
            "arbol": [], "grafo": {"vertices": [], "aristas": []}}

estado = nuevo_estado()

@app.get("/")
def inicio():
    return render_template("index.html")

@app.get("/api/estado")
def obtener_estado():
    return jsonify(estado)

@app.post("/api/operacion")
def operacion():
    datos = request.get_json(silent=True) or {}
    tipo = datos.get("tipo")
    accion = datos.get("accion")
    valor = str(datos.get("valor", "")).strip()
    otro = str(datos.get("otro", "")).strip()
    if tipo not in estado:
        return jsonify(error="Estructura no válida"), 400
    if accion != "reiniciar" and not valor and accion not in ("extraer", "atender"):
        return jsonify(error="Introduce un valor"), 400
    resultado = "Operación realizada"
    if accion == "reiniciar":
        estado[tipo] = nuevo_estado()[tipo]
    elif tipo == "pila":
        if accion == "agregar": estado[tipo].append(valor)
        elif accion == "extraer":
            if not estado[tipo]: return jsonify(error="Pila vacía"), 400
            resultado = "Salió: " + estado[tipo].pop()
        else: return jsonify(error="Acción no válida"), 400
    elif tipo == "cola":
        if accion == "agregar": estado[tipo].append(valor)
        elif accion == "atender":
            if not estado[tipo]: return jsonify(error="Cola vacía"), 400
            resultado = "Atendido: " + estado[tipo].pop(0)
        else: return jsonify(error="Acción no válida"), 400
    elif tipo == "lista":
        if accion == "agregar": estado[tipo].append(valor)
        elif accion == "eliminar":
            if valor not in estado[tipo]: return jsonify(error="No encontrado"), 404
            estado[tipo].remove(valor)
        elif accion == "buscar":
            if valor not in estado[tipo]:
                return jsonify(error=f"Elemento '{valor}' no encontrado en la lista"), 404
            posicion = estado[tipo].index(valor)
            resultado = f"Elemento '{valor}' encontrado en el índice {posicion}"
        else: return jsonify(error="Acción no válida"), 400
    elif tipo == "arbol":
        # Cada nodo guarda su nombre y el nombre de su padre.
        if accion == "agregar":
            if any(n["nombre"] == valor for n in estado[tipo]):
                return jsonify(error="Nodo duplicado"), 400
            if estado[tipo] and not any(n["nombre"] == otro for n in estado[tipo]):
                return jsonify(error="El padre debe existir"), 400
            if not estado[tipo] and otro:
                return jsonify(error="La raíz no tiene padre"), 400
            estado[tipo].append({"nombre": valor, "padre": otro or None})
        else: return jsonify(error="Acción no válida"), 400
    elif tipo == "grafo":
        if accion == "agregar":
            if valor not in estado[tipo]["vertices"]:
                estado[tipo]["vertices"].append(valor)
        elif accion == "conectar":
            if valor not in estado[tipo]["vertices"] or otro not in estado[tipo]["vertices"]:
                return jsonify(error="Primero crea ambos vértices"), 400
            if valor == otro: return jsonify(error="Usa vértices distintos"), 400
            arista = sorted([valor, otro])
            if arista not in estado[tipo]["aristas"]:
                estado[tipo]["aristas"].append(arista)
        else: return jsonify(error="Acción no válida"), 400
    return jsonify(mensaje=resultado, estado=estado)

if __name__ == "__main__":
    app.run(debug=True)