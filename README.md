# PDF Tool Pro

PDF Tool Pro is a Python-based desktop application designed for efficient and secure PDF management. This tool was developed as a proactive alternative to established monopolies in the PDF software market and to address the security vulnerabilities associated with web-based PDF converters. 

By running locally, this application ensures that sensitive data never leaves your machine. It is designed to be used as a private home utility or to be integrated into corporate environments as a secure, internal tool that adheres to organizational data-handling procedures.

## Features

- Merge multiple PDF files into a single document.
- Select specific page ranges for extraction and cutting.
- Rotate PDF pages and images before export for correct orientation.
- Support for PNG, JPG, JPEG, and WebP image formats.
- Global drag and drop functionality to import files from any directory.
- Instant toggle between light and dark modes.
- Tactile, responsive UI with visual feedback on all actions.

## Security and Privacy

Unlike online PDF utilities, PDF Tool Pro performs all processing on your local hardware. This makes it suitable for:
- Handling sensitive financial or legal documents.
- Use in restricted corporate environments where external data uploads are prohibited.
- Bypassing subscription-based models for basic document manipulation.

## Prerequisites

The application requires Python 3.x and the following libraries:

- PyQt5 (Interface)
- PyMuPDF / fitz (PDF Rendering)
- PyPDF2 (Backend manipulation)
- Pillow (Image processing)

## Installation

1. Clone this repository:
   git clone https://github.com/RamjeU/PDF-Tool-Pro.git

2. Install dependencies:
   pip install PyQt5 pymupdf PyPDF2 Pillow

3. Launch the tool:
   python PDF_Tool.py

## Usage

1. **Browse**: Use the browse bar or drag files from your computer into the Source panel.
2. **Preview**: Click a file to view its contents. Use the rotation button to fix orientation.
3. **Build**: Define your page ranges (e.g., 1, 3-5) and click "ADD TO BUILD."
4. **Organize**: Use the Move Up/Down buttons to set the final page order.
5. **Export**: Name your file and click "EXPORT PDF." Monitor the status bar for confirmation.
