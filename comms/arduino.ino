#include <Arduino_FreeRTOS.h>
#include <queue.h>
#include <semphr.h>

const int NUM_SENSORS = 2;

QueueHandle_t queue;
SemaphoreHandle_t barrierSemaphore;

struct TSensorData {
  byte sensorId;
  int aX;
  int aY;
  int aZ;
  int gX;
  int gY;
  int gZ;
};

struct TJZONPacket {
  byte head;
  byte packetCode;
  TSensorData sensorData[NUM_SENSORS];
  byte tail;
};

void setup() {
  // initialize both serial ports
  // Serial: Debugging console
  Serial.begin(9600);
  Serial.flush();
  // Serial1: TX/RX to RPi
  Serial1.begin(9600);
  Serial1.flush();

  queue = xQueueCreate( NUM_SENSORS, sizeof( TSensorData ) );
  if(queue == NULL){
    Serial.println("Error creating the queue");
  }

  barrierSemaphore = xSemaphoreCreateCounting( NUM_SENSORS, 0 );
  if(barrierSemaphore == NULL){
    Serial.println("Error creating the semaphore");
  }

  // Now set up four tasks to run independently.
  xTaskCreate(
    Send2Rpi,
    "Send2Rpi",
    256, // Stack size
    NULL,
    4, // priority
    NULL
  );

  xTaskCreate(
    SensorRead,
    "SensorRead1",
    256, // stack size
    (void *) 1,
    3, // priority
    NULL
  );

  xTaskCreate(
    SensorRead,
    "SensorRead2",
    256, // stack size
    (void *) 2,
    2, // priority
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

  // TODO: Initial handshaking protocol
  // Arduino is ready at this point, and initiates a handshake
}

void Send2Rpi(void *pvParameters)  // This is a task.
{
  (void) pvParameters;

  for (;;) {
    // Run only if all sensors are ready with data
    if (uxSemaphoreGetCount(barrierSemaphore) == 0) {
      TJZONPacket msg;
      byte buffer[42];
      msg.head = 55;
      msg.packetCode = 5; // CODE: Data response
      msg.tail = 57;
      for (int i=0;i<NUM_SENSORS;i++) {
        TSensorData sensorData;
        xQueueReceive(queue, &sensorData, portMAX_DELAY);
        msg.sensorData[i] = sensorData;
      }
      unsigned len = serialize(buffer, &msg, sizeof(msg));
      sendSerialData(buffer, len);
      // Release the semaphores
      for (int i=0;i<NUM_SENSORS;i++) {
        xSemaphoreGive(barrierSemaphore);
      }
    }
  }
}

void SensorRead(void *pvParameters)  // This is a task.
{
  (void) pvParameters;

  for (;;)
  {
    // Read the inputs
    // TODO: @jiahao sensor sampling code
    // e.g. int sensorValue = analogRead(A0);

    // Assemble sensor data packet
    // TODO: Replace with actual variables
    TSensorData sensorData;
    sensorData.aX = 0;
    sensorData.aY = 0;
    sensorData.aZ = 0;
    sensorData.gX = 0;
    sensorData.gY = 0;
    sensorData.gZ = 0;
    // Reserve the semaphore
    xSemaphoreTake(barrierSemaphore, portMAX_DELAY);
    // Add to inter-task communication queue
    xQueueSend(queue, &sensorData, portMAX_DELAY);
    vTaskDelay(1);  // one tick delay (15ms) in between reads for stability
  }
}

unsigned int serialize(byte *buf, void *p, size_t size) {
  char checksum = 0;
  buf[0]=size;
  memcpy(buf+1, p, size);
  for(int i=1; i<=size; i++) {
    checksum ^= buf[i];
  }
  buf[size+1]=checksum;
  return size+2;
}

void sendSerialData(byte *buffer, int len) {
  for(int i=0; i<len; i++)
    Serial1.write(buffer[i]);
}

void loop() {
  // if (Serial1.available()) {
  //   int inByte = Serial1.read();
  //   Serial.write(inByte);
  // }
  // if (Serial.available()) {
  //   int inByte = Serial.read();
  //   Serial1.write(inByte);
  // }
}
