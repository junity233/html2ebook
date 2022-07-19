# Html2ebook

Html2ebook is tool that help you convert a html webside to an epub-format ebook.

Html2ebook will copy all files that is in the input directory to the ebook.For .html files,they will be added to the toc and the spine.If `--title` option specificed,those file will be sorted by name.

Usage:

```
html2ebook.py -i <input_dir> -o <output_file> [--index <index_page>] [--identifier <identifier>] [--title <title>] [--sort]
-i --input: input directory
-o --output: output file
--index: index page. Default is index.html
--identifier: identifier. Default is "html2ebook"
--title: title. Default is the title of index page
--sort: sort files by name
```

Example:

```
python3 html2ebook.py -i old_man_and_the_sea -o old_man_and_the_sea.epub --index index.html --identifier mybook --title "The old man and the sea" --sort
```
