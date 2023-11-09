from imutils.video import FPS
import numpy as np
import argparse
import cv2
import os
import smtplib
import imghdr
from email.message import EmailMessage

#def yolo_detection():
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-y", "--yolo", required=True,
	help="base path to YOLO directory")
ap.add_argument("-i", "--input", type=str, default="",
	help="path to (optional) input video file")
ap.add_argument("-o", "--output", type=str, default="",
	help="path to (optional) output video file")
ap.add_argument("-d", "--display", type=int, default=1,
	help="whether or not output frame should be displayed")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
ap.add_argument("-t", "--threshold", type=float, default=0.3,
	help="threshold when applyong non-maxima suppression")
ap.add_argument("-u", "--use-gpu", type=bool, default=0,
	help="boolean indicating if CUDA GPU should be used")
args = vars(ap.parse_args())

# load the weapons class labels
labelsPath = os.path.sep.join([args["yolo"], "obj.names"])
LABELS = open(labelsPath).read().strip().split("\n")

# initialize a list of colors to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	dtype="uint8")

# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.sep.join([args["yolo"], "yolov3_1.weights"])
configPath = os.path.sep.join([args["yolo"], "yolov3_custom.cfg"])

# load our YOLO object detector trained on COCO dataset (80 classes)
print("Loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

# check if we are going to use GPU
#if args["use_gpu"]:
# set CUDA as the preferable backend and target
	#print("Setting preferable backend and target to CUDA...")
	#net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
	#net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# determine only the *output* layer names that we need from YOLO
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# initialize the width and height of the frames in the video file
W = None
H = None

# initialize the video stream and pointer to output video file, then
# start the FPS timer
print("Accessing video stream...")
vs = cv2.VideoCapture(args["input"] if args["input"] else 0)
success, image = vs.read()
count = 0
success = True
writer = None
fps = FPS().start()
countTime = 10
nameImg = []
take_picture = []
name_Img = []
cwd = os.getcwd()
EMAIL_ADDRESS = 'mrjokezzz19@gmail.com'
EMAIL_PASSWORD = 'uwfondvblnijdkkl'
# loop over frames from the video file stream
while True:
	# read the next frame from the file
	(grabbed, frame) = vs.read()

	# if the frame was not grabbed, then we have reached the end
	# of the stream
	if not grabbed:
		break

	# if the frame dimensions are empty, grab them
	if W is None or H is None:
		(H, W) = frame.shape[:2]

	# construct a blob from the input frame and then perform a forward
	# pass of the YOLO object detector, giving us our bounding boxes
	# and associated probabilities
	blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
		swapRB=True, crop=False)
	net.setInput(blob)
	layerOutputs = net.forward(ln)
	# initialize our lists of detected bounding boxes, confidences, and class IDs, respectively
	boxes = []
	confidences = []
	classIDs = []
	# loop over each of the layer outputs
	for output in layerOutputs:
		# loop over each of the detections
		for detection in output:
			# extract the class ID and confidence (i.e., probability) of the current object detection
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]
			
            #confidence of the detection
			if confidence > args["confidence"]: 
				
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
				idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
					args["threshold"])

                # ensure at least one detection exists
                # apply non-maxima suppression to suppress weak, overlapping
                # bounding boxes
				if len(idxs) > 0:
					# loop over the indexes we are keeping
					for i in idxs.flatten():
						# extract the bounding box coordinates
						(x, y) = (boxes[i][0], boxes[i][1])
						(w, h) = (boxes[i][2], boxes[i][3])

						# draw a bounding box rectangle and label on the frame
						color = [int(c) for c in COLORS[classIDs[i]]]
						cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
						text = "{}: {:.4f}".format(LABELS[classIDs[i]],
							confidences[i])
						cv2.putText(frame, text, (x, y - 5),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
				#delay time to capture an image
				if countTime != 10:
					countTime += 1
				else:
					print('Have an object: ', grabbed)
					cv2.imwrite("%d.jpg" %count, frame)
					countTime = 0
					for file in os.listdir(cwd):
						if "jpg" in file:
							split_file = file.split(".")
							take_picture = split_file[0]
							int_number = int(take_picture)
							name_Img.append(int_number)
							newList = sorted(name_Img)
							nameImg = newList[-1]
							#sending signal message by GMAIL
							msg = EmailMessage()
							msg['Subject'] = 'Warning: Have weapons in the frame'
							msg['From'] = 'Anti-terrorist system | Hau Nguyen'
							msg['To'] = 'hau.nguyen2904@gmail.com'
							msg.set_content('Here is the frame, check it please...')
							with open('%d.jpg' %nameImg, 'rb') as f:
								file_data = f.read()
								file_type = imghdr.what(f.name)
								file_name = f.name
							msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
						else:
							pass
					with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
						smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
						smtp.send_message(msg)
					print(nameImg)
				count += 1
                #print the alarm letter on the frame
				cv2.putText(frame, 'Alarm!!!', (90,125),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0 , 255), 2)

	# check to see if the output frame should be displayed to our screen
	if args["display"] > 0:
		# show the output frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

	# if an output video file path has been supplied and the video
	# writer has not been initialized, do so now
	if args["output"] != "" and writer is None:
		# initialize our video writer
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		writer = cv2.VideoWriter(args["output"], fourcc, 30,
			(frame.shape[1], frame.shape[0]), True)

	# if the video writer is not None, write the frame to the output
	# video file
	if writer is not None:
		writer.write(frame)

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
