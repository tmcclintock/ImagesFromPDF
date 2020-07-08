# ImagesFromPDF

A python script to pull images from a PDF, and then make
backgrounds transparent with `ImageMagick`. Images are saved
as `png` files.

## Requirements

The first requirement is [`pdfreader`](https://github.com/maxpmaxp/pdfreader),
which is a Python package for manipulating PDFs. It can be installed with
`pip` using
```bash
$ pip install pdfreader
```
There are other install options detailed in that repository. Note that
you must be using Python 3.X to use `pdfreader`.

The other requirement is [`ImageMagick`](https://imagemagick.org/index.php),
which is a command-line program for editing images. It is used in
this script to remove white and/or black backgrounds from images.
`ImageMagick` must be installed following the instructions in their
documentation. You can use `brew` if you have a Mac, but the
instructions are slightly more complicated for Windows or Unix users.

## Usage

The script in thie repository is `extract_images_from_pdf.py` and it
can be ran from the command line with
```bash
$ python extract_images_from_pdf.py MyFile.pdf
```

You can run this script with a number of flags that you can set
to enable different features. These include:

* `-o` or `--output`; controls the output directory, by default it will output to `<filename>_images/` where the input file is called `<filename>.pdf`.
* `-v` or `--verbose`; set to `True` by default, controls the amount of output provided.
* `-fp` or `--first_page`; default 0, first page to export from.
* `-lp` or `--last_page`; default 1000, last page to export from.
* `-mw` or `--min_width`; default 200, minimum pixel width of pictures to export.
* `-mh` or `--min_height`; default 200, minimum pixel height of pictures to export.
* `-xw` or `--max_width`; default 200, maximum pixel width of pictures to export.
* `-xh` or `--max_height`; default 200, maximum pixel height of pictures to export.
* `-mt` or `--make_transparent`; default `False`, flag to attempt to make backgrounds transparent.
* `-wt` or `--white_to_trans`; default `True`, if `-mt=True` then flag to make white pixels transparent
* `-bt` or `--black_to_trans`; default `True`, if `-mt=True` then flag to make black pixels transparent.
* `-wf` or `--white_fuzz`; default 1, if white pixels are made transparent, sets the `ImageMagick` fuzz percentage (i.e. sets _almost_ white pixels to transparent as well).
* `-bf` or `--black_fuzz`; default 1, if black pixels are made transparent, sets the `ImageMagick` fuzz percentage (i.e. sets _almost_ black pixels to transparent as well).
* `-ims` or `--image_string`; default is `"Im"`, string that appears in all image names used to indicate which images to pull from the document.

## Example usage

I have a PDF of the [Pathfinder Bestiary](https://paizo.com/products/btpy8auu?Pathfinder-Roleplaying-Game-Bestiary) released by Paizo. I was able to use this script to pull out all monster images into `png` with transparent backgrounds using:
```bash
$ python extract_images_from_pdf.py Bestiary1.pdf -mt=True
```
These images can then be inserted into virtual tabletop software.