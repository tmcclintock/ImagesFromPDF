"""
Script for extracting PDF images to an album.
"""

import argparse, glob, os, sys
from pdfreader import PDFDocument


def main():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("-v", "--verbose", default=True,
                        help="increase output verbosity")
    parser.add_argument("-fp", "--first_page", default=0,
                        help="first page to extract from")
    parser.add_argument("-lp", "--last_page", default=1000,
                        help="last page to extract from")
    parser.add_argument("-mw", "--min_width", default=200)
    parser.add_argument("-mh", "--min_height", default=200)
    parser.add_argument("-xw", "--max_width", default=1210)
    parser.add_argument("-xh", "--max_height", default=1570)
    parser.add_argument("-mt", "--make_transparent", default=True)
    parser.add_argument("-wt", "--white_to_trans", default=True)
    parser.add_argument("-bt", "--black_to_trans", default=True)
    args = parser.parse_args()

    if args.verbose:
        print(f"Args:\n\t{args}")

    # Obtain the base filename
    file_name = args.file_name
    assert os.path.exists(file_name)
    assert file_name[-4:] == ".pdf", "must provide '.pdf' file"
    base_file_name = file_name[:-4]
    # Split on slashes
    base_file_name = base_file_name.split("/")[-1]
    base_file_name = base_file_name.split("\\")[-1]
    assert len(base_file_name) > 0

    # Make the output directory
    if args.output is not None:
        output = args.output
    else:
        output = base_file_name + "_images"
        if args.verbose:
            print(f"No output file given; outputing to {output}/")
    os.makedirs(output, exist_ok=True)

    # Import the pdfreader
    fd = open(file_name, "rb")
    doc = PDFDocument(fd)

    # Check pages
    assert args.first_page > -1
    assert args.last_page > -1
    assert args.last_page > args.first_page

    # Loop over pages
    for i, page in enumerate(doc.pages()):
        if i < args.first_page:
            continue
        if i >= args.last_page:
            exit()
        if args.verbose:
            nkeys = len(page.Resources.XObject.keys())
            print(f"On page {i} -- {nkeys} XObjects detected")

        # Loop over possible image objects
        for key in page.Resources.XObject.keys():
            if "Im" in key or "im" in key:
                xobj = page.Resources.XObject[key]
                try:
                    pil_image = xobj.to_Pillow()
                except IndexError:
                    if args.verbose:
                        print(
                            f"IndexError raised on page {i} {key} - skipping"
                        )
                    continue
                width, height = pil_image.size
                if width < args.max_width and height < args.max_height:
                    if width > args.min_width and height > args.min_height:
                        if args.verbose:
                            print(
                                f"Saving image {key} on page{i}: "+\
                                f"(w,h)={pil_image.size}"
                            )
                        pil_image.save(f"{output}/page{i}_{key}.png")
                        if args.make_transparent:
                            _do_transparent(args, i, key, pil_image, output)
    return

def _do_transparent(args, i, key, im, output):
    if not args.white_to_trans and not args.black_to_trans:
        raise Exception("set either white_to_trans or black_to_trans to True")

    inpath = f"{output}/page{i}_{key}.png"
    outpath = "{output}/page{i}_{key}_{s}.png"
    cmd = "convert {inpath} -transparent {color} {outpath}"

    # Figure out paths
    if args.white_to_trans and args.black_to_trans:
        s = "nowhite_noblack"
        color = None
    elif args.white_to_trans:
        s = "nowhite"
        color = "white"
    else:  # args.black_to_trans
        s = "noblack"
        color = "black"
    outpath = outpath.format(output=output, i=i, key=key, s=s)

    def check_result(res):
        if res != 0:
            raise Exception("'convert' from ImageMagick not recognized")
        pass

    # Make the command and execute
    if args.white_to_trans:
        cmd = f"convert {inpath} -fuzz 1% -transparent white {outpath}"
        res = os.system(cmd)
        check_result(res)
        if args.black_to_trans:
            inpath = outpath
    if args.black_to_trans:
        cmd = f"convert {inpath} -fuzz 1% -transparent black {outpath}"
        res = os.system(cmd)
        check_result(res)
    return 0


if __name__ == "__main__":
    main()
