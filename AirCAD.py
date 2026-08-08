import cv2
import mediapipe as mp
import math
import numpy as np


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
ret, frame = cap.read()
h, w, _ = frame.shape
#STORING 
strokes = []
current_stroke = []
particles = []
moving_stroke = None
prev_pinch_pos = None

PINCH_THRESHOLD = 35
smooth_factor = 0.8
prev_x, prev_y = 0,0


line_start = None
rect_start = None


MODE_IDLE = 0
MODE_DRAW = 1
MODE_MOVE = 2
MODE_LINE = 3
MODE_RECT = 4
MODE_ERASE = 5

mode = MODE_IDLE


def distance(p1,p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def create_sparks(x, y):

    for _ in range(8):

        angle = np.random.uniform(0, 2*np.pi)
        speed = np.random.uniform(3,8)

        vx = math.cos(angle)*speed
        vy = math.sin(angle)*speed

        particles.append({
            "x":x,
            "y":y,
            "vx":vx,
            "vy":vy,
           "life":np.random.randint(15,30)
        })

def line_points(p1,p2,step=5):
    x1,y1=p1
    x2,y2=p2
    d=int(distance(p1,p2))
    pts=[]
    if d==0: return [p1]

    for i in range(0,d,step):
        t=i/d
        x=int(x1+(x2-x1)*t)
        y=int(y1+(y2-y1)*t)
        pts.append((x,y))

    pts.append(p2)
    return pts


def rect_points(p1,p2,step=5):

    x1,y1=p1
    x2,y2=p2

    pts=[]

    for x in range(min(x1,x2),max(x1,x2),step):
        pts.append((x,y1))

    for y in range(min(y1,y2),max(y1,y2),step):
        pts.append((x2,y))

    for x in range(max(x1,x2),min(x1,x2),-step):
        pts.append((x,y2))

    for y in range(max(y1,y2),min(y1,y2),-step):
        pts.append((x1,y))

    return pts


def fingers_up(lm, hand_label="Right"):

    fingers=[]

    if hand_label=="Right":
        fingers.append(lm[4].x < lm[3].x)
    else:
        fingers.append(lm[4].x > lm[3].x)

    tips=[8,12,16,20]

    for tip in tips:
        fingers.append(lm[tip].y < lm[tip-2].y)

    return fingers


#MAIN loop
while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame,1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    canvas = frame.copy()
    canvas[:] = (0,0,0)

    index_pos=None

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]
        lm = hand.landmark

        label="Right"
        if results.multi_handedness:
            label = results.multi_handedness[0].classification[0].label

        mp_draw.draw_landmarks(canvas, hand, mp_hands.HAND_CONNECTIONS)

        ix,iy=int(lm[8].x*w),int(lm[8].y*h)
        tx,ty=int(lm[4].x*w),int(lm[4].y*h)

        index_pos=(ix,iy)

        pinch_distance = distance((ix,iy),(tx,ty))

        finger_state = fingers_up(lm,label)

        all_open = all(finger_state)
        fist = not any(finger_state)

        #all geustures

        if fist:
            strokes=[]
            current_stroke=[]
            moving_stroke=None

        # ERASE (Thumbs up)
        elif finger_state == [1,0,0,0,0]:

            mode = MODE_ERASE

        elif finger_state[1] and not finger_state[2] and not finger_state[3] and not finger_state[4] and not finger_state[0]:
            mode = MODE_DRAW

        elif finger_state[1] and finger_state[2] and not finger_state[3] and not finger_state[4]:
            mode = MODE_LINE

        elif finger_state[1] and finger_state[4] and not finger_state[2] and not finger_state[3]:
            mode = MODE_RECT

        elif pinch_distance < PINCH_THRESHOLD:
            mode = MODE_MOVE

        elif all_open:
            mode = MODE_IDLE

        else:
            mode = MODE_IDLE


        # drawing
        if mode == MODE_DRAW:

            if prev_x==0 and prev_y==0:
                prev_x,prev_y=index_pos

            x_s=int(prev_x*smooth_factor + ix*(1-smooth_factor))
            y_s=int(prev_y*smooth_factor + iy*(1-smooth_factor))

            index_pos=(x_s,y_s)
            prev_x,prev_y=x_s,y_s

        else:

            prev_x,prev_y=0,0

            if current_stroke:
                strokes.append({"points":current_stroke.copy(),
                                "vx":0,"vy":0,"moving":False})
                current_stroke=[]


        # straight line
        if mode == MODE_LINE:

            if line_start is None:
                line_start=index_pos
            else:
                cv2.line(canvas,line_start,index_pos,(0,255,0),2)

        else:

            if line_start and index_pos:

                strokes.append({
                    "points":line_points(line_start,index_pos),
                    "vx":0,"vy":0,"moving":False
                })

            line_start=None


        # rectangle
        if mode == MODE_RECT:

            if rect_start is None:
                rect_start=index_pos
            else:
                cv2.rectangle(canvas,rect_start,index_pos,(255, 200, 50),2)

        else:

            if rect_start and index_pos:

                strokes.append({
                    "points":rect_points(rect_start,index_pos),
                    "vx":0,"vy":0,"moving":False
                })

            rect_start=None


        # eraser
        if mode == MODE_ERASE:

            erase_radius = 25
            new_strokes = []

            for s in strokes:

                pts = s["points"]
                segment = []

                for p in pts:

                    if distance(p, (tx,ty)) > erase_radius:
                        segment.append(p)

                    else:
                        if len(segment) > 1:
                         new_strokes.append({
                            "points": segment.copy(),
                            "vx": s["vx"],
                            "vy": s["vy"],
                            "moving": False
                         })
                        segment = []

                if len(segment) > 1:
                    new_strokes.append({
                    "points": segment.copy(),
                    "vx": s["vx"],
                    "vy": s["vy"],
                    "moving": False
                })

            strokes = new_strokes

        # pinch & move
        if mode == MODE_MOVE:

            pinch_pos=((ix+tx)//2,(iy+ty)//2)

            if moving_stroke is None:

                for s in reversed(strokes):

                    for px,py in s["points"]:

                        if distance(pinch_pos,(px,py))<20:

                            moving_stroke=s
                            prev_pinch_pos=pinch_pos
                            moving_stroke["moving"]=False
                            break

                    if moving_stroke:
                        break

            else:

                dx=pinch_pos[0]-prev_pinch_pos[0]
                dy=pinch_pos[1]-prev_pinch_pos[1]

                for i in range(len(moving_stroke["points"])):

                    x,y=moving_stroke["points"][i]
                    moving_stroke["points"][i]=(x+dx,y+dy)

                moving_stroke["vx"]=dx
                moving_stroke["vy"]=dy

                prev_pinch_pos=pinch_pos

        else:

            if moving_stroke:
                moving_stroke["moving"]=True

            moving_stroke=None
            prev_pinch_pos=None


  
    if index_pos and mode==MODE_DRAW:
        current_stroke.append(index_pos)


    # bounce
    for s in strokes:

        if s.get("moving", False):

            s["points"] = [(x+s["vx"], y+s["vy"]) for (x,y) in s["points"]]

            xs = [p[0] for p in s["points"]]
            ys = [p[1] for p in s["points"]]

            # Horizontal bounce
            if min(xs) <= 0 and s["vx"] < 0:
                s["vx"] *= -1
                create_sparks(xs[0], ys[0])

            if max(xs) >= w and s["vx"] > 0:
                s["vx"] *= -1
                create_sparks(xs[0], ys[0])

            # Vertical bounce
            if min(ys) <= 0 and s["vy"] < 0:
                s["vy"] *= -1
                create_sparks(xs[0], ys[0])

            if max(ys) >= h and s["vy"] > 0:
                s["vy"] *= -1
                create_sparks(xs[0], ys[0])

            s["vx"] *= 0.95
            s["vy"] *= 0.95

            if abs(s["vx"]) < 0.2 and abs(s["vy"]) < 0.2:
                s["moving"] = False


    #particles
    for p in particles:

        p["x"] += p["vx"]
        p["y"] += p["vy"]

        p["vy"] += 0.2
        p["life"] -= 1

    particles = [p for p in particles if p["life"] > 0]

    glow_canvas = np.zeros_like(canvas)


    for s in strokes:
        color = (255, 200, 50)
        if s==moving_stroke:
            color=(0, 255, 0)
        pts = s["points"]
        for i in range(1,len(pts)):
            p1 = (int(pts[i-1][0]), int(pts[i-1][1]))
            p2 = (int(pts[i][0]), int(pts[i][1]))
            cv2.line(glow_canvas, p1, p2, color, 4)

    for i in range(1,len(current_stroke)):
        p1 = current_stroke[i-1]
        p2 = current_stroke[i]
        cv2.line(glow_canvas, p1, p2, (255, 200, 50), 6)
      
    blur1 = cv2.GaussianBlur(glow_canvas, (11,11), 0)
    blur2 = cv2.GaussianBlur(glow_canvas, (21,21), 0)
    glow_overlay = cv2.addWeighted(blur1, 0.5, blur2, 0.5, 0)
    glow_overlay = cv2.addWeighted(glow_overlay, 1, canvas, 1, 0)


    for s in strokes:
        color = (255, 200, 50)
        if s==moving_stroke:
            color=(0, 255, 0)
        pts = s["points"]
        for i in range(1,len(pts)):
            p1 = (int(pts[i-1][0]), int(pts[i-1][1]))
            p2 = (int(pts[i][0]), int(pts[i][1]))
            cv2.line(glow_overlay, p1, p2, color, 3)

    for i in range(1,len(current_stroke)):
        p1 = current_stroke[i-1]
        p2 = current_stroke[i]
        cv2.line(glow_overlay, p1, p2, (255, 200, 50), 2)

    for p in particles:

        x = int(p["x"])
        y = int(p["y"])

        cv2.circle(glow_overlay, (x,y), 2, (255,255,255), -1)


    cv2.imshow("Hand Drawing with Bounce", glow_overlay)
    if cv2.waitKey(1)==27:
        break

cap.release()
cv2.destroyAllWindows()
