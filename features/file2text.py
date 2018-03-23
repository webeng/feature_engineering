#!/usr/bin/python
# -*- coding: utf-8 -*-

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import textract
from features.pypdf_to_image import convert as convert_pdf_to_image
from time import time
import os


class File2Text(object):
    """docstring for File2Text"""
    def __init__(self):
        super(File2Text, self).__init__()

    def extract(self, src, maxpages=0):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams(line_overlap=0.5,
                     char_margin=2.0,
                     line_margin=0.5,
                     word_margin=0.1,
                     boxes_flow=0.5,
                     detect_vertical=True,
                     all_texts=True)
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        # device = TextConverter(rsrcmgr, retstr, codec=codec)
        fp = file(src, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        caching = True
        pagenos = set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        return text

    def extract_all(self, src, maxpages=0):
        if '.pdf' in src:
            try:
                start = time()
                text = self.extract(src, maxpages=maxpages)
                print "case 1 elapsed_time {}s".format(time() - start)
            except Exception, e:
                start = time()
                text = textract.process(src)
                print "case 2 elapsed_time {}s".format(time() - start)

        else:
            # TODO: allow other formats
            # return None
            start = time()
            text = textract.process(src)
            print "case 3 elapsed_time {}s".format(time() - start)


        # if text and len(text.strip()) == 0:
        #   text = None

        if not text or len(text) < 10:
            # TODO: Speed this process up
            # return None
            print "...attempting convert_pdf_to_image"
            start = time()
            pdf_path = convert_pdf_to_image(src)
            text = textract.process(pdf_path)
            os.remove(pdf_path)
            print "case 4 elapsed_time {}s".format(time() - start)

        return text

if __name__ == '__main__':
    src = '/Volumes/FLUFFUSHFS/Datasets/product_properties/data/documents/105293334418129088138c7cf90dacf7_hush-acoustics_Hush-Panel-32_Specifications_NR282-12-Hush-Panel-32.pdf'
    # src = '/Volumes/FLUFFUSHFS/Datasets/product_properties/data/documents/0a3a09b2ddb9615ba06cb2f7b812a3b4_ruukki-uk_C-purlin_Technical-Files_LP-IN05-EN.pdf'
    #print File2Text.extract(src)
    pdf2text = File2Text()
    # print File2Text.extract(src)
    print pdf2text.extract_all(src)
    # print convert_pdf_to_txt(src)
