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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_API_URL = "https://openlibrary.org"
LOGGING = True
LOGGING_LEVEL = logging.INFO
LOGGING_FILE = __file__.replace(".py", ".log")
OUTPUT_FILE = __file__.replace(".py", ".csv")
MAX_NUM_PAGES = 300
MINIMUM_RATING = 4.0
MAX_BOOKS = 20


def googlebooks_search(query: str):
    # Define the search query for Google Books API
    query = f"{query}"
    url = f"{GOOGLE_BOOKS_API_URL}?q={query}&key={GOOGLE_API_KEY}"
    logger.debug("url: %s", url)

    # Make the request to the Google Books API
    response = requests.get(url)
    logger.info("%s", response.json)

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch data from Google Books API: {response.status_code}"
        )
        sys.exit(1)

    # Parse the JSON response
    data = response.json()
    return data


def open_library_search(query: str):
    # Define the search query for openlibrary

    url = f"https://openlibrary.org/search.json?q={query}"
    logger.debug("url: %s", url)

    # Make the request to the Open Library Search API
    response = requests.get(url)
    logger.info("%s", response.json)

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch data from Open Library API: {response.status_code}"
        )
        return

    # Parse the JSON response
    data = response.json()
    return data


def main(
    api: str = "openlibrary",
    count: int = MAX_BOOKS,
    max_num_pages: int = MAX_NUM_PAGES,
    min_rating: float = MINIMUM_RATING,
):
    logger.info("-------------- Logging started --------------")
    logger.info("Number of books: %d", count)
    logger.info("Max number of pages: %d", max_num_pages)
    logger.info("Rating threshold: %.1f", min_rating)

    # Define the search query for openlibrary
    query = "'high school literature' 'english language'"  # .replace(" ", "+")
    query += "&sort=rating&language:eng"

    logger.info("---------------- Query API -----------------")

    # Initialize the book list
    book_list = []

    if api == "googlebooks":
        data = googlebooks_search(query)
        logger.info(json.dumps(data, indent=4))
        books = data.get("items", [])

        # Extract book information from the JSON response
        logger.debug("fields: %r", books[0].keys())

        for book in books:
            title = book.get("volumeInfo", {}).get("title", "N/A")
            authors = book.get("volumeInfo", {}).get("authors", [])
            author = ", ".join(authors) if authors else "N/A"
            book_id = book.get("id", "N/A")
            num_pages = book.get("volumeInfo", {}).get("pageCount", 0)
            rating = book.get("volumeInfo", {}).get("averageRating", 0)
            language = book.get("volumeInfo", {}).get("language", "N/A")
            preview_url = book.get("volumeInfo", {}).get("previewLink", "N/A")
            categories = book.get("volumeInfo", {}).get("categories", [])

            if book.get("accessInfo", {}).get("epub", {}).get("isAvailable", False):
                epub_url = (
                    book.get("accessInfo", {})
                    .get("epub", {})
                    .get("downloadLink", "N/A")
                )
            else:
                epub_url = "N/A"

            if book.get("accessInfo", {}).get("pdf", {}).get("isAvailable", False):
                pdf_url = (
                    book.get("accessInfo", {}).get("pdf", {}).get("downloadLink", "N/A")
                )
            else:
                pdf_url = "N/A"

            if book_id == "N/A":
                continue
            book_list.append(
                {
                    "Title": title,
                    "Author": author,
                    "ID": book_id,
                    "Total Number of Pages": num_pages,
                    "Rating": rating,
                    "language": language,
                    "Preview": preview_url,
                    "EPUB": epub_url,
                    "PDF": pdf_url,
                    "Categories": ", ".join(categories),
                }
            )

    elif api == "openlibrary":
        data = open_library_search(query)
        books = data.get("docs", [])

        # Extract book information from the JSON response
        logger.debug("fields: %r", books[0].keys())

        for book in books:
            title = book.get("title", "N/A")
            author = ", ".join(book.get("author_name", ["N/A"]))
            book_id = book.get("cover_edition_key", "N/A")
            num_pages = int(book.get("number_of_pages_median", "0"))
            rating = float(book.get("ratings_average", "0"))
            language = book.get("language", "N/A")
            categories = book.get("subject", ["N/A"])

            if book_id == "N/A":
                continue
            book_list.append(
                {
                    "Title": title,
                    "Author": author,
                    "ID": book_id,
                    "Total Number of Pages": num_pages,
                    "Rating": rating,
                    "Language": language,
                    "Categories": ", ".join(categories),
                }
            )

    else:
        logger.warning("Invalid API specified. Exiting...")
        sys.exit(0)

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

    if api == "openlibrary":
        logger.info("*** Using GoogleBooks API to get missing attributes ***")
        # Get the missing attributes for the top books
        for book in top_books:

            title = book.get("Title")
            logger.info("Title: %s", title)
            # Retrieve ebooks attributes using the GoogleBook API
            googlebooks_data = googlebooks_search(
                "intitle:%s" % title.replace(" ", "+")
            )
            logger.debug(
                "Google Books Data: %s", json.dumps(googlebooks_data, indent=2)
            )
            googlebooks_books = googlebooks_data.get("items", [])
            logger.debug("Google Books: %s", json.dumps(googlebooks_books, indent=2))

            googlebook = googlebooks_books[0]

            logger.info("VolumeInfo %r", googlebook.get("volumeInfo", {}))
            preview_url = googlebook.get("volumeInfo", {}).get("previewLink", "N/A")

            logger.info("preview_url available: %s", preview_url)
            categories = googlebook.get("volumeInfo", {}).get("categories", [])

            epub_url = (
                googlebook.get("accessInfo", {})
                .get("epub", {})
                .get("acsTokenLink", "N/A")
            )
            logger.info("epub_url available: %s", epub_url)
            pdf_url = googlebook.get("accessInfo", {}).get("webReaderLink", "N/A")
            logger.info("webReader url: %s", pdf_url)

            # Add preview to the book information
            book["Preview"] = preview_url
            logger.info("Preview URL: %s", preview_url)
            book["EPUB"] = epub_url
            logger.info("EPUB URL: %s", epub_url)
            book["PDF"] = pdf_url
            logger.info("PDF URL: %s", pdf_url)
            book["Categories"] = ", ".join(categories)

            # Log the book information
            logger.info(
                f"Book: {book['Title']}, Author: {book['Author']}, Pages: {book['Total Number of Pages']}, Rating: {book['Rating']}, Language: {book['Language']}, Categories: {book['Categories']} ,Preview: {book['Preview']}, EPUB: {book['EPUB']}, PDF: {book['PDF']}"
            )

    # Write the top books to a separate CSV file
    top_books_output_file = __file__.replace(".py", "_top.csv")
    with open(top_books_output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Title",
                "Author",
                "ID",
                "Total Number of Pages",
                "Rating",
                "PDF",
                "Preview",
                "EPUB",
                "Language",
                "Categories",
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
        df.to_excel(excel_output_file, index=False, freeze_panes=(1, 1))

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
    # Add option to specify the API Google Books or Open Library
    parser.add_argument(
        "-a",
        "--api",
        type=str,
        choices=["openlibrary", "googlebooks"],
        default="openlibrary",
        help="Specify the API to use: 'openlibrary' or 'googlebooks'. Default is 'openlibrary'.",
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
    api = args.api

    print("executing %r as a module", __file__)
    try:
        main(api, Count, MAX_num_pages, rating_threshold)
        sys.exit(0)
    except KeyboardInterrupt:
        pass
