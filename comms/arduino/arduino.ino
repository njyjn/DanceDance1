#include <Arduino_FreeRTOS.h>
#include <queue.h>
#include <semphr.h>
#include "Wire.h"

/*
 * Hardware Pins
 */
#define MPU_1 22
#define MPU_2 38
#define MPU_3 52

/*
 * Hardware Constants
 */
#define CURRENT_PIN A0    // Input Pin for measuring Current
#define VOLTAGE_PIN A1   // Input Pin for measuring Voltage
#define RS 0.1          // Shunt resistor value (in ohms)
#define VOLTAGE_REF 5
#define accel2G 16384.0
#define gyroS 131.0

/*
 * Program Variables
 */
#define NUM_SENSORS 3
#define MPU_ADDR 0x68 // I2C address of the MPU-6050
#define NUM_TASKS 1
#define DELAY_INIT_HANDSHAKE 100
#define DELAY_SENSOR_READ 8
#define DELAY_POWER_READ 1000
#define DELAY_SEND2RPI 10
#define RESEND_THRESHOLD 0
//MPU6050 mpu_sensor(MPU_ADDR);

/*
 *  JZON 1.1 CONSTANTS (DO NOT CUSTOMIZE)
 */
#define MESSAGE_START 55
#define MESSAGE_SIZE_NO_DATA 3
#define MESSAGE_SIZE_POWER 8
#define MESSAGE_SIZE_DATA NUM_SENSORS*12+NUM_SENSORS+MESSAGE_SIZE_POWER
#define MESSAGE_SIZE_FULL MESSAGE_SIZE_NO_DATA+MESSAGE_SIZE_DATA+1
#define MESSAGE_PACKET_CODE_INDEX_NO_DATA 1
#define PACKET_CODE_NACK 0
#define PACKET_CODE_ACK 1
#define PACKET_CODE_HELLO 2
#define PACKET_CODE_READ 3
#define PACKET_CODE_WRITE 4
#define PACKET_CODE_DATA_RESPONSE 5
#define PACKET_CODE_RESET 6

QueueHandle_t dataQueue;
SemaphoreHandle_t dataSemaphore;
QueueHandle_t powerQueue;
SemaphoreHandle_t powerSemaphore;

struct TSensorData {
  char sensorId;
  short aX;
  short aY;
  short aZ;
  short gX;
  short gY;
  short gZ;
};

struct TPowerData {
  unsigned short mV;
  unsigned short mA;
  unsigned short mW;
  unsigned short uJ;
};

struct TJZONPacket {
  char start;
  char packetCode;
  char len;
  struct TPowerData powerData;
  struct TSensorData sensorData[NUM_SENSORS];
};

void setup() {
  // Serial: Debugging console
  Serial.begin(115200);
  // Serial1: TX/RX to RPi
  Serial1.begin(115200);

  Serial.println("Setting up I2C...");
  initI2C();

  dataQueue = xQueueCreate(60, sizeof( struct TSensorData[3] ));
  if(dataQueue == NULL){
    Serial.write("Error creating the data queue!\n");
  }

  powerQueue = xQueueCreate(10, sizeof( struct TPowerData ));
  if(powerQueue == NULL){
    Serial.write("Error creating the power queue!\n");
  }

  dataSemaphore = xSemaphoreCreateBinary();
  powerSemaphore = xSemaphoreCreateBinary();
  if(dataSemaphore == NULL || powerSemaphore == NULL){
    Serial.write("Error creating the semaphores!\n");
  }
  xSemaphoreGive(dataSemaphore);
  xSemaphoreGive(powerSemaphore);

  Serial.println("Initiating handshake with RPi...");
  initialHandshake();

  xTaskCreate(
    SendToRpi,
    "SendToRpi",
    1024, // Stack size
    NULL,
    3, // priority
    NULL
  );

  xTaskCreate(
    SensorRead,
    "SensorRead",
    1024, // Stack size
    NULL,
    2, // priority
    NULL
  );

  xTaskCreate(
    PowerRead,
    "PowerRead",
    1024, // Stack size
    NULL,
    2, // priority
    NULL
  );
}

