import frame_consumer
import frame_producer
import queue

if __name__ == "__main__":
    print("Start!")

    video_file_name = 'Videos/sample.avi'

    consumer = frame_consumer.FrameConsumer()

    producer = frame_producer.FrameProducer(video_file_name, consumer)
    producer.start()

    consumer.start()

    producer.join()
    consumer.join()