#include <Arduino.h>
#include <Servo.h>

#define RADAR_PWM_PIN 23  

Servo myServo;

int target = 180;
int step = 5;

#define MAX 180
#define MIN 0

#define ECHO 4
#define TRIG 2

void SetTargetAngle(int dgr);
void SetServoStepAngle(int step);

void Reset()
{
  // int val = MIN ? MAX : MIN;
  myServo.write(MAX);
  delay(500);
  SetTargetAngle(MAX);
}

int GetCurrentAngle();

void ResetToClosest()
{
  int val = MIN;
  int angle = GetCurrentAngle();
  if(MAX-angle < angle-MIN)
    val=MAX;

  myServo.write(val);
  delay(250);
  SetTargetAngle(val);
}

void setup() {
  Serial.begin(115200);
  myServo.attach(RADAR_PWM_PIN);

  Reset();

  // 
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
}

long readDistance() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  
  long duration = pulseIn(ECHO, HIGH);
  long distance = duration*0.034 / 2; //cm
  return distance;
}

bool stopped = true;
void Stop()
{
  stopped = true;
}

void Start()
{
  stopped = false;
}

int GetCurrentAngle()
{
  return myServo.read();
}

void SetTargetAngle(int dgr)
{
  target = dgr;
}

void loop() 
{
  // commands
  if (Serial.available()) {
      String command = "";
      while (Serial.available()) {
        char c = Serial.read(); // read one byte
        if (c == '\n') break;   // stop at newline
        command += c;
      }

      command.trim(); 
      if (command == "RESET") ResetToClosest();
      if (command == "STOP") Stop();
      if (command == "START") Start();
    }
  
  if(stopped)
    return;

  int currentAngle = myServo.read();
  if(currentAngle == MAX) SetTargetAngle(MIN);
  else if(currentAngle == MIN) SetTargetAngle(MAX);

  int step =5;
  int newAngle = currentAngle;
  
  if(currentAngle < target)
    newAngle += step;
  
  else if(currentAngle > target)
    newAngle -= step;

  newAngle=constrain(newAngle, MIN, MAX);
  myServo.write(newAngle);
  Serial.printf("%d, %ld\n", myServo.read(), readDistance());
  delay(70);
}