void SendToRpi(void *pvParameters)
{
  TickType_t xLastWakeTime = xTaskGetTickCount();
  struct TSensorData sensorData[3];
  struct TPowerData powerData;
  struct TJZONPacket msg;
  for (;;) {
    char bufferPacket[MESSAGE_SIZE_FULL];
    char bufferAck[MESSAGE_SIZE_NO_DATA];
    int acknowledged = 0;
    int resend_count = 0;

    // Create data packet
    msg.start = MESSAGE_START;
    msg.packetCode = PACKET_CODE_DATA_RESPONSE;
    msg.len = NUM_SENSORS;

    // Get sensor readings from queue
    if (xSemaphoreTake(dataSemaphore, 3)) {
//      Serial.print("TSem");
      if (xQueueReceive(dataQueue, &sensorData, 3)) {
//        Serial.print("Received from data queue!");
        for (int i=0;i<NUM_SENSORS;i++) {
          Serial.print("Sensor "); Serial.print(i); Serial.print(": ");
          Serial.print(sensorData[i].aX); Serial.print(",");
          Serial.print(sensorData[i].aY); Serial.print(",");
          Serial.print(sensorData[i].aZ); Serial.print(",");
          Serial.print(sensorData[i].gX); Serial.print(",");
          Serial.print(sensorData[i].gY); Serial.print(",");
          Serial.print(sensorData[i].gZ); Serial.print("\n");
          msg.sensorData[i] = sensorData[i];
        }
      }
      xSemaphoreGive(dataSemaphore);
    }

    // Get power readings from queue
    if (xSemaphoreTake(powerSemaphore, 3)) {
      if (xQueueReceive(powerQueue, &powerData, 3)) {
      }
      xSemaphoreGive(powerSemaphore);
    }
//    Serial.print("Power: ");
//    Serial.print(powerData.mV); Serial.print(",");
//    Serial.print(powerData.mA); Serial.print(",");
//    Serial.print(powerData.mW); Serial.print(",");
//    Serial.print(powerData.uJ); Serial.print("\n");
    msg.powerData = powerData;

    serialize(bufferPacket, &msg, sizeof(msg));
    while (acknowledged == 0 && resend_count <= RESEND_THRESHOLD) {
      sendSerialData(bufferPacket, sizeof(bufferPacket));
      Serial.println("Data sent... ");
      if (Serial1.available()) {
        Serial1.readBytes(bufferAck, MESSAGE_SIZE_NO_DATA);
        if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
          Serial.println("Acknowledged!");
          acknowledged = 1;
        } else if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_NACK) {
          Serial.println("Resend!");
        } else if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_RESET) {
//          initI2C(1);
          Serial.println("Reset I2C!");
          return;
        }
      }
      resend_count++;
    }
    vTaskDelayUntil(&xLastWakeTime,DELAY_SEND2RPI/portTICK_PERIOD_MS);
  }
}

void SensorRead(void *pvParameters)
{
  TickType_t xLastWakeTime = xTaskGetTickCount();
  struct TSensorData sensorDatum;
  struct TSensorData sensorData[NUM_SENSORS];

  for (;;) {
    for (int i=0;i<NUM_SENSORS;i++) {
      getSensorData(&sensorDatum,i+1);
      sensorData[i] = sensorDatum;
    }
//    Serial.println("Sensors sampled!");
    if (xSemaphoreTake(dataSemaphore, 3)) {
//      Serial.println("Data semaphore obtained!");
      xQueueSend(dataQueue, &sensorData, 3);
//      Serial.println("Sent to data queue!");
      xSemaphoreGive(dataSemaphore);
    }
    vTaskDelayUntil(&xLastWakeTime,DELAY_SENSOR_READ/portTICK_PERIOD_MS);
  }
}

