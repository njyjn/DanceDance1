#include <Arduino_FreeRTOS.h>
#include <queue.h>
#include <semphr.h>
#include <I2Cdev.h>
#include "Wire.h"
#include "MPU6050.h"

/*
 * Hardware Pins
 */
#define MPU_1 48
#define MPU_2 50
#define MPU_3 52

/*
 * Program Variables
 */
#define NUM_SENSORS 3
#define MPU_ADDR 0x68 // I2C address of the MPU-6050
#define NUM_TASKS 2
#define DELAY_INIT_HANDSHAKE 100
#define DELAY_SENSOR_READ 10
#define DELAY_SEND2RPI 10
#define RESEND_THRESHOLD 10
MPU6050 mpu_sensor(MPU_ADDR);

/*
 *  JZON 1.1 CONSTANTS (DO NOT CUSTOMIZE)
 */
#define MESSAGE_START 55
#define MESSAGE_SIZE_NO_DATA 3
#define MESSAGE_SIZE_DATA NUM_SENSORS*12+NUM_SENSORS+4
#define MESSAGE_SIZE_FULL MESSAGE_SIZE_NO_DATA+MESSAGE_SIZE_DATA+1
#define MESSAGE_PACKET_CODE_INDEX_NO_DATA 1
#define PACKET_CODE_NACK 0
#define PACKET_CODE_ACK 1
#define PACKET_CODE_HELLO 2
#define PACKET_CODE_READ 3
#define PACKET_CODE_WRITE 4
#define PACKET_CODE_DATA_RESPONSE 5

QueueHandle_t dataQueue;
QueueHandle_t powerQueue;
SemaphoreHandle_t barrierSemaphore;

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
  unsigned int mV;
  unsigned int mA;
};

struct TJZONPacket {
  char start;
  char packetCode;
  char len;
  struct TPowerData powerData;
  struct TSensorData sensorData[NUM_SENSORS];
};

void setup() {

  pinMode(MPU_1, OUTPUT);
  pinMode(MPU_2, OUTPUT);
  pinMode(MPU_3, OUTPUT);

  // Serial: Debugging console
  Serial.begin(115200);
  // Serial1: TX/RX to RPi
  Serial1.begin(115200);

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

  Serial.println("Initiating handshake with RPi...");
  initialHandshake();

  dataQueue = xQueueCreate(NUM_SENSORS, sizeof( struct TSensorData ));
  if(dataQueue == NULL){
    Serial.write("Error creating the data queue!\n");
  }

  powerQueue = xQueueCreate(1, sizeof( struct TPowerData ));
  if(powerQueue == NULL){
    Serial.write("Error creating the power queue!\n");
  }

  barrierSemaphore = xSemaphoreCreateCounting(NUM_TASKS, NUM_TASKS);
  if(barrierSemaphore == NULL){
    Serial.write("Error creating the semaphore!\n");
  }

  // Now set up four tasks to run independently.
  xTaskCreate(
    Send2Rpi,
    "Send2Rpi",
    256, // Stack size
    NULL,
    2, // priority
    NULL
  );

  xTaskCreate(
    SensorRead,
    "SensorRead",
    256, // stack size
    NULL,
    1, // priority
    NULL
  );

  xTaskCreate(
    PowerRead,
    "PowerRead",
    256, // stack size
    NULL,
    1, // priority
    NULL
  );

  // xTaskCreate(
  //   SensorRead,
  //   "SensorRead3",
  //   256, // stack size
  //   (void *) 3,
  //   1, // priority
  //   NULL
  // );

  Serial.println("Setup complete!");
}

