import cv2
import socketio
import pybase64

sv = True
sio = socketio.Client()
sio.connect('http://localhost:3000', namespaces=['/video'])
@sio.event(namespace='/video')
def stopvideo(data):
    global sv
    sv = data

cap = cv2.VideoCapture(0)
cap.set(3, 960)
cap.set(4, 540)

mog = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
while True:
    if sv:
        print('video on')
        posx = []
        posy = []
        i=0
        ret, frame = cap.read()
        mogframe = mog.apply(frame)
        contours, _ = cv2.findContours(mogframe, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            mmt = cv2.moments(c)
            if mmt['m00'] > 40:
                i=i+1
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)
                cx = int(mmt['m10']/mmt['m00'])
                cy = int(mmt['m01']/mmt['m00'])
                posx.insert(i, cx)
                posy.insert(i, cy)

        
            #pos = '(' + str(cx) + ',' + str(cy) + ')'
            #cv2.putText(frame, pos, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (157, 255, 0), 1, cv2.LINE_AA)
        sio.emit('posdata', {'x': posx, 'y': posy}, namespace='/video')
        #cv2.imshow('video view', mogframe)
        res, sframe = cv2.imencode('.jpg', frame)
        data = pybase64.b64encode(sframe)
        sio.emit('videocamera', data, namespace='/video')
        #cv2.imshow('recttangle view', frame)
    
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
cap.release()
cv2.destroyAllWindows()