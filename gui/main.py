import pygame
import pygame_gui
import pygame_gui.elements.ui_text_box
import serial
import math
from serial_com import SerialCom

serialCom = SerialCom()

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

import config

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

    # event-processing
    for event in pygame.event.get():
        manager.process_events(event)
        if event.type == pygame.QUIT:
            running=False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == ResetButton:
                serialCom.Reset()
            elif event.ui_element == StopButton:
                serialCom.Stop()
            elif event.ui_element == StartButton:
                serialCom.Start()


    manager.update(time_delta)
    screen.fill((0,0,0))
    manager.draw_ui(screen)


    # pygame.display.update()
    pygame.draw.line(screen, (0, 255, 0), (cx, cy), (cx+RADIUS*math.cos(math.radians(angle)), cy-RADIUS*math.sin(math.radians(angle))), 3)

    screen.blit(radar_bg, (0,0))
    # targets
    for point in config.points:
        pygame.draw.circle(screen, (255, 0, 0), point, 3)   

    while serialCom.ser.in_waiting:
        line = serialCom.ser.readline().decode().strip()
        if line:
            try:
                angle, distance = map(float, line.split(","))

                if angle == 0 or angle == 180:
                    serialCom.Reset()

                else: config.justReseted = False

                if distance > MAX_RADIUS_FOR_SENSOR:
                    continue
                
                config.minValue = min(config.minValue, distance)
                config.maxValue = max(config.maxValue, distance)

                angleLabel.set_text(f"Angle: {angle}°")
                Min.set_text(f"Min: {config.minValue}cm")
                Max.set_text(f"Max: {config.maxValue}cm")
            
                r = map_range(distance, 0, MAX_RADIUS_FOR_SENSOR, 0, RADIUS)
                config.points.append((cx+r*math.cos(math.radians(angle)), cy-r*math.sin(math.radians(angle))))

            except:
                pass

    
    pygame.display.flip()

pygame.quit()