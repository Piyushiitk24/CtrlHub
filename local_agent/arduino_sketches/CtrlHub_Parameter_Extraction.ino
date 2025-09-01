/*
  ==============================================================
  CtrlHub Parameter Extraction - Unified Arduino Interface
  ==============================================================
  This sketch combines all parameter extraction tests in one program.
  It responds to commands from the CtrlHub local agent to run:
  - Coast-down test for inertia measurement
  - Steady-state test for viscous damping
  - Back-EMF test for motor constants
  
  Pin Configuration (Your Hardware):
  - Motor ENA (PWM Speed): Pin 9
  - Motor IN1 (Direction): Pin 8
  - Motor IN2 (Direction): Pin 7
  - Encoder A: Pin 2 (Interrupt Pin)
  - Encoder B: Pin 3 (Interrupt Pin)
  
  Encoder Details:
  - PPR (Pulses Per Revolution): 600
  - CPR (Counts Per Revolution): 2400 (4x decoding)
*/

// ======================================================
// ENCODER AND MOTOR CONFIGURATION
// ======================================================
const int COUNTS_PER_REVOLUTION = 2400;  // 4 * PPR for quadrature

// Pin Definitions
const int MOTOR_ENA_PIN = 9;
const int MOTOR_IN1_PIN = 8;
const int MOTOR_IN2_PIN = 7;
const int ENCODER_A_PIN = 2;
const int ENCODER_B_PIN = 3;

// 'volatile' variables for interrupt service routines
volatile long encoderPos = 0;

// Global variables for speed calculation
long lastEncoderPos = 0;
unsigned long previousTime = 0;
float rpm = 0;

// Test state management
enum TestState {
  IDLE,
  COAST_DOWN_ACCELERATING,
  COAST_DOWN_LOGGING,
  STEADY_STATE_RUNNING,
  BACK_EMF_RUNNING,
  TEST_COMPLETE
};

TestState currentState = IDLE;
unsigned long testStartTime = 0;
unsigned long testDuration = 0;
int testPWM = 0;

// Test parameters
const int COAST_ACCELERATION_DURATION = 4000;  // 4 seconds
const int COAST_LOGGING_DURATION = 8000;       // 8 seconds
const int DATA_INTERVAL = 50;                  // 50ms between readings

// ======================================================
// INTERRUPT SERVICE ROUTINES (ISRs)
// ======================================================
void readEncoderA() {
  if (digitalRead(ENCODER_B_PIN) != digitalRead(ENCODER_A_PIN)) {
    encoderPos++;
  } else {
    encoderPos--;
  }
}

void readEncoderB() {
  if (digitalRead(ENCODER_A_PIN) == digitalRead(ENCODER_B_PIN)) {
    encoderPos++;
  } else {
    encoderPos--;
  }
}

// ======================================================
// SETUP FUNCTION
// ======================================================
void setup() {
  Serial.begin(9600);
  Serial.println("CtrlHub Parameter Extraction Interface Ready");
  Serial.println("Commands: START_COAST_DOWN, START_STEADY_STATE,pwm,duration, START_BACK_EMF,pwm,duration");
  
  // Initialize motor pins
  pinMode(MOTOR_ENA_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);
  
  // Initialize encoder pins
  pinMode(ENCODER_A_PIN, INPUT_PULLUP);
  pinMode(ENCODER_B_PIN, INPUT_PULLUP);
  
  // Attach interrupts for quadrature encoding
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_PIN), readEncoderA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_B_PIN), readEncoderB, CHANGE);
  
  // Ensure motor is stopped
  stopMotor();
  
  // Initialize timing
  previousTime = millis();
  lastEncoderPos = encoderPos;
}

// ======================================================
// MOTOR CONTROL FUNCTIONS
// ======================================================
void runMotor(int pwmValue) {
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, LOW);
  analogWrite(MOTOR_ENA_PIN, pwmValue);
}

void stopMotor() {
  analogWrite(MOTOR_ENA_PIN, 0);
  digitalWrite(MOTOR_IN1_PIN, LOW);
  digitalWrite(MOTOR_IN2_PIN, LOW);
}

// ======================================================
// SPEED CALCULATION
// ======================================================
float calculateRPM() {
  unsigned long currentTime = millis();
  long currentPos = encoderPos;
  
  float deltaTime = (currentTime - previousTime) / 1000.0;  // Convert to seconds
  long deltaPos = currentPos - lastEncoderPos;
  
  if (deltaTime > 0) {
    // RPM = (pulses/sec) * (60 sec/min) / (counts/rev)
    rpm = (deltaPos / deltaTime) * 60.0 / COUNTS_PER_REVOLUTION;
  }
  
  previousTime = currentTime;
  lastEncoderPos = currentPos;
  
  return rpm;
}

