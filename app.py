from flask import Flask, request, jsonify, render_template
from Bio import Entrez, SeqIO
import motor_hmm

app = Flask(__name__)
Entrez.email = "lapegnaivan@gmail.com"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analizar", methods=["POST"])
def analizar():
    datos = request.get_json(force=True)
    secuencia = (datos.get("secuencia") or "").strip()
    accession = (datos.get("accession") or "").strip()

    try:
        if accession:
            handle = Entrez.efetch(db="nucleotide", id=accession, rettype="fasta", retmode="text")
            record = SeqIO.read(handle, "fasta")
            handle.close()
            secuencia = str(record.seq)

        if not secuencia:
            return jsonify({"error": "Falta la secuencia o el accession"}), 400

        resultado = motor_hmm.analizar_secuencia(secuencia)
        return jsonify(resultado)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"No se pudo bajar el accession de NCBI: {e}"}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)