void getSensorData(TSensorData * packet, char sensorId) {
  int16_t aX = 10*sensorId;
  int16_t aY = 20*sensorId;
  int16_t aZ = 30*sensorId;
  int16_t gX = 4*sensorId;
  int16_t gY = 5*sensorId;
  int16_t gZ = 6*sensorId;
  packet->sensorId = sensorId;
  if (sensorId == 1) {
    digitalWrite(MPU_1, LOW);
    digitalWrite(MPU_2, HIGH);
    digitalWrite(MPU_3, HIGH);
  }
  if (sensorId == 2) {
    digitalWrite(MPU_1,HIGH);
    digitalWrite(MPU_2,LOW);
    digitalWrite(MPU_3,HIGH);
  }
  if (sensorId == 3) {
    digitalWrite(MPU_1,HIGH);
    digitalWrite(MPU_2,HIGH);
    digitalWrite(MPU_3,LOW);
  }

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  if (Wire.endTransmission(false) == 0) {
    if (Wire.requestFrom(MPU_ADDR,14,true) == 14) {  // request a total of 14 registers
      aX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
      aY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
      aZ=Wire.read()<<8|Wire.read();  // 0x3F (AC  m CEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
      Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
      gX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
      gY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
      gZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
    }
//    Serial.println("Wire read complete ");
  }

  aX = ((aX / accel2G) * 1000);
  aY = ((aY / accel2G) * 1000);
  aZ = ((aZ / accel2G) * 1000);
  gX = ((gX / gyroS) * 1000);
  gY = ((gY / gyroS) * 1000);
  gZ = ((gZ / gyroS) * 1000);

//  Serial.print(aX);  Serial.print(", ");
//  Serial.print(aY);  Serial.print(", ");
//  Serial.print(aZ);  Serial.print(", ");
//  Serial.print(gX);  Serial.print(", ");
//  Serial.print(gY);  Serial.print(", ");
//  Serial.print(gZ);  Serial.print("]");
//  if (sensorId != 3) Serial.print(",");

  packet->aX = aX;
  packet->aY = aY;
  packet->aZ = aZ;
  packet->gX = gX;
  packet->gY = gY;
  packet->gZ = gZ;
}

void PowerRead(void *pvParameters)
{
  struct TPowerData powerData;
  TickType_t xLastWakeTime = xTaskGetTickCount();
  float currentValue;   // Variable to store value from analog read
  float voltageValue;
  float current;       // Calculated current value
  float voltage;
  float power;
  float cumpower;
  unsigned long currentTime;
  unsigned long last_elapsed = 0;

  for (;;) {
    currentTime = millis();
    // Read current & voltage values from circuit board
    currentValue = analogRead(CURRENT_PIN);
    voltageValue = analogRead(VOLTAGE_PIN);
    // Remap the ADC value into a voltage number (5V reference)
    currentValue = (currentValue * VOLTAGE_REF) / 1023.0;
    voltageValue = (voltageValue * VOLTAGE_REF) / 1023.0;

    // Follow the equation given by the INA169 datasheet to
    // determine the current flowing through RS. Assume RL = 10k
    // Is = (Vout x 1k) / (RS x RL)
    current = currentValue / (10 * RS);
    voltage = voltageValue * 2;
    power = current * voltage;
    cumpower += power * (currentTime - last_elapsed);
    last_elapsed = currentTime;

    // Assemble power data packet (Multipled by 1k for decimal-short conversion)
    powerData.mV = (short)(voltage*1000);
    powerData.mA = (short)(current*1000);
    powerData.mW = (short)(power*1000);
    powerData.uJ = (short)(cumpower*1000);
    // Get power readings from queue
    if (xSemaphoreTake(powerSemaphore, 3)) {
      xQueueSend(powerQueue, &powerData, 3);
      xSemaphoreGive(powerSemaphore);
    }
    vTaskDelay(DELAY_SENSOR_READ);
  }
}

