import cv2
import torch
import numpy as np
from yandex_ocr import OCR
from checkText import san
import io
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')


def cut_image(result):
    image_bytes = result.getvalue()
    np_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 640), interpolation=cv2.INTER_LANCZOS4)

    results = model(img)

    results.print()
    boxes = results.xyxy[0].numpy()
    class_names = results.names
    extracted_images = []

    for idx,box in enumerate(boxes):
        x1, y1, x2, y2, conf, cls = box
        class_name = class_names[int(cls)]
        cropped_image = img[int(y1):int(y2), int(x1):int(x2)]
        white_square = np.ones((320, 320, 3), dtype=np.uint8) * 255 
        h, w, _ = cropped_image.shape
        y_offset = (320 - h) // 2
        x_offset = (320 - w) // 2
        white_square[y_offset:y_offset + h, x_offset:x_offset + w] = cropped_image
        white_square = cv2.cvtColor(white_square, cv2.COLOR_RGB2GRAY)

        is_success, buffer = cv2.imencode(".png", white_square)
        io_buf = io.BytesIO(buffer)
        
        # file_name = f"{class_name}_{idx}.jpg"
        # cv2.imwrite(file_name, white_square)
        extracted_images.append((io_buf, class_name))

    fin_res = []
    for el in extracted_images:
        wrd = OCR(el[0],str(el[1]))
        print(wrd)
        if wrd!=None:
            if el[1]!="birthday":
                clean_wrd = san(str(wrd))
                if clean_wrd == None:
                    fin_res.append((wrd, el[1]))
                else:
                    fin_res.append((clean_wrd, el[1]))
            else:
                fin_res.append((wrd,"birthday"))
    return fin_res
        