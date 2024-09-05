import re
import argparse
import pytesseract
import os
from collections import defaultdict
from fuzzywuzzy import fuzz
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")

def extract_product_name(text):
    product_match = re.search(r'Nội dung hàng.*?\n(.*?)SL:', text, re.DOTALL)
    
    if product_match:
        product_name = product_match.group(1).strip()
        if product_name.endswith(','):
            product_name = product_name[:-1].strip()
        return product_name
    return None

def process_pdf_and_cluster(input_pdf_path, dpi=300):
    pages = convert_from_path(input_pdf_path, dpi=dpi)
    
    products = []
    
    for page_number, page_data in enumerate(pages):
        gray_image = page_data.convert('L')

        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray_image, lang='vie+eng', config=custom_config)
        
        product_name = extract_product_name(text)
        
        if product_name:
            products.append((product_name, page_number))
        
        # print(f"Extracted Product Name from Page {page_number + 1}: {product_name}")
    
    return products

def group_products_fuzzily(products, similarity_threshold=80):
    # This dictionary will map a representative product name to a list of similar product names and their pages
    product_groups = defaultdict(list)

    for product_name, page_number in products:
        match = None
        best_match_name = None

        for existing_product_name in product_groups.keys():
            similarity = fuzz.ratio(existing_product_name, product_name)
            if similarity >= similarity_threshold:
                match = similarity
                best_match_name = existing_product_name
                break

        # If a match is found, group it under the best match product name
        if match:
            product_groups[best_match_name].append(page_number)
        else:
            # If no match is found, consider it a new product name group
            product_groups[product_name].append(page_number)
    
    return product_groups

def create_clustered_pdfs(input_pdf_path, product_groups, output_folder):
    reader = PdfReader(input_pdf_path)
    
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Create new PDFs for each product group
    for product_name, page_numbers in product_groups.items():
        writer = PdfWriter()
        
        for page_number in page_numbers:
            writer.add_page(reader.pages[page_number])
        
        total_pages = len(page_numbers)

        safe_product_name = re.sub(r'[^\w\s-]', '', product_name).strip().replace(' ', '_')

        # Construct the output file name in the format <total_pdf_page>_<product_name>.pdf
        output_file_name = f"{total_pages}_{safe_product_name}.pdf"
        output_file_path = os.path.join(output_folder, output_file_name)
        
        with open(output_file_path, 'wb') as output_file:
            writer.write(output_file)
        
        # print(f"Created PDF for product '{product_name}' with {total_pages} pages -> {output_file_path}")

def create_combined_pdf(input_pdf_path, product_groups, output_file_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Sort the products by the number of pages (most frequent first)
    sorted_products = sorted(product_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Add pages from each product group in the sorted order
    for product_name, page_numbers in sorted_products:
        for page_number in page_numbers:
            writer.add_page(reader.pages[page_number])
    
    with open(output_file_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"Created combined PDF sorted by frequency -> {output_file_path}")

def main():
    # Parse command-line arguments for input/output paths and similarity threshold
    parser = argparse.ArgumentParser(description="Process PDF and cluster product pages.")
    parser.add_argument("input_pdf_path", help="Path to the input PDF file.")
    parser.add_argument("output_folder", help="Folder to store the resulting PDFs.")
    parser.add_argument("--similarity_threshold", type=int, default=80, help="Similarity threshold for fuzzy matching.")
    
    args = parser.parse_args()
    
    # Step 1: Process the PDF, extract product names, and get the list of products
    products = process_pdf_and_cluster(args.input_pdf_path)

    # Step 2: Group product names fuzzily based on a similarity threshold
    product_groups = group_products_fuzzily(products, args.similarity_threshold)

    # Step 3: Create clustered PDFs based on product names
    create_clustered_pdfs(args.input_pdf_path, product_groups, args.output_folder)

    # Step 4: Create a final combined PDF sorted by most frequent product
    combined_pdf_path = os.path.join(args.output_folder, "combined_sorted_by_frequency.pdf")
    create_combined_pdf(args.input_pdf_path, product_groups, combined_pdf_path)

if __name__ == "__main__":
    main()
