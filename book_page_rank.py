#!/usr/bin/env python
__author__ = "Vincent Ricci"
__email__ = "riccivm@gmail.com"
__status__ = "Development"
__version__ = "0.1.0"
__license__ = "MIT"
__maintainer__ = "Vincent Ricci"
__credits__ = ["Vincent Ricci"]
__created__ = "2024-10-27"

import argparse
import requests
import os
import logging
import sys
import csv
import subprocess
import json
import pandas as pd

""" Web scraping script to extract English Books with fields, Title, Author, ID, Total Number of Pages, and rating from the website https://books.toscrape.com/ """

# LOGGING
""" setup logging with 2 handlers, one for console and one for file """
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

# Set up console logging with logging.INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Set up file logging with logging.DEBUG
file_handler = logging.FileHandler(__file__.replace(".py", ".log"), mode="w")
file_handler.setLevel(logging.DEBUG)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# GLOBAL VARIABLES
URL = "https://openlibrary.org"
LOGGING = True
LOGGING_LEVEL = logging.INFO
LOGGING_FILE = __file__.replace(".py", ".log")
OUTPUT_FILE = __file__.replace(".py", ".csv")
MAX_NUM_PAGES = 300
MINIMUM_RATING = 4.0
MAX_BOOKS = 20


def main(
    count: int = MAX_BOOKS,
    max_num_pages: int = MAX_NUM_PAGES,
    min_rating: float = MINIMUM_RATING,
):
    logger.info("-------------- Logging started --------------")
    logger.info("Number of books: %d", count)
    logger.info("Max number of pages: %d", max_num_pages)
    logger.info("Rating threshold: %.1f", min_rating)

    # Define the search query
    query = "'high school literature' 'english language'"  # .replace(" ", "+")
    url = f"https://openlibrary.org/search.json?q={query}&sort=rating&language:eng"
    logger.debug("url: %s", url)

    # Make the request to the Open Library Search API
    logger.info("---------------- Query API -----------------")
    response = requests.get(url)
    logger.info("%s", response.json)

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch data from Open Library API: {response.status_code}"
        )
        return

    # Parse the JSON response
    data = response.json()
    books = data.get("docs", [])

    # Extract book information
    book_list = []
    logger.debug("fields: %r", books[0].keys())

    for book in books:
        title = book.get("title", "N/A")
        author = ", ".join(book.get("author_name", ["N/A"]))
        book_id = book.get("cover_edition_key", "N/A")
        num_pages = int(book.get("number_of_pages_median", "0"))
        rating = float(book.get("ratings_average", "0"))
        chinese_translation = "Translations into Chinese" in book.get("subject_key", [])
        if book_id == "N/A":
            continue
        book_list.append(
            {
                "Title": title,
                "Author": author,
                "ID": book_id,
                "Total Number of Pages": num_pages,
                "Rating": rating,
                "Chinese Translation": chinese_translation,
            }
        )

    # Get the list of books matching the criteria
    high_rating_books = [
        book
        for book in book_list
        if (
            float(book["Rating"]) >= float(min_rating)
            and 0 < book["Total Number of Pages"] <= max_num_pages
        )
    ]

    logger.warning(f"Number of high rating books: {len(high_rating_books)}")

    # Sort the high_rating_books by low to high number of pages
    sorted_books = sorted(
        high_rating_books, key=lambda x: int(x["Total Number of Pages"]), reverse=True
    )

    # Get the books with available IDs that meet the desired criteria
    top_books = [book for book in sorted_books if book.get("ID") != "N/A"][:count]

    for book in top_books:
        # Retrieve a preview of the book if it exists
        logger.info("Book: %r", json.dumps(book))
        book_id = book.get("ID")
        bookid_query = f"http://openlibrary.org/api/volumes/brief/olid/{book_id}.json"
        bookid_response = requests.get(bookid_query)
        if bookid_response.status_code == 200:
            preview_data = bookid_response.json()
            logger.debug("preview_data: %s", json.dumps(preview_data, indent=4))
            ebooks = (
                preview_data.get("records", {})
                .get(f"/books/{book_id}", {})
                .get("data", {})
                .get("ebooks", {})
            )

            logger.debug("ebooks: %s", json.dumps(ebooks, indent=4))

            preview_url = "N/A"
            epub_url = "N/A"
            pdf_url = "N/A"

            if len(ebooks):
                ebook = ebooks[0]
                preview_url = ebook.get("preview_url", "N/A")
                if preview_url != "N/A":
                    preview_url = f'=HYPERLINK("{preview_url}", "Preview")'
                logger.info(f"preview_url: {preview_url}")
                epub_url = ebook.get("formats").get("epub", {}).get("url", "N/A")
                if epub_url != "N/A":
                    epub_url = f'=HYPERLINK("{epub_url}", "EPUB")'
                logger.info(f"epub_url: {epub_url}")
                pdf_url = ebook.get("formats").get("pdf", {}).get("url", "N/A")
                if pdf_url != "N/A":
                    pdf_url = f'=HYPERLINK("{pdf_url}", "PDF")'
                logger.info(f"pdf_url: {pdf_url}")

        # Add preview to the book information
        book["Preview"] = preview_url
        book["EPUB"] = epub_url
        book["PDF"] = pdf_url

        # Log the book information
        logger.info(
            f"Title: {book['Title']}, Author: {book['Author']}, Pages: {book['Total Number of Pages']}, Rating: {book['Rating']}, Chinese Translation: {book['Chinese Translation']}, Preview: {book['Preview']}, EPUB: {book['EPUB']}, PDF: {book['PDF']}"
        )

    # Write the top 20 books to a separate CSV file
    top_books_output_file = __file__.replace(".py", "_top_20.csv")
    with open(top_books_output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Title",
                "Author",
                "ID",
                "Total Number of Pages",
                "Rating",
                "Chinese Translation",
                "Preview",
                "EPUB",
                "PDF",
            ],
        )
        writer.writeheader()
        writer.writerows(top_books)

    logger.info(f"Top {count} books successfully written to {top_books_output_file}")

    # Open the CSV file in Excel and save it as an Excel file
    try:
        # Read the CSV file
        df = pd.read_csv(top_books_output_file)

        # Save it as an Excel file
        excel_output_file = top_books_output_file.replace(".csv", ".xlsx")
        df.to_excel(excel_output_file, index=False)

        # Open the Excel file
        if sys.platform == "win32":
            os.startfile(excel_output_file)
        else:
            subprocess.run(["open", "-a", "Microsoft Excel.app", excel_output_file])

        logger.info(f"Top {count} books successfully written to {excel_output_file}")
    except Exception as e:
        logger.error(
            f"Failed to open the CSV file in Excel and save it as an Excel file: {e}"
        )

    logger.info("Logging finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Book scraping script")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    # Add option to specify the number of books to return
    parser.add_argument(
        "-n",
        "--num_books",
        type=int,
        default=MAX_BOOKS,
        help="Number of books to return. Default is %d" % MAX_BOOKS,
    )
    # Add option to specify the max number of pages
    parser.add_argument(
        "-m",
        "--max_pages",
        type=int,
        default=250,
        help="Maximum number of pages for a book. Default is %d" % MAX_NUM_PAGES,
    )
    # Add option to specify the rating threshold
    parser.add_argument(
        "-r",
        "--rating_threshold",
        type=float,
        default=4.0,
        help="Minimum rating threshold for a book. Default is %.1f" % MINIMUM_RATING,
    )
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    Count = args.num_books
    MAX_num_pages = args.max_pages
    rating_threshold = args.rating_threshold

    print("executing %r as a module", __file__)
    try:
        main(Count, MAX_num_pages, rating_threshold)
        sys.exit(0)
    except KeyboardInterrupt:
        pass
