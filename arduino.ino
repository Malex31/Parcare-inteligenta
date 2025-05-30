#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

LiquidCrystal_I2C lcd_1(0x27, 16, 2);

const int trigPins[4] = {2, 4, 6, 8};
const int echoPins[4] = {3, 5, 7, 9};

const int redPins[4] = {10, 12, A0, A2};
const int greenPins[4] = {11, 13, A1, A3};

// Pinii noilor senzori ultrasonici
const int trigPin1 = 22;
const int echoPin1 = 23;
const int trigPin2 = 24;
const int echoPin2 = 25;

Servo servo1;
Servo servo2;

const int servoPin1 = 30;
const int servoPin2 = 32;

bool servo1Activated = false;
bool servo2Activated = false;

// Număr total de locuri de parcare
const int totalSpots = 4;
int freeSpots = totalSpots;

void setup() {
  lcd_1.init();
  lcd_1.backlight();
  lcd_1.setCursor(0, 0);
  lcd_1.print("Parking System");

  for (int i = 0; i < 4; i++) {
    pinMode(trigPins[i], OUTPUT);
    pinMode(echoPins[i], INPUT);
    pinMode(redPins[i], OUTPUT);
    pinMode(greenPins[i], OUTPUT);
  }

  // Configurare senzori ultrasonici suplimentari
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);

  // Configurare servo motoare
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo1.write(0);
  servo2.write(0);

  Serial.begin(9600);
}

void loop() {



  
 
  long duration1, distance1;
  long duration2, distance2;

  digitalWrite(trigPin1, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin1, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin1, LOW);

  duration1 = pulseIn(echoPin1, HIGH);
  distance1 = (duration1 / 2) / 29.1;

  digitalWrite(trigPin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin2, LOW);

  duration2 = pulseIn(echoPin2, HIGH);
  distance2 = (duration2 / 2) / 29.1;

  // Control Servo 1 (Intrare barieră)
  if (distance1 < 10 && !servo1Activated && freeSpots > 0) {
    
    servo1Activated = true;
    Serial.println("INTRARE");

  } else if (distance1 >= 10 && servo1Activated) {
    servo1.write(0); 
    servo1Activated = false;  // Resetăm starea dacă nu mai este detectat nimic în apropiere
  }


  
    if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command == "OPEN") {
      servo1.write(90);
      Serial.println("Bariera deschisa.");


      
      while (true) {
        digitalWrite(trigPin1, LOW);
        delayMicroseconds(2);
        digitalWrite(trigPin1, HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin1, LOW);
        long dur = pulseIn(echoPin1, HIGH);
        long dist = (dur / 2) / 29.1;
        if (dist < 10) break;
        delay(100);
      }

      // Așteptăm ca mașina să fi trecut complet
      while (true) {
        digitalWrite(trigPin1, LOW);
        delayMicroseconds(2);
        digitalWrite(trigPin1, HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin1, LOW);
        long dur = pulseIn(echoPin1, HIGH);
        long dist = (dur / 2) / 29.1;
        if (dist >= 10) break;
        delay(100);
      }


      delay(500);
      servo1.write(0);
      freeSpots--;
    } else if (command == "CLOSE") {
      servo1.write(0);
      Serial.println("Bariera inchisa.");
    }
  }




  

  

  // Control Servo 2 (Ieșire barieră)
  if (distance2 < 10 && !servo2Activated && freeSpots < totalSpots) {
    servo2.write(90);    // Deschide servo
    //delay(3000);         // Așteaptă 3 secunde
    //servo2.write(0);     // Închide servo  
    servo2Activated = true;
    freeSpots++; // Eliberează un loc de parcare
    

    
  } else if (distance2 >= 10 && servo2Activated) {
    servo2.write(0);   
    servo2Activated = false;  // Resetăm starea dacă nu mai este detectat nimic în apropiere
    Serial.println("EXIT");
  }

  // Actualizăm LED-urile și afișajul LCD
  for (int i = 0; i < 4; i++) {
    long duration, distance;

    // Măsurarea distanței cu senzorul ultrasonic
    digitalWrite(trigPins[i], LOW);
    delayMicroseconds(2);
    digitalWrite(trigPins[i], HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPins[i], LOW);

    duration = pulseIn(echoPins[i], HIGH);
    distance = (duration / 2) / 29.1;
    if (distance < 5) {
      digitalWrite(redPins[i], HIGH);
      digitalWrite(greenPins[i], LOW);
    } else {
      digitalWrite(redPins[i], LOW);
      digitalWrite(greenPins[i], HIGH);
    }
  }
lcd_1.clear();
lcd_1.setCursor(0, 0);

if (freeSpots == 0) {
  lcd_1.print("Parcare ocupata");
} else {
  lcd_1.print("Locuri libere: ");
  lcd_1.setCursor(0, 1);
  lcd_1.print(freeSpots);
  Serial.println(freeSpots);
  
}

delay(1000); 
}