import numpy as np
import cv2
import os

class YoloDetector(object):

	def __init__(self, yolo_path):

		self.input_confidence = 0.1
		self.threshold = 0.5

		labels_path = os.path.sep.join([yolo_path, "yolo.names"])
		self.LABELS = open(labels_path).read().strip().split("\n")

		np.random.seed(42)
		self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3),
								   dtype="uint8")

		weightsPath = os.path.sep.join([yolo_path, "yolo.weights"])
		configPath = os.path.sep.join([yolo_path, "yolo.cfg"])

		self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
		ln = self.net.getLayerNames()
		self.ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
		(self.W, self.H) = (None, None)

	def detect(self, frame):

		if self.W is None or self.H is None:
			(H, W) = frame.shape[:2]

		blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
									 swapRB=True, crop=False)

		self.net.setInput(blob)
		layerOutputs = self.net.forward(self.ln)

		# initialize our lists of detected bounding boxes, confidences,
		# and class IDs, respectively
		boxes = []
		confidences = []
		classIDs = []
		objects = []

		# loop over each of the layer outputs
		for output in layerOutputs:
			# loop over each of the detections
			for detection in output:
				# extract the class ID and confidence (i.e., probability)
				# of the current object detection
				scores = detection[5:]
				classID = np.argmax(scores)
				confidence = scores[classID]
				# filter out weak predictions by ensuring the detected
				# probability is greater than the minimum probability
				if confidence > self.input_confidence:
					# scale the bounding box coordinates back relative to
					# the size of the image, keeping in mind that YOLO
					# actually returns the center (x, y)-coordinates of
					# the bounding box followed by the boxes' width and
					# height
					box = detection[0:4] * np.array([W, H, W, H])
					(centerX, centerY, width, height) = box.astype("int")
					# use the center (x, y)-coordinates to derive the top
					# and and left corner of the bounding box
					x = int(centerX - (width / 2))
					y = int(centerY - (height / 2))
					# update our list of bounding box coordinates,
					# confidences, and class IDs
					boxes.append([x, y, int(width), int(height)])
					confidences.append(float(confidence))
					classIDs.append(classID)

		# apply non-maxima suppression to suppress weak, overlapping
		# bounding boxes
		idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.input_confidence,
								self.threshold)

		# ensure at least one detection exists
		if len(idxs) > 0:
			# loop over the indexes we are keeping
			for i in idxs.flatten():
				# add object to objects list
				objects.append(self.LABELS[classIDs[i]])
				# extract the bounding box coordinates
				(x, y) = (boxes[i][0], boxes[i][1])
				(w, h) = (boxes[i][2], boxes[i][3])
				# draw a bounding box rectangle and label on the frame
				color = [int(c) for c in self.COLORS[0]]
				cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
				text = "{}: {:.4f}".format(self.LABELS[classIDs[i]],
										   confidences[i])
				cv2.putText(frame, text, (x, y - 5),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

		return frame, objects