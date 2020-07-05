import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer

file_name = "Bestiary2.pdf"
fd = open(file_name, "rb")
doc = PDFDocument(fd)

print(doc.root.Type)
print(doc.root.Metadata.Subtype)
print(doc.root.Outlines.First['Title'])


for i, page in enumerate(doc.pages()):
    if i == 292:
        break
    # print(page.keys())
    # print(page.Resources.XObject.keys())
    nkeys = len(page.Resources.XObject.keys())
    print(f"On page {i} -- {nkeys} XObjects detected")
    for key in page.Resources.XObject.keys():
        if "Im" in key:
            xobj = page.Resources.XObject[key]
            try:
                pil_image = xobj.to_Pillow()
            except IndexError:
                print(
                    f"IndexError raised on page {i} {key} - skipping"
                )
                continue
            width, height = pil_image.size
            if width < 1260 and height < 1635:
                if width > 200 and height > 200:
                    print(i, key, pil_image.size)
                    pil_image.save(f"images/page{i}_{key}.png")

#xobj = page.Resources.XObject['Im1']
#pil_image = xobj.to_Pillow()
#print(pil_image.size)
#pil_image.save("test_image.png")

#viewer = SimplePDFViewer(fd)
#viewer.navigate(0)  # randomly chosen page
#viewer.render()
