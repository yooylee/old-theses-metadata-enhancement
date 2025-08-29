# Theses, 1910-2010 Collection Metadata Enhancement

## The Spark Behind the Project

There has long been a need to determine how many French-language materials are in our institutional repository. Since this information was not previously captured, I saw an opportunity to explore it through one of our largest collections – the [Theses, 1910-2010 Collection] – which also happens to have incomplete metadata.

[Theses, 1910-2010 Collection]: https://ruor.uottawa.ca/collections/fc050432-dc24-47c5-afdf-f8ace00451df

## How I Approached the Project?

### Considerations

Many reports (references will be added) on artificial intelligence (AI) and its impact on academic libraries highlight metadata as an area where AI can be applied. I saw this project as an opportunity test that idea in practice. I also reflected on broader considerations, including the environmental costs of energy consumption, as well as the ethical and privacy implications of working with our collections. I also questioned whether this was the right balance between human expertise and AI automation.

In the end, I found it was worth exploring for several reasons. The collection includes over 13,000 theses, each averaging 100-200 pages, making it impractical to address manually given limited staff resources. Enhancing metadata for such a large set had never been considered feasible before. Since the work involves repetitive tasks, it presented a strong case for testing AI-driven approaches.

### Environments

In consideration of ethical and privacy concerns, I chose to apply AI – specifically machine learning (ML) – within the secure computing environment of the [Digital Research Alliance of Canada]. This infrastructure provided a trusted space for working with collections while avoiding reliance on commercial platforms like ChatGPT. Beyond security, it also offered the large-scale processing power needed to analyze thousands of lengthy theses efficiently, ensuring that the project could be carried out both responsibly and effectively.

[Digital Research Alliance of Canada]: https://alliancecan.ca/en/services/advanced-research-computing

### Methods
The logic of the work followed these steps:
1. Retrieve all item UUIDs from the collection UUID. 
  * Item UUIDs are required when updating `dc.language` field.
2. Retrieve all bitstream UUIDs associated with each item.
  * Bitstream UUIDs are required to download the corresponding PDF files. [See Python Code](https://github.com/yooylee/old-theses-metadata-enhancement/blob/main/get_bitstreamUUID.py).
3. Download the PDF files into the secure computing environment. [See Python Code](https://github.com/yooylee/old-theses-metadata-enhancement/blob/main/get_download_files.py).
4. Extract text from the PDFs, accounting for both text-based and image-based files.
  * [tesseract](https://github.com/tesseract-ocr/tesseract) and [pytesseract](https://pypi.org/project/pytesseract/): used for extracting text from image-based PDFs (OCR).
  * [pdf2image](https://pypi.org/project/pdf2image/): Applied when direct text extraction was unreliable, particularly with scanned PDFs.
  * [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/): Used to extract text from standard, text-based PDFs.
5. Detect the language of the extracted full text.
  * [langdetect](https://pypi.org/project/langdetect/): a Python port of Google’s language-detection library.
  * [lingua](https://github.com/pemistahl/lingua): a rule-based language detection library for cross-verification.
  * Optimization: To reduce computing power and energy consumption, language detection was performed on only the first 20 pages per thesis, with image conversion set at 100 dpi.
  * [See Python Code](https://github.com/yooylee/old-theses-metadata-enhancement/blob/main/get_lang_detect.py).
6. Conduct quality assurance checks to validate results.
  * Threshold check: Required at least 95% agreement between `langdetect` and `lingua`.
    * Items flagged for disagreement were subject to human verification.
  * Random sampling : Applied a manual review using a 95% confidence level with 5% margin of errors.

## Next Steps
1.	Generate keywords and abstracts (in progress).
2.	Extract additional metadata, including degree, contributor, and department information.
3.	Batch update records in RUOR.
4. Batch update metadata in DataCite, including Publisher using the ROR ID.




