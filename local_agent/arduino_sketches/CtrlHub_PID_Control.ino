/*
  ==============================================================
  CtrlHub PID Control - Enhanced Arduino Interface
  ==============================================================
  This sketch extends the parameter extraction functionality
  to include PID control capabilities for the DC Motor PID 
  Control experiment.
  
  Features:
  - All existing parameter extraction tests
  - PID controller implementation
  - Real-time speed control
  - Data logging and reporting
  
  Pin Configuration:
  - Motor ENA (PWM Speed): Pin 9
  - Motor IN1 (Direction): Pin 8
  - Motor IN2 (Direction): Pin 7
  - Encoder A: Pin 2 (Interrupt Pin)
  - Encoder B: Pin 3 (Interrupt Pin)
  
  Commands:
  - SET_PID Kp Ki Kd: Set PID parameters
  - SET_SPEED speed: Set target speed
  - START_PID_CONTROL: Begin PID control loop
  - STOP_PID_CONTROL: Stop PID control
  - GET_SPEED: Get current speed
  - GET_PID_DATA: Get speed, error, output data
*/

#include <PID_v1.h>

// ======================================================
// ENCODER AND MOTOR CONFIGURATION
// ======================================================
const int COUNTS_PER_REVOLUTION = 2400;  // 4 * PPR for quadrature

// Pin Definitions
const int MOTOR_ENA_PIN = 9;   // PWM pin for motor speed
const int MOTOR_IN1_PIN = 8;   // Motor direction pin 1
const int MOTOR_IN2_PIN = 7;   // Motor direction pin 2
const int ENCODER_A_PIN = 2;   // Encoder A (interrupt)
const int ENCODER_B_PIN = 3;   // Encoder B (interrupt)

// Global Variables
volatile long encoderCount = 0;
volatile long lastEncoderCount = 0;
unsigned long lastTime = 0;
unsigned long currentTime = 0;
float currentSpeed = 0.0;  // RPM

// Test control variables
bool testRunning = false;
String currentTest = "";
unsigned long testStartTime = 0;
const int DATA_INTERVAL = 50;  // 50ms between readings

// PID Control Variables
double pidSetpoint = 0.0;     // Target speed (RPM)
double pidInput = 0.0;        // Current speed (RPM)
double pidOutput = 0.0;       // PID output (PWM value)
double pidKp = 1.0, pidKi = 0.1, pidKd = 0.01;  // PID gains
bool pidControlActive = false;

// Create PID controller
PID pidController(&pidInput, &pidOutput, &pidSetpoint, pidKp, pidKi, pidKd, DIRECT);

// ======================================================
// INTERRUPT SERVICE ROUTINES (ISRs)
// ======================================================
void readEncoderA() {
  bool A = digitalRead(ENCODER_A_PIN);
  bool B = digitalRead(ENCODER_B_PIN);
  
  if (A == B) {
    encoderCount--;
  } else {
    encoderCount++;
  }
}

void readEncoderB() {
  bool A = digitalRead(ENCODER_A_PIN);
  bool B = digitalRead(ENCODER_B_PIN);
  
  if (A == B) {
    encoderCount++;
  } else {
    encoderCount--;
  }
}

// ======================================================
// SETUP FUNCTION
// ======================================================
void setup() {
  Serial.begin(9600);
  
  // Initialize motor pins
  pinMode(MOTOR_ENA_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);
  
  // Initialize encoder pins
  pinMode(ENCODER_A_PIN, INPUT_PULLUP);
  pinMode(ENCODER_B_PIN, INPUT_PULLUP);
  
  // Attach interrupts
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_PIN), readEncoderA, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_B_PIN), readEncoderB, CHANGE);
  
  // Initialize PID controller
  pidController.SetMode(AUTOMATIC);
  pidController.SetOutputLimits(0, 255);  // PWM limits
  pidController.SetSampleTime(50);       // 50ms sample time
  
  // Stop motor initially
  stopMotor();
  
  Serial.println("CtrlHub PID Control System Ready");
  Serial.println("Commands: SET_PID, SET_SPEED, START_PID_CONTROL, STOP_PID_CONTROL, GET_SPEED, GET_PID_DATA");
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
  currentTime = millis();
  unsigned long deltaTime = currentTime - lastTime;
  
  if (deltaTime >= DATA_INTERVAL) {
    long deltaCount = encoderCount - lastEncoderCount;
    
    // Calculate RPM
    // RPM = (deltaCount / COUNTS_PER_REVOLUTION) * (60000 / deltaTime)
    currentSpeed = (float)deltaCount * 60000.0 / (COUNTS_PER_REVOLUTION * deltaTime);
    
    lastEncoderCount = encoderCount;
    lastTime = currentTime;
  }
  
  return currentSpeed;
}

// ======================================================
// PID CONTROL FUNCTIONS
// ======================================================
void updatePIDController() {
  if (!pidControlActive) return;
  
  // Update current speed
  pidInput = calculateRPM();
  
  // Compute PID
  pidController.Compute();
  
  // Apply output to motor
  runMotor((int)pidOutput);
}

void setPIDParameters(double kp, double ki, double kd) {
  pidKp = kp;
  pidKi = ki;
  pidKd = kd;
  pidController.SetTunings(pidKp, pidKi, pidKd);
  
  Serial.print("PID_SET_OK Kp:");
  Serial.print(pidKp);
  Serial.print(" Ki:");
  Serial.print(pidKi);
  Serial.print(" Kd:");
  Serial.println(pidKd);
}

