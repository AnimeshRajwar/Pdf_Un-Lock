from flask import Flask, render_template, request, send_file
import PyPDF2
import io
import os

app = Flask(__name__)

BAND_FILE_KI_JAGAH = 'uploads'
if not os.path.exists(BAND_FILE_KI_JAGAH):
    os.makedirs(BAND_FILE_KI_JAGAH)

app.config['UPLOAD_FOLDER'] = BAND_FILE_KI_JAGAH


def unlock_pdf(pdf_path, password):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        if pdf_reader.is_encrypted:
            try:
                pdf_reader.decrypt(password)
            except Exception as e:
                return None

            pdf_writer = PyPDF2.PdfWriter()
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            output = io.BytesIO()
            pdf_writer.write(output)
            output.seek(0)
            return output
        else:
            return None


def protect_pdf(pdf_file, password):
    with open(pdf_file, 'rb') as f_in:
        pdf_reader = PyPDF2.PdfReader(f_in)


        if not pdf_reader.is_encrypted:
            pdf_writer = PyPDF2.PdfWriter()
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            encrypted_pdf = io.BytesIO()
            pdf_writer.encrypt(password)
            pdf_writer.write(encrypted_pdf)
            encrypted_pdf.seek(0)
            return encrypted_pdf
        else:
            return None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mode = request.form["option"]
        password = request.form["password"]

        if "pdf_file" not in request.files:
            return render_template("index.html", error="No file uploaded.")
        
        band_file = request.files["pdf_file"]

        if band_file.filename == "":
            return render_template("index.html", error="No file selected.")

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], band_file.filename)
        band_file.save(file_path)

        if mode == 'Decrypt':
            unlocked_pdf = unlock_pdf(file_path, password)

            if unlocked_pdf:
                unlocked_pdf.seek(0)
                return send_file(unlocked_pdf, as_attachment=True, download_name="unlocked.pdf", mimetype='application/pdf')
            else:
                return render_template("index.html", error="Incorrect password or PDF is not encrypted.")
        else:
            encrypted_file = protect_pdf(file_path, password)

            if encrypted_file:
                encrypted_file.seek(0)
                return send_file(encrypted_file, as_attachment=True, download_name="encrypted.pdf", mimetype='application/pdf')
            else:
                return render_template("index.html", error="PDF is already encrypted.")

    return render_template("index.html", error=None)


if __name__ == "__main__":
    app.run(debug=True)
