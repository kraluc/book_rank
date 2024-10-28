# book_rank
Identify a list of books and their links to pdf, etc based on desired criteria


# Dependencies

* [google-api-python-client](https://github.com/googleapis/google-api-python-client)
* [pyopenssl](https://pypi.python.org/pypi/pyOpenSSL)
* [WebTest](https://pypi.org/project/WebTest/)

## Getting started

1. Setup API key on Google Books
2. Enable the API Key by visiting the console for the project - see (documentation)[https://developers.google.com/books/docs/v1/getting_started?csw=1]
"https://console.developers.google.com/apis/api/books.googleapis.com/overview?project=964121603531


## Google Books API

### Volumes

```json
---------------- Query API -----------------
url: https://www.googleapis.com/books/v1/volumes?q='high school literature' 'english language'&sort=rating&language:eng&key=<removed>
<bound method Response.json of <Response [200]>>
{
    "kind": "books#volumes",
    "totalItems": 3906,
    "items": [
        {
            "kind": "books#volume",
            "id": "Uuj9wQEACAAJ",
            "etag": "+oC0A+ho/2w",
            "selfLink": "https://www.googleapis.com/books/v1/volumes/Uuj9wQEACAAJ",
            "volumeInfo": {
                "title": "The Complete Guide to High School English Literature",
                "subtitle": "The Most Comprehensive Guide for Four Successful Years of High School in English Language and Literature",
                "authors": [
                    "Amirsaman Zahabioun"
                ],
                "publishedDate": "2018-12-30",
                "description": "The Complete Guide to High School English Literature brings an extraordinary and comprehensive learning experience to all high school students in the field of English language and literature through skill-by-skill instructions and case studies. Whether you are seeking a complete grammar guide or step-by-step techniques to write exemplary essays, The Complete Guide to High School English Literature meets your needs. Amirsaman Zahabioun, the author of The Complete Guide to High School English Literature, published this book as a high school senior. He employs his experience, techniques, and strategies within each lesson to optimize your learning experience. His distinctive approach to language and literature, using case studies particular to each topic, empowers you to read, write, shape, and analyze language appropriately while building a solid chain of skills.",
                "industryIdentifiers": [
                    {
                        "type": "ISBN_10",
                        "identifier": "1793074933"
                    },
                    {
                        "type": "ISBN_13",
                        "identifier": "9781793074935"
                    }
                ],
                "readingModes": {
                    "text": false,
                    "image": false
                },
                "pageCount": 103,
                "printType": "BOOK",
                "maturityRating": "NOT_MATURE",
                "allowAnonLogging": false,
                "contentVersion": "preview-1.0.0",
                "panelizationSummary": {
                    "containsEpubBubbles": false,
                    "containsImageBubbles": false
                },
                "language": "en",
                "previewLink": "http://books.google.com/books?id=Uuj9wQEACAAJ&dq=%27high+school+literature%27+%27english+language%27&hl=&cd=1&source=gbs_api",
                "infoLink": "http://books.google.com/books?id=Uuj9wQEACAAJ&dq=%27high+school+literature%27+%27english+language%27&hl=&source=gbs_api",
                "canonicalVolumeLink": "https://books.google.com/books/about/The_Complete_Guide_to_High_School_Englis.html?hl=&id=Uuj9wQEACAAJ"
            },
            "saleInfo": {
                "country": "US",
                "saleability": "NOT_FOR_SALE",
                "isEbook": false
            },
            "accessInfo": {
                "country": "US",
                "viewability": "NO_PAGES",
                "embeddable": false,
                "publicDomain": false,
                "textToSpeechPermission": "ALLOWED",
                "epub": {
                    "isAvailable": false
                },
                "pdf": {
                    "isAvailable": false
                },
                "webReaderLink": "http://play.google.com/books/reader?id=Uuj9wQEACAAJ&hl=&source=gbs_api",
                "accessViewStatus": "NONE",
                "quoteSharingAllowed": false
            },
            "searchInfo": {
                "textSnippet": "Amirsaman Zahabioun, the author of The Complete Guide to High School English Literature, published this book as a high school senior."
            }
        },]
}
```