"""
Script for extracting PDF images to an album.
"""

import os
from pdfreader import PDFDocument
import begin


def _do_transparent(white_to_trans, black_to_trans, white_fuzz, black_fuzz, i, key, im, output):
    if not white_to_trans and not black_to_trans:
        raise Exception("set either white_to_trans or black_to_trans to True")

    inpath = f"{output}/page{i}_{key}.png"
    outpath = "{output}/page{i}_{key}_{s}.png"
    cmd = "convert {inpath} -transparent {color} {outpath}"

    # Figure out paths
    if white_to_trans and black_to_trans:
        s = "nowhite_noblack"
        color = None
    elif white_to_trans:
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
    if white_to_trans:
        assert 0 <= white_fuzz <= 100, "white_fuzz must be within 0-100"
        cmd = f"convert {inpath} -fuzz {white_fuzz}% -transparent " + \
            f"white {outpath}"
        res = os.system(cmd)
        check_result(res)
        if black_to_trans:
            inpath = outpath
    if black_to_trans:
        assert 0 <= black_fuzz <= 100, "black_fuzz must be within 0-100"
        cmd = f"convert {inpath} -fuzz {black_fuzz}% -transparent " + \
            f"black {outpath}"
        res = os.system(cmd)
        check_result(res)
    return 0


@begin.start(auto_convert=True)
def main(file_name: 'the pdf to extract from',
         output: 'sets the output directory name' = None,
         verbose: 'increase output verbosity' = False,
         first_page: 'first page to extract from' = 0,
         last_page: 'last page to extract from' = 1000,
         min_width: 'minimum pixel width' = 200,
         min_height: 'minimum pixel height' = 200,
         max_width: 'maximum pixel width' = 1210,
         max_height: 'maximum pixel height' = 1570,
         make_transparent: 'flag to make the background transparent' = True,
         white_to_trans: 'turn white pixels transparent' = True,
         black_to_trans: 'turn black pixels transparent' = True,
         white_fuzz: 'fuzz percent (0-100) for white transparency' = 1,
         black_fuzz: 'fuzz percent (0-100) for black transparency' = 1,
         image_string: 'string that appears in all image names' = 'Im',
         ):

    # Obtain the base filename
    assert os.path.exists(file_name), f"{file_name} not found"
    assert file_name[-4:] == ".pdf", "must provide '.pdf' file"
    base_file_name = file_name[:-4]
    # Split on slashes
    base_file_name = base_file_name.split("/")[-1]
    base_file_name = base_file_name.split("\\")[-1]
    assert len(base_file_name) > 0

    # Make the output directory
    output = output or base_file_name + "_images"
    output = './' + output
    if verbose:
        print(f"Outputting to {output}/")
    os.makedirs(output, exist_ok=True)

    # Import the pdfreader
    fd = open(file_name, "rb")
    doc = PDFDocument(fd)

    # Check pages
    assert first_page > -1
    assert last_page > -1
    assert last_page > first_page

    # Loop over pages
    for i, page in enumerate(doc.pages()):
        if i < first_page:
            continue
        if i >= last_page:
            exit()
        if verbose:
            nkeys = len(page.Resources.XObject.keys())
            print(f"On page {i} -- {nkeys} XObjects detected")

        # Loop over possible image objects
        for key in page.Resources.XObject.keys():
            if image_string in key or "im" in key.lower():
                xobj = page.Resources.XObject[key]
                try:
                    pil_image = xobj.to_Pillow()
                except IndexError:
                    if verbose:
                        print(
                            f"IndexError raised on page {i} {key} - skipping"
                        )
                    continue
                width, height = pil_image.size
                if width < max_width and height < max_height:
                    if width > min_width and height > min_height:
                        if verbose:
                            print(
                                f"Saving image {key} on page{i}: "+\
                                f"(w,h)={pil_image.size}"
                            )
                        pil_image.save(f"{output}/page{i}_{key}.png")
                        if make_transparent:
                            _do_transparent(white_to_trans, black_to_trans, white_fuzz, black_fuzz, i, key, pil_image, output)