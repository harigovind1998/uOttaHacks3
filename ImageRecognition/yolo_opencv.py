import cv2
import argparse
import numpy as np

imgsize = (700,700)

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--config', 
                help = 'path to config file', default="custom/yolov3-tiny.cfg")
ap.add_argument('-w', '--weights', 
                help = 'path to pre-trained weights', default="../backup/yolov3-tiny.backup")
ap.add_argument('-cl', '--classes', 
                help = 'path to objects.names',default="custom/objects.names")
ap.add_argument('-s', '--server',
                help = 'yes to connect to server, no to not', default='no')
args = ap.parse_args()

scores = None
class_id = None
confidence = None

# Get names of output layers, output for YOLOv3 is ['yolo_16', 'yolo_23']
def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Load names classes
classes = None
with open(args.classes, 'r') as f:
    classes = [line.strip() for line in f.readlines()]
print(classes)

#Generate color for each class randomly
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# Define network from configuration file and load the weights from the given weights file
net = cv2.dnn.readNet(args.weights, args.config)

# Define video capture for default cam
cap = cv2.VideoCapture(0)


while cv2.waitKey(1) < 0 or False:

    hasframe, image = cap.read()
    image=cv2.resize(image, imgsize) 
    
    blob = cv2.dnn.blobFromImage(image, 1.0/255.0, imgsize, [0,0,0], True, crop=False)
    Width = image.shape[1]
    Height = image.shape[0]
    net.setInput(blob)
    
    outs = net.forward(getOutputsNames(net))
    
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    
    
    #print(len(outs))
    
    # In case of tiny YOLOv3 we have 2 output(outs) from 2 different scales [3 bounding box per each scale]
    # For normal normal YOLOv3 we have 3 output(outs) from 3 different scales [3 bounding box per each scale]
    
    # For tiny YOLOv3, the first output will be 507x6 = 13x13x18
    # 18=3*(4+1+1) 4 boundingbox offsets, 1 objectness prediction, and 1 class score.
    # and the second output will be = 2028x6=26x26x18 (18=3*6) 
    
    for out in outs: 
        #print(out.shape)
        for detection in out:
            
        #each detection  has the form like this [center_x center_y width height obj_score class_1_score class_2_score ..]
            scores = detection[5:]#classes scores starts from index 5
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.75:
                print(classes[class_id])
                print(detection[0])
                print(detection[1])
            

        # idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],args["threshold"])

        # if len(idxs) > 0:
        #     for a in idxs.flatten():
        #         text = "{}: {:.4f}".format(classes[class_id[a]], confidences[a])
        #         print(text)
                 
    # apply non-maximum suppression algorithm on the bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
   
    # Put efficiency information.
    t, _ = net.getPerfProfile()
    label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
    cv2.putText(image, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 0, 0))
    # cv2.imshow("window_title", image)