void Send2Rpi(void *pvParameters)
{
  (void) pvParameters;
  const TickType_t xFrequency = DELAY_SEND2RPI;
  TickType_t xLastWakeTime;
  xLastWakeTime = xTaskGetTickCount();
  struct TSensorData sensorData;
  struct TPowerData powerData;
  for (;;) {
    struct TJZONPacket msg;
    char bufferPacket[MESSAGE_SIZE_FULL];
    char bufferAck[MESSAGE_SIZE_NO_DATA];
    int acknowledged = 0;
    int resend_count = 0;
    // Run only if all sensors are ready with data
    if (uxSemaphoreGetCount(barrierSemaphore) == 0) {
      // Create data packet
      msg.start = MESSAGE_START;
      msg.packetCode = PACKET_CODE_DATA_RESPONSE;
      msg.len = NUM_SENSORS;
      xQueueReceive(powerQueue, &powerData, portMAX_DELAY);
      msg.powerData = powerData;
      for (int i=0;i<NUM_SENSORS;i++) {
        xQueueReceive(dataQueue, &sensorData, portMAX_DELAY);
        msg.sensorData[i] = sensorData;
      }
      serialize(bufferPacket, &msg, sizeof(msg));
      while (acknowledged == 0 && resend_count <= RESEND_THRESHOLD) {
        sendSerialData(bufferPacket, sizeof(bufferPacket));
        Serial.print("Data sent... ");
        if (Serial1.available()) {
          Serial1.readBytes(bufferAck, MESSAGE_SIZE_NO_DATA);
          if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
            Serial.println("Acknowledged!");
            acknowledged = 1;
          } else if (bufferAck[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_NACK) {
            Serial.println("Resend!");
          }
        }
        resend_count++;
      }
      // Release the semaphores
      for (int i=0;i<NUM_TASKS;i++) {
        xSemaphoreGive(barrierSemaphore);
      }
    }
    vTaskDelayUntil(&xLastWakeTime, xFrequency);
  }
}

void SensorRead(void *pvParameters)
{
  struct TSensorData sensorData;
  // int sensorId = (uint32_t) pvParameters;
  for (;;)
  {
    // Reserve the semaphore
    xSemaphoreTake(barrierSemaphore, portMAX_DELAY);
    // Read the inputs
    for (int i=0; i<NUM_SENSORS; i++) {
      int sensorId = i+1;
      if (sensorId == 1) {
        digitalWrite(MPU_1, LOW);
        digitalWrite(MPU_2, HIGH);
        digitalWrite(MPU_3, HIGH);
      } else if (sensorId == 2) {
        digitalWrite(MPU_1,HIGH);
        digitalWrite(MPU_2,LOW);
        digitalWrite(MPU_3, HIGH);
      } else if (sensorId == 3) {
        digitalWrite(MPU_1,HIGH);
        digitalWrite(MPU_2,HIGH);
        digitalWrite(MPU_3, LOW);
      }
      // Assemble sensor data packet
      sensorData.sensorId = sensorId;
      mpu_sensor.getAcceleration((int16_t*)&sensorData.aX, (int16_t*)&sensorData.aY, (int16_t*)&sensorData.aZ);
      mpu_sensor.getRotation((int16_t*)&sensorData.gX, (int16_t*)&sensorData.gY, (int16_t*)&sensorData.gZ);
      // Add to inter-task communication queue
      xQueueSend(dataQueue, &sensorData, portMAX_DELAY);
    }
    vTaskDelay(DELAY_SENSOR_READ);
  }
}

void PowerRead(void *pvParameters)
{
  struct TPowerData powerData;
  for (;;)
  {
    // Reserve the semaphore
    xSemaphoreTake(barrierSemaphore, portMAX_DELAY);
    // TODO: @zhiwei power sampling code

    // Assemble power data packet
    powerData.mV = (short)random(0,6000);
    powerData.mA = (short)random(0,3000);
    xQueueSend(powerQueue, &powerData, portMAX_DELAY);
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
    Serial.println("Sent HELLO to RPi");
    // Get ACK from RPi
    Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
    if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
      Serial.println("Got HELLO ACK from RPi");
      // Send ACK to RPi
      msg = generateHandshakeMessage(PACKET_CODE_ACK);
      memcpy(bufferSend, &msg, sizeof(msg));
      sendSerialData(bufferSend, sizeof(bufferSend));
      Serial.println("Sent first ACK to RPi");
      // Get HELLO from RPi
      Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
      if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_HELLO) {
        Serial.println("Got HELLO from RPi");
        // Send Ack to RPi
        msg = generateHandshakeMessage(PACKET_CODE_ACK);
        memcpy(bufferSend, &msg, sizeof(msg));
        sendSerialData(bufferSend, sizeof(bufferSend));
        Serial.println("Sent HELLO ACK to RPi");
        // Get Ack from RPi
        Serial1.readBytes(bufferReceive, MESSAGE_SIZE_NO_DATA);
        if (bufferReceive[MESSAGE_PACKET_CODE_INDEX_NO_DATA] == PACKET_CODE_ACK) {
          // Success!
          Serial.println("Got last ACK from RPi");
          return;
        }
      }
    }
    Serial.println("Handshake failed. Retrying...");
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

void loop() {
  delay(1000);
}
