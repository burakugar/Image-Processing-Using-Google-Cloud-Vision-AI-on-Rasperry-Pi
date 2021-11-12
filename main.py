from time import sleep
import picamera  # kutuphane import edildi
from google.cloud import vision
import io

client = vision.ImageAnnotatorClient()  # client objesi uzerinden api kullanilacak

def compareStrings(label):
    list = {"PET", "pet", "Pet Bottle", "Bottle", "Water Bottle", "Bottle", "Bottled Water","Plastic Bottle"}
    for string in list:
        if string == "labels":
            return 1
        else:
            return 0
def localize_objects(path):
    # path:image.jpg'nin konumu(aynı klasörde olmalı)
    with open(path, 'rb') as image_file:  # image'i aciyoruz
        content = image_file.read()
    image = vision.Image(content=content)
    objects = client.object_localization(image=image).localized_object_annotations
    f = open("number_of_objects.txt", "w", encoding='utf-8')  # dosya acma
    f.write('{}'.format(len(objects)))
    for object_ in objects:
        f.write('\n{} (confidence: {})'.format(object_.name, object_.score))  # dogruluk orani
        f.write('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            f.write(' - ({}, {})'.format(vertex.x, vertex.y))
    f.close()


def detect_properties(path):
    """Detects image color properties in the file."""
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.image_properties(image=image)
    props = response.image_properties_annotation
    f = open("picture_properties.txt", "w", encoding='utf-8')  # dosya acma
    for color in props.dominant_colors.colors:
        f.write('fraction: {}'.format(color.pixel_fraction))
        f.write('red: {}'.format(color.color.red))
        f.write('green: {}'.format(color.color.green))
        f.write('blue: {}'.format(color.color.blue))
        f.write('alpha: {}'.format(color.color.alpha))
    f.close()

def takephoto():
    camera = picamera.PiCamera()
    camera.start_preview()
    sleep(5)
    camera.capture('/home/pi/Desktop/image.jpg') #desktop üzerinde kod calistirilmali
    camera.stop_preview()


def writefile_logos(logos):  # logo isimlerini dosyaya yazma fonksiyonu
    with open('logos.txt', 'w', encoding='utf-8') as f:  # dosya acma
        for logo in logos:  # listedeki logo isimleri teker teker dosya icine yaziliyor
            print >> f, logo.description
    f.close()


def writefile_labels(labels):  # etiketleri dosyaya yazma fonksiyonu
    with open('labels.txt', 'w', encoding='utf-8') as f:  # dosya acma
        for label in labels:  # listedeki etiketler isimleri teker teker dosya icine yaziliyor
            print >> f, label.description
    f.close()

def main():
    takephoto()  # resim cekildi
    with open('image.jpg', 'rb') as image_file:  # resim dosyasi acildi
        content = image_file.read()  # dosya icerigi contente atandi
    image = vision.types.Image(content=content)
    response = client.label_detection(image=image)  # api uzerinden etiket cevabi alindi ve response objesine atandı
    labels = response.label_annotations  # response objesinin label annotations fonksiyonu kullanilarak etiketler liste olarak cekildi
    if compareStrings(labels) == 0: # labellar karsilastiriliyor
        return 0
    response1 = client.logo_detection(image=image)  # api uzerinden logo cevabi alindi ve response1 objesine atandı
    logos = response1.logo_annotations  # response objesinin logo annotations fonksiyonu kullanilarak logo isimleri liste olarak cekildi
    writefile_logos(logos)
    writefile_labels(labels)
    detect_properties('image.jpg')
    image_file.close()


    main()
