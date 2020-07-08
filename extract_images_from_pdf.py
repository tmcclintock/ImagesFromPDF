"""
Script for extracting PDF images to an album.
"""

import argparse, glob, os, sys
from pdfreader import PDFDocument

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    parser.add_argument("-o", "--output", default=None,
                        help="sets the output directory")
    parser.add_argument("-v", "--verbose", default=False, type=str2bool,
                        const=True, nargs='?',
                        help="increase output verbosity")
    parser.add_argument("-fp", "--first_page", default=0,
                        help="first page to extract from")
    parser.add_argument("-lp", "--last_page", default=1000,
                        help="last page to extract from")
    parser.add_argument("-mw", "--min_width", default=200,
                        help="minimum pixel width")
    parser.add_argument("-mh", "--min_height", default=200,
                        help="minimum pixel height")
    parser.add_argument("-xw", "--max_width", default=1210,
                        help="maximum pixel width")
    parser.add_argument("-xh", "--max_height", default=1570,
                        help="maximum pixel height")
    parser.add_argument("-mt", "--make_transparent", default=True,
                        type=str2bool, const=False, nargs='?',
                        help="flag to make the background transparent")
    parser.add_argument("-wt", "--white_to_trans", default=True,
                        type=str2bool, const=False, nargs='?',
                        help="turn white pixels transparent")
    parser.add_argument("-bt", "--black_to_trans", default=True,
                        type=str2bool, const=False, nargs='?',
                        help="turn black pixels transparent")
    parser.add_argument("-wf", "--white_fuzz", default=1,
                        help="fuzz percent (0-100) for white transparency")
    parser.add_argument("-bf", "--black_fuzz", default=1,
                        help="fuzz percent (0-100) for black transparency")
    parser.add_argument("-ims", "--image_string", default="Im",
                        help="string that appears in all image names")
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
            if args.image_string in key or "im" in key:
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
                            print("did this")
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
            raise Exception(
                "'convert' from ImageMagick not recognized " +
                "either install ImageMagick or run with " +
                "--make_transparent=False"
            )
        pass

    # Make the command and execute
    if args.white_to_trans:
        assert 0 <= args.white_fuzz <= 100, "white_fuzz must be within 0-100"
        cmd = f"convert {inpath} -fuzz {args.white_fuzz}% -transparent " + \
            f"white {outpath}"
        res = os.system(cmd)
        check_result(res)
        if args.black_to_trans:
            inpath = outpath
    if args.black_to_trans:
        assert 0 <= args.black_fuzz <= 100, "black_fuzz must be within 0-100"
        cmd = f"convert {inpath} -fuzz {args.black_fuzz}% -transparent " + \
            f"black {outpath}"
        res = os.system(cmd)
        check_result(res)
        print("here  ",outpath)
    return 0


if __name__ == "__main__":
    main()
