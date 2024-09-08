import re
import argparse
import pytesseract
import os
from collections import defaultdict
from fuzzywuzzy import fuzz
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter

# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")

def extract_product_info(text):
  text = re.sub(r'\n+', ' | ', text)
  
  # Pattern to match product info
  pattern = r'Nội dung h[aà]ng.*?(\d+\.\s*(.*?)(?:,\s*SL:\s*\d+|$))'
  
  match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
  
  if match:
      full_info = match.group(2).strip()
      
      # Split the full info by commas, reading from the end
      parts = full_info.split(',')
      
      # The category is the last part (excluding SL if present)
      category = parts[-1].strip()
      if 'SL:' in category:
          category = parts[-2].strip() if len(parts) > 1 else "Uncategorized"
      
      # The name is everything else
      name_parts = parts[:-1] if 'SL:' not in parts[-1] else parts[:-2]
      product_name = ', '.join(name_parts).strip()
      
      # Clean up the product name and category
      product_name = re.sub(r'\s+', ' ', product_name).strip()
      product_name = product_name.replace(' | ', ' ')
      category = re.sub(r'\s+', ' ', category).strip()
      category = category.replace(' | ', ' ')
      return {
          "name": product_name,
          "category": category
      }
  else:
      return None
    
def process_pdf_and_cluster(input_pdf_path, dpi= 600):
    pages = convert_from_path(input_pdf_path, dpi=dpi)
    
    products = []
    
    for page_number, page_data in enumerate(pages):
        gray_image = page_data.convert('L')

        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray_image, lang='vie+eng', config=custom_config)
        
        product_info = extract_product_info(text)
        
        if product_info:
            print(product_info)
            # write to file
            with open("output/product_info.txt", "a") as f:
                f.write(f"{product_info}\n")
            products.append((product_info, page_number))
        else:
            print(f"No product info found on page {page_number + 1}")
            print(text)
        # print(f"Extracted Product Info from Page {page_number + 1}: {product_info}")
    
    return products

def group_products_fuzzily(products, name_similarity_threshold=80, category_similarity_threshold=99):
  product_groups = defaultdict(list)

  for product_info, page_number in products:
      best_match = None
      best_match_score = 0
      best_match_key = None

      for existing_key in product_groups.keys():
          existing_name, existing_category = existing_key
          name_similarity = fuzz.ratio(existing_name.lower(), product_info['name'].lower())
          
          # Use token_set_ratio for category comparison to handle word order and slight variations
          category_similarity = fuzz.token_set_ratio(existing_category.lower(), product_info['category'].lower())
          
          # Calculate weighted average score
          avg_score = (name_similarity * 0.7 + category_similarity * 0.3)
          
          if avg_score > best_match_score and name_similarity >= name_similarity_threshold:
              best_match_score = avg_score
              best_match_key = existing_key

      if best_match_key:
          product_groups[best_match_key].append(page_number)
      else:
          new_key = (product_info['name'], product_info['category'])
          product_groups[new_key].append(page_number)
  
  return product_groups

def create_clustered_pdfs(input_pdf_path, product_groups, output_folder):
    reader = PdfReader(input_pdf_path)
    
    os.makedirs(output_folder, exist_ok=True)
    
    for (product_name, category), page_numbers in product_groups.items():
        writer = PdfWriter()
        
        for page_number in page_numbers:
            writer.add_page(reader.pages[page_number])
        
        total_pages = len(page_numbers)

        safe_product_name = re.sub(r'[^\w\s-]', '', product_name).strip().replace(' ', '_')
        safe_category = re.sub(r'[^\w\s-]', '', category).strip().replace(' ', '_')

        output_file_name = f"{total_pages}_{safe_product_name}_{safe_category}.pdf"
        output_file_path = os.path.join(output_folder, output_file_name)
        
        with open(output_file_path, 'wb') as output_file:
            writer.write(output_file)
        
        # print(f"Created PDF for product '{product_name}' (Category: {category}) with {total_pages} pages -> {output_file_path}")

def create_combined_pdf(input_pdf_path, product_groups, output_file_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    
    # Sort the products by category and then by name in descending order
    sorted_products = sorted(product_groups.items(), key=lambda x: (x[0][1], x[0][0]), reverse=True)
    
    for (product_name, category), page_numbers in sorted_products:
        for page_number in page_numbers:
            writer.add_page(reader.pages[page_number])
    
    with open(output_file_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"Created combined PDF sorted by category and name in descending order -> {output_file_path}")

def main():
    parser = argparse.ArgumentParser(description="Process PDF and cluster product pages.")
    parser.add_argument("input_pdf_path", help="Path to the input PDF file.")
    parser.add_argument("output_folder", help="Folder to store the resulting PDFs.")
    parser.add_argument("--name_similarity_threshold", type=int, default=80, help="Similarity threshold for name matching.")
    parser.add_argument("--category_similarity_threshold", type=int, default=99, help="Similarity threshold for category matching.")
    
    args = parser.parse_args()
    
    products = process_pdf_and_cluster(args.input_pdf_path)
    product_groups = group_products_fuzzily(products, 
                                            args.name_similarity_threshold, 
                                            args.category_similarity_threshold)
    # create_clustered_pdfs(args.input_pdf_path, product_groups, args.output_folder)
    combined_pdf_path = os.path.join(args.output_folder, "combined_sorted_by_frequency.pdf")
    create_combined_pdf(args.input_pdf_path, product_groups, combined_pdf_path)

if __name__ == "__main__":
    main()


# python3 classify.py input/test_first_1_pages.pdf output --name_similarity_threshold 80 --category_similarity_threshold 95 