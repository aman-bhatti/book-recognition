import requests

def get_book_info(title):
    api_key = 'your_google_books_api_key'  # Replace with your API key
    url = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    if 'items' in data:
        book = data['items'][0]['volumeInfo']
        # Return book details
        return f"Title: {book.get('title')}\nAuthor: {', '.join(book.get('authors', []))}\nDescription: {book.get('description')}"
    else:
        return "Book information not found."