// ======================================================
// COMMAND PROCESSING
// ======================================================
void processCommand(String command) {
  command.trim();
  
  if (command == "START_COAST_DOWN") {
    startCoastDownTest();
  }
  else if (command.startsWith("START_STEADY_STATE")) {
    // Parse: START_STEADY_STATE,150,10
    int firstComma = command.indexOf(',');
    int secondComma = command.indexOf(',', firstComma + 1);
    
    if (firstComma > 0 && secondComma > 0) {
      testPWM = command.substring(firstComma + 1, secondComma).toInt();
      testDuration = command.substring(secondComma + 1).toInt() * 1000; // Convert to ms
      startSteadyStateTest();
    }
  }
  else if (command.startsWith("START_BACK_EMF")) {
    // Parse: START_BACK_EMF,200,5
    int firstComma = command.indexOf(',');
    int secondComma = command.indexOf(',', firstComma + 1);
    
    if (firstComma > 0 && secondComma > 0) {
      testPWM = command.substring(firstComma + 1, secondComma).toInt();
      testDuration = command.substring(secondComma + 1).toInt() * 1000; // Convert to ms
      startBackEMFTest();
    }
  }
  else if (command == "STOP") {
    stopAllTests();
  }
}

// ======================================================
// TEST IMPLEMENTATIONS
// ======================================================
void startCoastDownTest() {
  Serial.println("Starting coast-down test...");
  currentState = COAST_DOWN_ACCELERATING;
  testStartTime = millis();
  runMotor(255);  // Full speed acceleration
}

void startSteadyStateTest() {
  Serial.println("Starting steady-state test...");
  currentState = STEADY_STATE_RUNNING;
  testStartTime = millis();
  runMotor(testPWM);
  
  // Wait for stabilization
  delay(2000);
  Serial.println("Motor stabilized. Recording steady-state data...");
}

void startBackEMFTest() {
  Serial.println("Starting back-EMF test...");
  currentState = BACK_EMF_RUNNING;
  testStartTime = millis();
  runMotor(testPWM);
  
  // Wait for stabilization
  delay(1000);
  Serial.println("Motor stabilized. Recording back-EMF data...");
}

void stopAllTests() {
  currentState = IDLE;
  stopMotor();
  Serial.println("All tests stopped.");
}

// ======================================================
// MAIN LOOP
// ======================================================
void loop() {
  // Check for incoming commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
  
  // Handle test state machine
  switch (currentState) {
    case IDLE:
      // Do nothing, wait for commands
      break;
      
    case COAST_DOWN_ACCELERATING:
      if (millis() - testStartTime >= COAST_ACCELERATION_DURATION) {
        // Switch to coast-down logging
        stopMotor();
        currentState = COAST_DOWN_LOGGING;
        testStartTime = millis();  // Reset timer for logging phase
        
        Serial.println("Phase 2: Power cut. Starting data logging.");
        Serial.println("ElapsedTime(ms),Speed(RPM)");
        
        // Reset speed calculation
        previousTime = millis();
        lastEncoderPos = encoderPos;
      }
      break;
      
    case COAST_DOWN_LOGGING:
      if (millis() - previousTime >= DATA_INTERVAL) {
        float currentRPM = calculateRPM();
        unsigned long elapsed = millis() - testStartTime;
        
        Serial.print(elapsed);
        Serial.print(",");
        Serial.println(currentRPM);
        
        // Check if logging duration is complete
        if (elapsed >= COAST_LOGGING_DURATION) {
          currentState = TEST_COMPLETE;
          Serial.println("Test complete.");
        }
      }
      break;
      
    case STEADY_STATE_RUNNING:
      if (millis() - previousTime >= 1000) {  // Update every second
        float currentRPM = calculateRPM();
        Serial.print("Current Speed: ");
        Serial.print(currentRPM);
        Serial.println(" RPM");
        
        // Check if test duration is complete
        if (millis() - testStartTime >= testDuration) {
          currentState = TEST_COMPLETE;
          stopMotor();
          Serial.println("Steady-state test complete.");
        }
      }
      break;
      
    case BACK_EMF_RUNNING:
      if (millis() - previousTime >= 100) {  // Update every 100ms
        float currentRPM = calculateRPM();
        Serial.print("Current Speed: ");
        Serial.print(currentRPM);
        Serial.println(" RPM");
        
        // Check if test duration is complete
        if (millis() - testStartTime >= testDuration) {
          currentState = TEST_COMPLETE;
          stopMotor();
          Serial.println("Back-EMF test complete.");
        }
      }
      break;
      
    case TEST_COMPLETE:
      // Stay in this state until new command
      break;
  }
}
