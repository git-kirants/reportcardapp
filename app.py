from flask import Flask, request, render_template, send_file
import firebase_admin
from firebase_admin import credentials, storage
import io
import PyPDF2

app = Flask(__name__)

# Initialize Firebase Admin
cred = credentials.Certificate('C:\\Users\\Kiran T S\\Documents\\Projects\\report\\reportcardapp-fe480-firebase-adminsdk-wl5o9-55b90068ac.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'reportcardapp-fe480.appspot.com'
})

def list_pdf_files():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()
    files = [blob.name for blob in blobs if blob.name.endswith('.pdf')]
    return files

@app.route('/')
def index():
    files = list_pdf_files()
    return render_template('index.html', files=files)

@app.route('/search', methods=['POST'])
def search():
    file_name = request.form.get('file_name')
    roll_number = request.form.get('roll_number')

    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    file_stream = io.BytesIO()
    blob.download_to_file(file_stream)
    file_stream.seek(0)

    roll_page_map = {}

    pdf = PyPDF2.PdfReader(file_stream)
    outlines = pdf.outline
    for outline in outlines:
        if isinstance(outline, PyPDF2.generic.Destination):
            # Assuming the outline title is the roll number
            roll_no = outline.title
            page_no = pdf.get_destination_page_number(outline)
            roll_page_map[roll_no] = page_no

    print("Roll to Page Mapping:", roll_page_map)  # Debug output

    target_page_index = roll_page_map.get(roll_number)

    if target_page_index is not None:
        # Create a new PDF with just the target page
        output = PyPDF2.PdfWriter()
        output.add_page(pdf.pages[target_page_index])
        
        # Save the single page to a bytes buffer
        buffer = io.BytesIO()
        output.write(buffer)
        buffer.seek(0)
        
        # Return the PDF file
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"roll_number_{roll_number}.pdf",
            mimetype='application/pdf'
        )
    else:
        return "Invalid Roll No"

if __name__ == '__main__':
    app.run(debug=True)