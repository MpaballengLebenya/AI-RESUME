from flask import Flask, render_template, request, make_response
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import cohere

app = Flask(__name__)

# Initialize Cohere client with your API key
COHERE_API_KEY = "Bearer LtPRSd3JtAkBgOzmp17cCPmHRGxYpgWSB3dhelel"



co = cohere.Client(COHERE_API_KEY)

generated_data = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    global generated_data
    data = request.form.to_dict()

    prompt = (
        f"Create a professional resume for {data.get('name')} applying as a {data.get('job')}.\n"
        f"Email: {data.get('email')}\n"
        f"Phone: {data.get('phone')}\n"
        f"Summary: {data.get('summary')}\n"
        f"Skills: {data.get('skills')}\n"
        f"Work Experience: {data.get('experience')}\n"
        f"Education: {data.get('education')}\n"
        "Format the resume professionally."
    )

    response = co.generate(
        model="command",
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    resume_text = response.generations[0].text.strip()

    generated_data = {
        "resume": resume_text,
        **data
    }

    return render_template("result.html", resume=resume_text, **data, hide_buttons=False)

# Wrap text to fit within PDF margins
def wrap_text(text, max_width, pdf_canvas, font_name, font_size):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        width = pdf_canvas.stringWidth(test_line, font_name, font_size)
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

@app.route("/download")
def download_pdf():
    global generated_data

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    font_name = "Helvetica"
    font_size = 10
    pdf.setFont(font_name, font_size)

    margin = 50
    max_width = width - 2 * margin
    x = margin
    y = height - margin

    paragraphs = generated_data.get("resume", "").split('\n\n')

    for para in paragraphs:
        clean_para = para.strip().replace('\n', ' ')
        lines = wrap_text(clean_para, max_width, pdf, font_name, font_size)

        for line in lines:
            if y < margin:
                pdf.showPage()
                pdf.setFont(font_name, font_size)
                y = height - margin
            pdf.drawString(x, y, line)
            y -= font_size + 4
        y -= font_size + 8

    pdf.save()

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=resume.pdf'
    return response

if __name__ == "__main__":
    app.run(debug=True)
