from imutils import paths
import face_recognition
import pickle
import cv2

def save_faces():
    #settings
    dataset = './dataset/faces_dataset/'
    detection_method = 'hog'
    output_file = 'output/encodings.pickle'

    image_path_list = list(paths.list_images(dataset))
    face_encodings = []
    face_names = []

    for (i, image_path) in enumerate(image_path_list):
        name = image_path.split('/')[-1].split('\\', 1)[0] #hard-coded for now
        image = cv2.imread(image_path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model=detection_method)
        encodings = face_recognition.face_encodings(rgb, boxes)
        for encoding in encodings:
            face_encodings.append(encoding)
            face_names.append(name)

    data = {"encodings": face_encodings, "names": face_names}
    f = open(output_file, "wb")
    f.write(pickle.dumps(data))
    f.close()