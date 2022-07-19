from ebooklib import epub
from lxml import etree
from getopt import getopt
import sys
import os
import mimetypes

mime_types : mimetypes.MimeTypes = mimetypes.MimeTypes()

extract_mimetype = [
    ('image/webp', '.webp'),
    ('audio/m4a', '.m4a')
]

def add_mimetypes():
    for mime_type,ext in extract_mimetype:
        mime_types.add_type(mime_type, ext)

def print_usage():
    print('html2ebook.py -i <input_dir> -o <output_file> [--help] [--index <index_page>] [--identifier <identifier>] [--title <title>] [--author <author>] [--cover <cover>] [--sort]')
    print('-i --input: input directory')
    print('-o --output: output file')
    print('--help: print this help')
    print('--index: index page. Default is index.html')
    print('--identifier: identifier. Default is "html2ebook"')
    print('--title: title. Default is the title of index page')
    print('--author: author. ')
    print('--cover: cover image. Default is cover.jpg')
    print('--sort: sort files by name')

def get_mime_type(file_name):
    return mime_types.guess_type(file_name)[0]

def get_html_title_info(html_file):
    with open(html_file, 'r',encoding='utf-8') as f:
        html = f.read()
    root = etree.HTML(html)
    title = root.find('head/title').text.strip()

    return (title, html)

def add_html_to_book(book:epub.EpubBook, html_file,file_name):
    '''
    Add html file to book
    
    Args:
        - book: epub.EpubBook object to add html file to
        - html_file: html file to add
    '''
    title,content = get_html_title_info(html_file)
    
    item = epub.EpubHtml(title=title, file_name=file_name)
    item.set_content(content)

    book.add_item(item)

    return item,title

def add_assest_to_book(book:epub.EpubBook, asset_file:str,file_name:str,mime_type:str):
    '''
    Add asset file to book
    
    Args:
        - book: epub.EpubBook object to add asset file to
        - asset_file: asset file to add (real path)
        - file_name: file name of asset file
        - mime_type: mime type of asset file
    '''
    item = epub.EpubItem(file_name=file_name, media_type=mime_type)

    with open(asset_file, 'rb') as f:
        item.set_content(f.read())

    book.add_item(item)

    return item

def main(argv):

    opts,_ = getopt(argv, 'i:o:',["input=", "output=","index=","identifier=","help","sort","author=","title=","cover="])

    input_dir = ''
    output_file = ''
    index_page = 'index.html'
    identifier = 'html2ebook'
    author = ''
    title = ''
    cover = ''
    sort_pages = False

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            input_dir = arg
        elif opt in ('-o', '--output'):
            output_file = arg
        elif opt == '--index':
            index_page = arg
        elif opt == '--identifier':
            identifier = arg
        elif opt == '--title':
            title = arg
        elif opt == '--sort':
            sort_pages = True 
        elif opt == '--author':
            author = arg
        elif opt == '--cover':
            cover = arg
        elif opt == '--help':
            print_usage()
            return
        else:
            print("Unknown option: " + str(opt))
            print_usage()
            sys.exit(1)
    
    if input_dir == '':
        print('Missing input file')
        print_usage()
        sys.exit(1)
    
    book = epub.EpubBook()

    book.set_identifier(identifier)

    if cover != '':
        with open(cover, 'rb') as f:
            file_name = os.path.split(cover)[1]

            book.set_cover(file_name, content=f.read())
        
    if author != '':
        book.add_author(author)

    html_items = []

    add_mimetypes()

    index_link = None
    index_item = None

    for root,_,files in os.walk(input_dir):
        for file in files:
            abs_path = os.path.join(root, file)
            relative_path = os.path.relpath(abs_path, input_dir).replace('\\', '/')

            if file == index_page:
                index_item,page_title = add_html_to_book(book, abs_path, relative_path)
                index_link = epub.Link('index.html', title=page_title,uid = 'index')

                if title == '':
                    book.set_title(page_title)

                continue
                
            if file.endswith('.html'):
                item,_ = add_html_to_book(book, abs_path, relative_path)
                html_items.append(item)
            elif file.endswith('.css'):
                item = add_assest_to_book(book, abs_path, relative_path, 'text/css')
                book.add_item(item)
            else:
                mime_type = get_mime_type(file)
                add_assest_to_book(book, abs_path, relative_path, mime_type)
            
            print('Added ' + file)

    if sort_pages:
        get_index = lambda file_name : os.path.split(file_name)[1].split('.')[0] 

        digit_items = [i for i in html_items if get_index(i.file_name).isdigit()]
        non_digit_items = [i for i in html_items if not get_index(i.file_name).isdigit()]

        digit_items.sort(key=lambda x: int(get_index(x.file_name)))
        non_digit_items.sort(key=lambda x: x.file_name)

        html_items = non_digit_items + digit_items

    book.spine = [index_item,] + html_items

    toc = [index_link,]

    for i in html_items:
        toc.append(epub.Link(i.file_name, title=i.title, uid=i.file_name))
    
    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    if output_file == '':
        output_file = os.path.join(input_dir, title + '.epub')
    
    epub.write_epub(output_file, book)



if __name__ == '__main__':
    main(sys.argv[1:])