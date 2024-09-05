# Shopee Social Brother

## Project Overview

This project automates the tedious task of managing product documents for a Shopee shop. By processing PDFs, the script extracts product names from invoices or packing lists and groups similar products using fuzzy matching. It then generates separate PDFs for each product, along with a combined document sorted by the most frequent products. This was originally created to help my brother automate these repetitive tasks in his Shopee shop.

## Features

- **PDF Processing**: Extract product names from PDFs using OCR.
- **Fuzzy Matching**: Group similar product names automatically using a similarity threshold.
- **Automated PDF Generation**: Create separate PDFs for each product group and a combined document sorted by frequency.
- **Shopee Document Handling**: Tailored specifically to Shopee invoice/packing list formats.

## How It Works

The script reads the input PDF, extracts product names, and groups them using fuzzy matching. It then generates individual PDFs for each product group and combines them into a single document. The tool is designed to automate and streamline the handling of Shopee shop documents by reducing manual effort.

## Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/your-username/shopee-social-brother.git
   cd shopee-social-brother
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and configure the path for your environment:

   ```bash
   sudo apt install tesseract-ocr
   ```

4. Run the script:

   ```bash
   python script.py <input_pdf_path> <output_folder> --similarity_threshold 80
   ```

## Example

```bash
python script.py sample_invoice.pdf output_folder --similarity_threshold 80
```

This command will:
- Process the `sample_invoice.pdf` file.
- Extract product names and group similar ones based on the similarity threshold (default 80%).
- Save grouped PDFs in the `output_folder` directory.
- Create a combined PDF sorted by the most frequent products.

## Requirements

- Python 3.12+
- Tesseract OCR
- Dependencies listed in `requirements.txt`:
  - pdf2image
  - pytesseract
  - pypdf
  - fuzzywuzzy

## Future Improvements

- Support for additional document types and formats.
- Enhancing error handling for various PDF structures.
- Adding a GUI for easier use.

## Contributions

Feel free to fork this project, submit issues, or make pull requests. Any contributions are welcome!
