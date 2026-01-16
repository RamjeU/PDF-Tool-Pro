# PDF Tool Pro

PDF Tool Pro is a Python-based desktop application designed for efficient PDF management. The tool allows users to merge, cut, and rotate PDF pages through a graphical user interface. It also supports converting various image formats into PDF pages.

## Features

- Merge multiple PDF files into a single document.
- Select specific page ranges for extraction.
- Rotate PDF pages and images before export.
- Support for PNG, JPG, JPEG, and WebP image formats.
- Global drag and drop functionality for adding files.
- Toggle between light and dark modes for a customized workspace.

## Prerequisites

Ensure the following Python libraries are installed before running the application:

- PyQt5
- PyMuPDF (fitz)
- PyPDF2
- Pillow

## Installation

1. Clone the repository to your local machine.
2. Install the required dependencies:
   pip install PyQt5 pymupdf PyPDF2 Pillow
3. Run the application:
   python PDF_Tool.py

## Usage

1. Launch the application.
2. Browse a root folder or drag and drop files directly into the source panel.
3. Select a file to preview pages.
4. Define page ranges and rotate if necessary.
5. Add the selection to the build panel.
6. Reorder items in the build panel using the move up and move down buttons.
7. Enter the desired output name and select Export PDF.