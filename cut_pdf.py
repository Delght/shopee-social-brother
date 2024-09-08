from pypdf import PdfReader, PdfWriter

def cut_pdf(input_path, output_path, pages_to_keep):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page_num in range(min(pages_to_keep, len(reader.pages))):
        writer.add_page(reader.pages[page_num])

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

# Usage
input_file = "input/test.pdf"
output_file = "input/test_first_100_pages.pdf"
cut_pdf(input_file, output_file, 100)