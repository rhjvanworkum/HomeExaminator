import pickle
import cv2
import face_recognition
import imutils

class FaceDetector(object):

    def __init__(self):
        self.face_data = pickle.loads(open('output/encodings.pickle', "rb").read())

    def detect(self, frame):
        # convert the input frame from BGR to RGB then resize it to have
        # a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width=750)
        r = frame.shape[1] / float(rgb.shape[1])
        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)

        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(self.face_data["encodings"], encoding)
            name = "Unknown"

            if True in matches:
                match_index = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in match_index:
                    name = self.face_data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)

            names.append(name)

        # visualization
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # rescale the face coordinates
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        return frame, names