void initialHandshake() {
  int handshake_status = 0;
  struct TJZONPacket msg;
  for (;;) {
    char bufferSend[sizeof(msg)];
    char bufferReceive[sizeof(msg)];
    // Send HELLO to RPi
    msg = generateHandshakeMessage(PACKET_CODE_HELLO);
    memcpy(bufferSend, &msg, sizeof(msg));
    sendSerialData(bufferSend, sizeof(bufferSend));
    //Serial.println("Sent HELLO to RPi");
    // Get ACK from RPi
    Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
    if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
      //Serial.println("Got HELLO ACK from RPi");
      // Send ACK to RPi
      msg = generateHandshakeMessage(PACKET_CODE_ACK);
      memcpy(bufferSend, &msg, sizeof(msg));
      sendSerialData(bufferSend, sizeof(bufferSend));
      //Serial.println("Sent first ACK to RPi");
      // Get HELLO from RPi
      Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
      if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_HELLO) {
        //Serial.println("Got HELLO from RPi");
        // Send Ack to RPi
        msg = generateHandshakeMessage(PACKET_CODE_ACK);
        memcpy(bufferSend, &msg, sizeof(msg));
        sendSerialData(bufferSend, sizeof(bufferSend));
        //Serial.println("Sent HELLO ACK to RPi");
        // Get Ack from RPi
        Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
        if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
          // Success!
          //Serial.println("Got last ACK from RPi");
          return;
        }
      }
    }
    //Serial.println("Handshake failed. Retrying...");
    delay(DELAY_INIT_HANDSHAKE);
  }
}

struct TJZONPacket generateHandshakeMessage(int packetCode) {
    struct TJZONPacket msg;
    msg.start = MESSAGE_START;
    msg.packetCode = packetCode;
    msg.len = 0;
    return msg;
}

void serialize(char *buf, void *p, size_t size) {
  char checksum = 0;
  memcpy(buf, p, size);
  for(int i=MESSAGE_SIZE_NO_DATA; i<size; i++) {
    checksum ^= buf[i];
  }
  buf[size] = checksum;
}

void sendSerialData(char *buffer, int len) {
  Serial1.write(buffer, len);
}

void writeToWire() {
  Wire.begin();
  Serial.print('a');
  Wire.beginTransmission(MPU_ADDR);  // Begin a transmission to the I2C slave device with the given address
  Serial.print('b');
  Wire.write(0x6B);   // PWR_MGMT_1 register
  Serial.print('c');
  Wire.write(0);      // set to zero (wakes up the MPU-6050)
  Serial.print('d');
  Serial.print(Wire.endTransmission(true));  // Sends a stop message after transmission, releasing the I2C bus.
  Serial.print('e');
}

void initI2C() {
  delay(100);
  int i = 0;
  Serial.print(i++);
  pinMode(MPU_1, OUTPUT);
  Serial.print(i++);
  pinMode(MPU_2, OUTPUT);
  Serial.print(i++);
  pinMode(MPU_3, OUTPUT);
  Serial.print(i++);

  digitalWrite(MPU_1, LOW);
  Serial.print(i++);
  digitalWrite(MPU_2, HIGH);
  Serial.print(i++);
  digitalWrite(MPU_3, HIGH);
  Serial.print(i++);
  writeToWire();
  Serial.print(i++);
  digitalWrite(MPU_1, HIGH);
  Serial.print(i++);
  digitalWrite(MPU_2, LOW);
  Serial.print(i++);
  digitalWrite(MPU_3, HIGH);
  Serial.print(i++);
  writeToWire();
  Serial.print(i++);
  digitalWrite(MPU_1, HIGH);
  Serial.print(i++);
  digitalWrite(MPU_2, HIGH);
  Serial.print(i++);
  digitalWrite(MPU_3, LOW);
  Serial.print(i++);
  writeToWire();
  Serial.print(i++);
}

void loop() {
}