void setTargetSpeed(double speed) {
  pidSetpoint = speed;
  Serial.print("SPEED_SET_OK Target:");
  Serial.println(pidSetpoint);
}

void startPIDControl() {
  pidControlActive = true;
  encoderCount = 0;
  lastEncoderCount = 0;
  lastTime = millis();
  
  Serial.println("PID_CONTROL_STARTED");
}

void stopPIDControl() {
  pidControlActive = false;
  stopMotor();
  Serial.println("PID_CONTROL_STOPPED");
}

// ======================================================
// COMMAND PROCESSING
// ======================================================
void processCommand(String command) {
  command.trim();
  
  if (command.startsWith("SET_PID")) {
    // Parse: SET_PID 1.0 0.1 0.01
    int firstSpace = command.indexOf(' ');
    int secondSpace = command.indexOf(' ', firstSpace + 1);
    int thirdSpace = command.indexOf(' ', secondSpace + 1);
    
    if (firstSpace > 0 && secondSpace > 0 && thirdSpace > 0) {
      double kp = command.substring(firstSpace + 1, secondSpace).toDouble();
      double ki = command.substring(secondSpace + 1, thirdSpace).toDouble();
      double kd = command.substring(thirdSpace + 1).toDouble();
      setPIDParameters(kp, ki, kd);
    } else {
      Serial.println("ERROR_INVALID_PID_FORMAT");
    }
  }
  else if (command.startsWith("SET_SPEED")) {
    // Parse: SET_SPEED 100.0
    int spaceIndex = command.indexOf(' ');
    if (spaceIndex > 0) {
      double speed = command.substring(spaceIndex + 1).toDouble();
      setTargetSpeed(speed);
    } else {
      Serial.println("ERROR_INVALID_SPEED_FORMAT");
    }
  }
  else if (command == "START_PID_CONTROL") {
    startPIDControl();
  }
  else if (command == "STOP_PID_CONTROL") {
    stopPIDControl();
  }
  else if (command == "GET_SPEED") {
    float speed = calculateRPM();
    Serial.print("SPEED:");
    Serial.println(speed);
  }
  else if (command == "GET_PID_DATA") {
    float speed = calculateRPM();
    double error = pidSetpoint - pidInput;
    Serial.print("SPEED:");
    Serial.print(speed);
    Serial.print(",ERROR:");
    Serial.print(error);
    Serial.print(",OUTPUT:");
    Serial.println(pidOutput);
  }
  
  // Legacy parameter extraction commands
  else if (command == "START_COAST_DOWN") {
    startCoastDownTest();
  }
  else if (command.startsWith("START_STEADY_STATE")) {
    int spaceIndex = command.indexOf(' ');
    if (spaceIndex > 0) {
      int pwmValue = command.substring(spaceIndex + 1).toInt();
      startSteadyStateTest(pwmValue);
    } else {
      startSteadyStateTest(150); // Default
    }
  }
  else if (command.startsWith("START_BACK_EMF")) {
    int spaceIndex = command.indexOf(' ');
    if (spaceIndex > 0) {
      int pwmValue = command.substring(spaceIndex + 1).toInt();
      startBackEMFTest(pwmValue);
    } else {
      startBackEMFTest(200); // Default
    }
  }
  else if (command == "STOP_TEST") {
    stopAllTests();
  }
  else {
    Serial.println("ERROR_UNKNOWN_COMMAND");
  }
}

// ======================================================
// LEGACY TEST IMPLEMENTATIONS
// ======================================================
void startCoastDownTest() {
  currentTest = "coast-down";
  testRunning = true;
  testStartTime = millis();
  encoderCount = 0;
  lastEncoderCount = 0;
  lastTime = millis();
  
  // Spin up motor then let it coast
  runMotor(200);
  delay(2000);  // Spin for 2 seconds
  stopMotor();
  
  Serial.println("COAST_DOWN_STARTED");
}

void startSteadyStateTest(int pwmValue) {
  currentTest = "steady-state";
  testRunning = true;
  testStartTime = millis();
  encoderCount = 0;
  lastEncoderCount = 0;
  lastTime = millis();
  
  runMotor(pwmValue);
  Serial.print("STEADY_STATE_STARTED PWM:");
  Serial.println(pwmValue);
}

void startBackEMFTest(int pwmValue) {
  currentTest = "back-emf";
  testRunning = true;
  testStartTime = millis();
  encoderCount = 0;
  lastEncoderCount = 0;
  lastTime = millis();
  
  runMotor(pwmValue);
  Serial.print("BACK_EMF_STARTED PWM:");
  Serial.println(pwmValue);
}

void stopAllTests() {
  testRunning = false;
  currentTest = "";
  stopMotor();
  Serial.println("ALL_TESTS_STOPPED");
}

// ======================================================
// MAIN LOOP
// ======================================================
void loop() {
  // Handle serial commands
  if (Serial.available()) {
    String command = Serial.readString();
    processCommand(command);
  }
  
  // Update PID controller if active
  if (pidControlActive) {
    updatePIDController();
  }
  
  // Handle legacy test data output
  if (testRunning && (millis() - lastTime >= DATA_INTERVAL)) {
    float rpm = calculateRPM();
    unsigned long elapsed = millis() - testStartTime;
    
    Serial.print("DATA,");
    Serial.print(elapsed);
    Serial.print(",");
    Serial.print(rpm);
    Serial.print(",");
    Serial.print(encoderCount);
    Serial.print(",");
    Serial.println(currentTest);
    
    // Auto-stop tests after reasonable duration
    if (elapsed > 30000) { // 30 seconds
      stopAllTests();
    }
  }
  
  delay(10); // Small delay for stability
}