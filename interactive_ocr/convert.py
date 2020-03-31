from PIL import Image
import pytesseract
import cv2
import pandas as pd
import glob
import time
import os

_base = os.path.dirname(os.path.realpath(__file__))
pytesseract.pytesseract.tesseract_cmd = f'{_base}/tesseract-Win64/tesseract.exe'

bad_names = {
    'ORD', '0RD', 'unu', 
    'v.“', 'um,', 'DRD', 
    '., ', 'UKU', 'uKu', 
    '0KD', 'unw', '`OR'}

def read_address_book(filename, i = 0):
    # ---- Post Processing
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    temp = 'tmp/test' + str(i) + '.png'
    cv2.imwrite(temp, gray)
    # ---- Post Processing
    
    img = Image.open(temp)
    (w, h) = img.size
    
    columns = [img.crop((0, 0, w // 2, h)), img.crop((w // 2, 0, w, h))]
    
    margin = 40
    lines = 8
    
    addresses = []
    
    for col in columns:
        for line in range(0, lines):
            (w, h) = col.size
            
            address = col.crop((0, line * h // 8 + margin, w, (line + 1) * (h // 8) + margin))
            addresses.append(address)
            
    text_addresses = []
    for address in addresses:
        data = pytesseract.image_to_string(address).split('\n')
        data = map(lambda x: x.strip(), data)
        data = filter(lambda x: x != '', data)
        data = filter(lambda x: x[:3] not in bad_names, data)
        text_addresses.append(list(data))
        
    return text_addresses

def read_all_pages_seq(images):
    n = len(images)
    data = []
    
    time_start = time.time()
    
    for index, image in enumerate(images):
        data.extend(read_address_book(image, index))
        
        time_past = time.time() - time_start
        time_avg = time_past / (index + 1)
        time_remaining = time_avg * (n - (index + 1))
        percentage = int((index + 1) * 10000 / n) / 100
        
        message = '{0:06.2f}% \t ETA: {1:.2f} minutes \t Time/img: {2:.2f} seconds'.format(
            percentage, time_remaining / 60, time_avg)
        
        print(message)

    time_end = time.time()
    
    print('Took ', time_end - time_start, ' seconds')
    return data

def kernel_read_address_book(x): 
    print(x)
    return list(read_address_book(x[0], x[1]))

#def read_all_pages_par(images):
#    time_start = time.time()
#    
#    with Pool(12) as pool:
#        return [r for r in pool.map(kernel_read_address_book,  enumerate(images[0]))]
#    
#    data = exec_par(images)
#    time_end = time.time()
#    print('Took ', time_end - time_start, ' seconds')
#    return data


def clean_data(data):
    for address in data:
        if len(address) > 0 and len(address[0]) > 0 and address[0][0] != 'M':
            del address[0]
        
    return data
	
def rearrange(cp):
    expanded = cp.join(cp['civilite_prenom_nom'].str.split(' ', 2, expand=True).rename(columns={0: 'civilite', 1: 'prenom', 2: 'nom'}))
    expanded = expanded.join(cp['code_postal_ville'].str.split(' ', 1, expand=True).rename(columns={0: 'code_postal', 1: 'ville'}))
    return expanded


def main():
    import os
    os.makedirs('tmp', exist_ok=True)

    data = clean_data(read_all_pages_seq(glob.glob('images/*')[:]))
    data = pd.DataFrame(data)
    data.to_excel('fichier.xlsx')

if __name__ == '__main__':
    main()
