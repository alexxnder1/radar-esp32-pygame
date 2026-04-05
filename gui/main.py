import pygame
import pygame_gui
import pygame_gui.elements.ui_text_box
import serial
import math


ser = serial.Serial("COM6", 115200, timeout=1)
count=0
angle, distance = (0,0)
running=True

WIDTH=500
HEIGHT=500

# FOR MY WIDTH, HEIGHT THE RADIUS
RADIUS = WIDTH/2
MAX_RADIUS_FOR_SENSOR = 150



pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Radar")
clock=pygame.time.Clock()

manager = pygame_gui.UIManager((WIDTH, HEIGHT))
angleLabel = pygame_gui.elements.UILabel(text="Starting...", relative_rect=pygame.Rect((0,0),(100,50)), manager=manager)
Max = pygame_gui.elements.UILabel(text="Starting...", relative_rect=pygame.Rect((0,50),(100,50)), manager=manager)
Min = pygame_gui.elements.UILabel(text="Starting...", relative_rect=pygame.Rect((0,100),(100,50)), manager=manager)
ResetButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH-100, 0), (100, 50)), text="Reset", manager=manager)
StopButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH-100, 50), (100, 50)), text="Stop", manager=manager)
StartButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH-100, 100), (100, 50)), text="Start", manager=manager)

points = []
minValue = math.inf
maxValue = -math.inf

justReseted = False


def Stop():
    ser.write(b'STOP\n')
    # print("Stop")


def Start():
    ser.write(b'START\n')
    # print("Start")

def Reset():
    global justReseted

    if justReseted == True:
        return

    points.clear()
    
    global minValue, maxValue
    minValue=math.inf
    maxValue=-math.inf

    ser.write(b'RESET\n')
    # print("Reset")
    justReseted=True

# Stop()
def map_range(x, A, B, C, D):
    y = C + (x - A) * (D - C) / (B - A)
    return y

cx = RADIUS
cy = HEIGHT

radar_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# main
for i in range(5):
    pygame.draw.circle(radar_bg, (0, 50 if i != 0 else 255-50*i, 0), (cx, cy), RADIUS-50*i, 2)

preDefAngles = []
step = math.pi/8
n = int(math.pi/step)+1

for i in range(n):
    preDefAngles.append((i)*step)

for ang in preDefAngles:
    point = (cx+RADIUS*math.cos(ang), cy-RADIUS*math.sin(ang))

    if ang != 0 and ang != math.pi:
        lbl = pygame_gui.elements.UILabel(text=f"{round(math.degrees(ang))}°", relative_rect=pygame.Rect((point[0]-50/2, point[1]-25),(50,25)), manager=manager)
    
    # test.append(lbl)
    pygame.draw.line(radar_bg, (0, 50, 0), (cx, cy), point, 3)
        
while running:
    time_delta = clock.tick(60)
    for event in pygame.event.get():
        manager.process_events(event)
        
        if event.type == pygame.QUIT:
            running=False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == ResetButton:
                Reset()
            elif event.ui_element == StopButton:
                Stop()
            elif event.ui_element == StartButton:
                Start()


    manager.update(time_delta)
    screen.fill((0,0,0))
    manager.draw_ui(screen)
    # pygame.display.update()
    pygame.draw.line(screen, (0, 255, 0), (cx, cy), (cx+RADIUS*math.cos(math.radians(angle)), cy-RADIUS*math.sin(math.radians(angle))), 3)

    screen.blit(radar_bg, (0,0))
    # targets
    for point in points:
        pygame.draw.circle(screen, (255, 0, 0), point, 3)   

    while ser.in_waiting:
        # if ser.readline().count() < 0:
        #     continue

        line = ser.readline().decode().strip()
        if line:
            try:
                angle, distance = map(float, line.split(","))

                if angle == 0 or angle == 180:
                    Reset()

                else: justReseted = False

                if distance > MAX_RADIUS_FOR_SENSOR:
                    continue
                
                minValue = min(minValue, distance)
                maxValue = max(maxValue, distance)

                angleLabel.set_text(f"Angle: {angle}°")
                Min.set_text(f"Min: {minValue}cm")
                Max.set_text(f"Max: {maxValue}cm")
            
                r = map_range(distance, 0, MAX_RADIUS_FOR_SENSOR, 0, RADIUS)
                points.append((cx+r*math.cos(math.radians(angle)), cy-r*math.sin(math.radians(angle))))

            except:
                pass

    
    pygame.display.flip()

pygame.quit()