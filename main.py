import FrameConsumer
import FrameProducer
import queue

if __name__ == "__main__":
    print("Start!")

    video_file_name = 'Videos/sample.avi'
    queue_frame = queue.Queue(100)

    producer = FrameProducer.FrameProducer(video_file_name, queue_frame)
    producer.start()

    consumer = FrameConsumer.FrameConsumer(queue_frame)
    consumer.start()

    producer.join()
    consumer.join()