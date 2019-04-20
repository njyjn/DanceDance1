#include <Arduino_FreeRTOS.h>
#include <queue.h>
#include <semphr.h>
#include "Wire.h"

/*
 * Hardware Pins
 */
#define MPU_1 51
#define MPU_2 52
#define MPU_3 53

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
#define DELAY_SENSOR_READ 60
#define DELAY_POWER_READ 1000
#define DELAY_SEND2RPI 10
#define RESEND_THRESHOLD 0

/*
 *  JZON 1.1 CONSTANTS (DO NOT CUSTOMIZE)
 */
#define MESSAGE_START 55
#define MESSAGE_SIZE_NO_DATA 3
#define MESSAGE_SIZE_POWER 10
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

int reset_cumpower;

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
  unsigned long uJ;
};

struct TJZONPacket {
  char start;
  char packetCode;
  char len;
  struct TPowerData powerData;
  struct TSensorData sensorData[NUM_SENSORS];
};

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  initI2C();
  for (int i = 0; i <= 50; i++){
    if (i < 18 || i > 21) {
      pinMode(i, INPUT_PULLUP);
    }
  }
  dataQueue = xQueueCreate(80, sizeof( struct TSensorData[3] ));
  if(dataQueue == NULL){
  }
  powerQueue = xQueueCreate(20, sizeof( struct TPowerData ));
  if(powerQueue == NULL){
  }
  dataSemaphore = xSemaphoreCreateBinary();
  powerSemaphore = xSemaphoreCreateBinary();
  if(dataSemaphore == NULL || powerSemaphore == NULL){
  }
  xSemaphoreGive(dataSemaphore);
  xSemaphoreGive(powerSemaphore);
  initialHandshake();
  xTaskCreate(
    SendToRpi,
    "SendToRpi",
    1024, // Stack size
    NULL,
    2, // priority
    NULL
  );
  xTaskCreate(
    SensorRead,
    "SensorRead",
    1024, // Stack size
    NULL,
    1, // priority
    NULL
  );
  xTaskCreate(
    PowerRead,
    "PowerRead",
    1024, // Stack size
    NULL,
    3, // priority
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
      if (xQueueReceive(dataQueue, &sensorData, 3)) {
        for (int i=0;i<NUM_SENSORS;i++) {
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
    msg.powerData = powerData;
    serialize(bufferPacket, &msg, sizeof(msg));
    while (acknowledged == 0 && resend_count <= RESEND_THRESHOLD) {
      sendSerialData(bufferPacket, sizeof(bufferPacket));
      if (Serial1.available()) {
        Serial1.readBytes(bufferAck, MESSAGE_SIZE_NO_DATA);
        if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
          acknowledged = 1;
        } else if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_NACK) {
        } else if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_RESET) {
          reset_cumpower = 1;
          acknowledged = 1;
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
    if (xSemaphoreTake(dataSemaphore, 3)) {
      xQueueSend(dataQueue, &sensorData, 3);
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
    digitalWrite(MPU_2, HIGH);
    digitalWrite(MPU_3, HIGH);
    vTaskDelay(1);
    digitalWrite(MPU_1, LOW);
  }
  if (sensorId == 2) {
    digitalWrite(MPU_1,HIGH);
    digitalWrite(MPU_3,HIGH);
    vTaskDelay(1);
    digitalWrite(MPU_2,LOW);
  }
  if (sensorId == 3) {
    digitalWrite(MPU_1,HIGH);
    digitalWrite(MPU_2,HIGH);
    vTaskDelay(1);
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
  }
  aX = ((aX / accel2G) * 1000);
  aY = ((aY / accel2G) * 1000);
  aZ = ((aZ / accel2G) * 1000);
  gX = ((gX / gyroS) * 1000);
  gY = ((gY / gyroS) * 1000);
  gZ = ((gZ / gyroS) * 1000);
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
    if (reset_cumpower == 1) {
      cumpower = 0;
      reset_cumpower = 0;
    }
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
    cumpower += power * (currentTime - last_elapsed)/(1000.0 * 3600.0);
    last_elapsed = currentTime;
    // Assemble power data packet (Multipled by 1k for decimal-short conversion)
    powerData.mV = (unsigned short)(voltage*1000);
    powerData.mA = (unsigned short)(current*1000);
    powerData.mW = (unsigned short)(power*1000);
    powerData.uJ = (unsigned long)(cumpower*1000000);
    // Get power readings from queue
    if (xSemaphoreTake(powerSemaphore, 3)) {
      xQueueSend(powerQueue, &powerData, 3);
      xSemaphoreGive(powerSemaphore);
    }
    vTaskDelayUntil(&xLastWakeTime,DELAY_POWER_READ/portTICK_PERIOD_MS);
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
    // Get ACK from RPi
    Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
    if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
      // Send ACK to RPi
      msg = generateHandshakeMessage(PACKET_CODE_ACK);
      memcpy(bufferSend, &msg, sizeof(msg));
      sendSerialData(bufferSend, sizeof(bufferSend));
      // Get HELLO from RPi
      Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
      if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_HELLO) {
        // Send Ack to RPi
        msg = generateHandshakeMessage(PACKET_CODE_ACK);
        memcpy(bufferSend, &msg, sizeof(msg));
        sendSerialData(bufferSend, sizeof(bufferSend));
        // Get Ack from RPi
        Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
        if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
          // Success!
          return;
        }
      }
    }
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
  Wire.beginTransmission(MPU_ADDR);  // Begin a transmission to the I2C slave device with the given address
  Wire.write(0x6B);   // PWR_MGMT_1 register
  Wire.write(0);      // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);  // Sends a stop message after transmission, releasing the I2C bus.
}

void initI2C() {
  delay(100);
  int i = 0;
  pinMode(MPU_1, OUTPUT);
  pinMode(MPU_2, OUTPUT);
  pinMode(MPU_3, OUTPUT);
  digitalWrite(MPU_1, LOW);
  digitalWrite(MPU_2, HIGH);
  digitalWrite(MPU_3, HIGH);
  writeToWire();
  digitalWrite(MPU_1, HIGH);
  digitalWrite(MPU_2, LOW);
  digitalWrite(MPU_3, HIGH);
  writeToWire();
  digitalWrite(MPU_1, HIGH);
  digitalWrite(MPU_2, HIGH);
  digitalWrite(MPU_3, LOW);
  writeToWire();
}

void loop() {
}